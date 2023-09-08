from libs.reflash.IHexFunctions import ihexFile
from struct import pack, unpack
import hashlib
from time import sleep, time
from libs.reflash.SimpleUDS import Uds
from libs.reflash import DecodeFunctions
from libs.reflash.logger import logger
from libs.reflash.crc32lib import CRC32
from os import path, getcwd
from configparser import ConfigParser

##############################################################################
####                            local variable                            ####
##############################################################################
EraseRoutineSID = [0x76, 0xF1]
RoutineMemID = [0x44]
ChecksumRoutineSID = [0x76, 0xF2]
SwitchBankRoutineSID = [0x76, 0xFE]
config_path = path.join(getcwd(), "config.ini")

log = logger()

class DownloadSequence():
    def __init__(self):
        pass

    def LoadBinary(self, callback = None):
        #load the configuration
        self.__config = None
        self.__loadConfiguration()
        self.HexFilePath = str(self.__config['flash']['hexfile'])
        self.app = ihexFile(self.HexFilePath)
        addr = (self.app.transmitAddress[0] << 24) + (self.app.transmitAddress[1] << 16) + (self.app.transmitAddress[2] << 8) + self.app.transmitAddress[3]
        len = (self.app.transmitLength[0] << 24) + (self.app.transmitLength[1] << 16) + (self.app.transmitLength[2] << 8) + self.app.transmitLength[3]
        callback(addr, len)

    def Flashing(self, notifyProgress=None):


        crcValue = CRC32()
        appTransmitAddress = self.app.transmitAddress
        AppTransmitLength = self.app.transmitLength
        info = "Parse binary file successfully"
        notifyProgress(1, info)

        udsConnection = Uds()
        info = "UDS connection is open"
        notifyProgress(2, info)
        requestCmd = []

        ###############
        ##print("Enter Des Session")
        requestCmd =  [0x10, 0x76]
        #response = udsConnection.send(requestCmd)
        ##print(response)
        info = "Enter Des session"
        notifyProgress(3, info)
        ###############
        sleep(0.2)
        info = "Start to erase the application region"
        notifyProgress(4, info)
        ##print(info)
        ## address 0x1003 0000, len 0x0006 0000
        ##requestCmd =  [0x31, 0x01, 0x76, 0xF1, 0x44, 0x10, 0x03, 0x00, 0x00, 0x00, 0x06, 0x00, 0x00]
        eraseCmd = [0x31, 0x01] + EraseRoutineSID +  RoutineMemID + appTransmitAddress + AppTransmitLength
        printHex(eraseCmd)
        response = udsConnection.send(eraseCmd)
        printHex(response)  
        info = "Erase successfully!"
        notifyProgress(5, info)
        info = "Setting up transfer for Application"
        notifyProgress(6, info)
        
        blocks = self.app.blocks
        dataIdx = 0
        sleep(0.2)

        for i in blocks:
            chunks = i.transmitChunks(512)
            #calculate CRC value
            crcValue.calculateCRC32(chunks)
            transmitAddress = i.transmitAddress
            transmitLength = i.transmitLength
            reqDlCmd = [0x34, 0x00, 0x44] + transmitAddress + transmitLength
            info = "Request download block " + str(blocks.index(i))
            notifyProgress(None, info)
            #print(info)
            printHex(reqDlCmd)
            response =  udsConnection.send(reqDlCmd)
            printHex(response)
            sleep(0.2)

            for blockCnt in range(0, len(chunks)):
                transferDataCmd = [0x36, (blockCnt + 1)] + chunks[blockCnt] 
                info = "Transfer block................." + str(blockCnt + 1)
                #print(info)
                printHex(transferDataCmd)
                response =  udsConnection.send(transferDataCmd)
                printHex(response)
                sleep(0.1)
                dataIdx+=1
                notifyProgress(7 + (dataIdx * 89 // (len(blocks) * len(chunks))), info)

            info = "Transfer Exit for block " + str(blocks.index(i))
            #print(info)
            TransferExitCmd = [0x37]
            response = udsConnection.send(TransferExitCmd)
            printHex(response)

        
        info = "Start to Check integrity................."
        notifyProgress(96, info)
        #ChecksumCmd =  [0x31, 0x01, 0x76, 0xF2, 0x44, 0x12, 0x03, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00]
        appTransmitAddress = [0x12, 0x00, 0x80, 0x00]
        ChecksumCmd = [0x31, 0x01] + ChecksumRoutineSID +  RoutineMemID + appTransmitAddress + AppTransmitLength
        printHex(ChecksumCmd)
        response =  udsConnection.send(ChecksumCmd)
        #response = [0x71, 0x1, 0x76, 0xf2, 0xae, 0x1, 0x51, 0x75]
        printHex(response)
        info = crcValue.verifyChecksum(response[4:])
        notifyProgress(97, info)
        sleep(4)
        info = ("Request to perform switching bank.................")
        notifyProgress(98, info)
        SwitchBankCmd = [0x31, 0x01] + SwitchBankRoutineSID
        printHex(SwitchBankCmd)
        response =  udsConnection.send(SwitchBankCmd)
        printHex(response)
        info = ("Ready to switch bank at next system reset")
        notifyProgress(99, info)
        udsConnection.disconnect()
        info = ("Reprogram successfully!!!! Close the connection....")
        notifyProgress(100, info)
        #end of download sequence

    def __loadConfiguration(self):
        baseConfig = config_path
        self.__config = ConfigParser()
        if path.exists(baseConfig):
            self.__config.read(baseConfig)
        else:
            raise FileNotFoundError("No base config file")

def printHex(list):
    message = '[{}]'.format(', '.join(hex(x) for x in list)) 
    #print(message)
    log.writeLog(message)