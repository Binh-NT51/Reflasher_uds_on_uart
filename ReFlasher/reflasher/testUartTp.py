from threading import Thread
from libs.reflash.UartTp import uartTp
from time import sleep

def printHex(list):
    print('[{}]'.format(', '.join(hex(x) for x in list)))
    pass

if __name__ == "__main__":

    connection = uartTp()

    payload = [0x22, 0x76, 0xAA]
    timecount = 1
    printHex(payload)

    while (timecount!=0):
        sleep(0.5)
        try: 
            connection.send(payload)
            RX = connection.recv(4)
            printHex(RX)
            print(len(RX))
        except Exception as e:
            traceback.print_exc()
        timecount = timecount - 1
    connection.closeConnection()

