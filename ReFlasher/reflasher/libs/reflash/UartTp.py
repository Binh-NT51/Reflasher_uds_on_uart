debugEnable = 0
from os import path, getcwd
from time import sleep

import serial
from threading import Thread
from uds import Config
from uds import ResettableTimer
from uds import fillArray

# types
from libs.reflash.UartTpTypes import UartTpState, UartTpMessageType

# consts
from libs.reflash.UartTpTypes import UART_MAX_PAYLOAD_LENGTH, N_PCI_INDEX, \
    SINGLE_FRAME_DL_INDEX, SINGLE_FRAME_DATA_START_INDEX, \
    FIRST_FRAME_DL_INDEX_HIGH, FIRST_FRAME_DL_INDEX_LOW, FIRST_FRAME_DATA_START_INDEX, \
    CONSECUTIVE_FRAME_SEQUENCE_NUMBER_INDEX, CONSECUTIVE_FRAME_SEQUENCE_DATA_START_INDEX

config_path = path.join(getcwd(), "config.ini")

def printHex(list):
    print('[{}]'.format(', '.join(hex(x) for x in list)))
    pass

class uartTp():

    #__metaclass__ = iTp

    def __init__(self, configPath=None, **kwargs):
        self.__config = None
        self.__loadConfiguration()

        self.__STMin = 0.01
        self.__maxPduLength = 31
        self.__recvBuffer = []
        self.__transmitBuffer = None
        
        print("trying to open a port")
        # configure the serial connections (the parameters differs on the device you are connecting to)
        self.uartconnection = serial.Serial(
            port=str(self.__config["uart"]["port"]),
            baudrate=int(self.__config["uart"]["baudrate"]),
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
        )
        #self.uartconnection.set_buffer_size(tx_size=512)

        if (debugEnable != 0):
            if (self.uartconnection.is_open != True):
                print("UART connection is open successfully on port " + self.uartconnection.port)
            else:
                print("cannot open port " + self.uartconnection.port)
#
        self.receiveThread = Thread(group=None, target=self.receiveFunction, name="Receive Thread")
        self.receiveThreadActive = False

        self.start_connection()

    def start_connection(self):
        self.receiveThreadActive = True
        self.receiveThread.start()
        #print("Start receive messsage")

    def send(self, payload, functionalReq=False):  # TODO: functionalReq not used???
        #self.__connection.send(payload)  # .... implemented in the UART bus impl, so the rest of function replaced by this
        payloadLength = len(payload)

        if payloadLength > UART_MAX_PAYLOAD_LENGTH:
            raise Exception("Payload too large for CAN Transport Protocol")

        if payloadLength < self.__maxPduLength:
            state = UartTpState.SEND_SINGLE_FRAME
        else:
            # we might need a check for functional request as we may not be able to service functional requests for
            # multi frame requests
            state = UartTpState.SEND_FIRST_FRAME
            firstFrameData = payload[0:self.__maxPduLength-1]
            cfBlocks = self.create_blockList(payload[30:])
            sequenceNumber = 1

        txPdu = [0,0]

        endOfMessage_flag = False

        ## this needs fixing to get the timing from the config
        timeoutTimer = ResettableTimer(1)
        stMinTimer = ResettableTimer(self.__STMin)

        self.clearBufferedMessages()

        timeoutTimer.start()
        while endOfMessage_flag is False:

            rxPdu = self.getNextBufferedMessage()

            #if rxPdu is not None:
                #print("Not done hihihi")

            if state ==UartTpState.SEND_SINGLE_FRAME:
                txPdu[N_PCI_INDEX] += (UartTpMessageType.SINGLE_FRAME << 4)
                txPdu[SINGLE_FRAME_DL_INDEX] = payloadLength
                txPdu[SINGLE_FRAME_DATA_START_INDEX:] = fillArray(payload, self.__maxPduLength-1,  fillValue=0x4B)
                self.transmit(txPdu)
                endOfMessage_flag = True
                #printHex(txPdu)
                if (debugEnable == 1):
                    print ("Send single frame")
            elif state == UartTpState.SEND_FIRST_FRAME:
                payloadLength_highNibble = (payloadLength & 0xF00) >> 8
                payloadLength_lowNibble  = (payloadLength & 0x0FF)
                txPdu[N_PCI_INDEX] += (UartTpMessageType.FIRST_FRAME << 4)
                txPdu[FIRST_FRAME_DL_INDEX_HIGH] += payloadLength_highNibble
                txPdu[FIRST_FRAME_DL_INDEX_LOW] += payloadLength_lowNibble
                txPdu[FIRST_FRAME_DATA_START_INDEX:] = firstFrameData
                self.transmit(txPdu)
                if (debugEnable == 0):
                    print ("Send first frame")
                state = UartTpState.SEND_CONSECUTIVE_FRAME
                stMinTimer.start()
                timeoutTimer.restart()
            elif state == UartTpState.SEND_CONSECUTIVE_FRAME:
                if(stMinTimer.isExpired()):  #  and
                      #  (self.__transmitBuffer is None)):
                    txPdu[N_PCI_INDEX] += (UartTpMessageType.CONSECUTIVE_FRAME << 4)
                    txPdu[CONSECUTIVE_FRAME_SEQUENCE_NUMBER_INDEX] += sequenceNumber
                    txPdu[CONSECUTIVE_FRAME_SEQUENCE_DATA_START_INDEX:] = cfBlocks.pop(0)
                    #print(sequenceNumber)
                    self.transmit(txPdu)
                    sequenceNumber = (sequenceNumber + 1) % 16
                    stMinTimer.restart()
                    timeoutTimer.restart()

                    if len(cfBlocks) == 0:
                        endOfMessage_flag = True
            #reinit txpdu
            txPdu = []
            for b in range(0, 32):
                txPdu.append(0)

            #sleep(0.05)
            if (debugEnable == 0):
                if timeoutTimer.isExpired(): 
                    print("Timeout")
                    #raise Exception("Timeout")
    def receiveFunction(self):

        while(self.receiveThreadActive):
            receivemsg = self.uartconnection.read(size=32)   #todo: repace magic number
            if receivemsg is not None:
                dataarray = []
                length = len(receivemsg)
                for i in range(0, length):
                    dataarray.append(receivemsg[i])
                self.callback_onReceive(dataarray)

    def recv(self, timeout_s):
        #return self.__connection.recv(... can pass timeout from here if required ...)  # .... implemented in the UART bus impl, so the rest of function replaced by this
        timeoutTimer = ResettableTimer(timeout_s)

        payload = []
        payloadPtr = 0
        payloadLength = None

        sequenceNumberExpected = 1

        endOfMessage_flag = False

        state = UartTpState.IDLE

        timeoutTimer.start()
        while endOfMessage_flag is False:

            rxPdu = self.getNextBufferedMessage()

            if rxPdu is not None:
                print(rxPdu)
                self.clearBufferedMessages()

                N_PCI = (rxPdu[N_PCI_INDEX] & 0xF0) >> 4
                if state == UartTpState.IDLE:
                    if 1:
                        payloadLength = rxPdu[1]
                        payload = rxPdu[2: 2 + payloadLength]
                        endOfMessage_flag = True
                    elif N_PCI ==UartTpMessageType.FIRST_FRAME:
                        payload = rxPdu[FIRST_FRAME_DATA_START_INDEX:]
                        payloadLength = ((rxPdu[FIRST_FRAME_DL_INDEX_HIGH] & 0x0F) << 8) + rxPdu[
                            FIRST_FRAME_DL_INDEX_LOW]
                        payloadPtr = self.__maxPduLength - 1
                        state = UartTpState.RECEIVING_CONSECUTIVE_FRAME
                        timeoutTimer.restart()
                elif state == UartTpState.RECEIVING_CONSECUTIVE_FRAME:
                    if N_PCI == UartTpMessageType.CONSECUTIVE_FRAME:
                        sequenceNumber = rxPdu[CONSECUTIVE_FRAME_SEQUENCE_NUMBER_INDEX] & 0x0F
                        if sequenceNumber != sequenceNumberExpected:
                            raise Exception("Consecutive frame sequence out of order")
                        else:
                            sequenceNumberExpected = (sequenceNumberExpected + 1) % 16
                        payload += rxPdu[CONSECUTIVE_FRAME_SEQUENCE_DATA_START_INDEX:]
                        payloadPtr += (self.__maxPduLength)
                        timeoutTimer.restart()
                    else:
                        raise Exception("Unexpected PDU received")
            if payloadLength is not None:
                if payloadPtr >= payloadLength:
                    endOfMessage_flag = True

            if timeoutTimer.isExpired():
                if (debugEnable == 0):
                    self.receiveThreadActive = False
                    self.closeConnection()
                    raise Exception("Timeout in waiting for message")
                else:
                    return [0x0, 0x0]
        return list(payload[:payloadLength])

    ##
    # dummy function for the time being
    def closeConnection(self):
        #self.__connection.disconnect()  # .... implemented in the UART bus impl, so the rest of function replaced by this
        self.receiveThreadActive = False
        self.uartconnection.close()
        print("Close connection")

    def callback_onReceive(self, msg):
        data = msg
        self.__recvBuffer = data
    ##
    # @brief clear out the receive list
    def clearBufferedMessages(self):
        self.__recvBuffer = []
        self.__transmitBuffer = None

    ##
    # @brief retrieves the next message from the received message buffers
    # @return list, or None if nothing is on the receive list
    def getNextBufferedMessage(self):
        length = len(self.__recvBuffer)
        if(length != 0):
            return self.__recvBuffer
        else:
            return None

    ##
    # @brief creates the blocklist from the blocksize and payload
    def create_blockList(self, payload):
        blockList = []
        currBlock = []

        payloadLength = len(payload)
        counter = 0

        for i in range(0, payloadLength):

            currBlock.append(payload[i])
            counter += 1

            if counter == self.__maxPduLength:
                blockList.append(currBlock)
                counter = 0
                currBlock = []

        if len(currBlock) != 0:
            blockList.append(fillArray(currBlock, self.__maxPduLength, fillValue = 0x4b))

        return blockList

    # This function is effectively moved down to the UART bus impl (i.e. only called from within send() which is moving down
    def transmit(self, payload):
        txPdu = payload
        if (debugEnable == 0):
            #print("Write data")
            hexTxPdu = []
            for x in range(len(txPdu)):
                hexTxPdu.append(hex(txPdu[x]))
        #printHex(txPdu)
        self.uartconnection.write(txPdu)
        self.__transmitBuffer = txPdu
        
    def __loadConfiguration(self, **kwargs):
        # load the base config
        baseConfig = config_path
        self.__config = Config()
        if path.exists(baseConfig):
            self.__config.read(baseConfig)
        else:
            raise FileNotFoundError("No base config file")

