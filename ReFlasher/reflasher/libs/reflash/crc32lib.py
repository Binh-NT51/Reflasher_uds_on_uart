import zlib


class CRC32():
    def __init__(self):
        self.isFirstCall = True
        self.initCRCValue = 0       # 0xFFFFFFFF
        self.calCrcValue = 0
    def calculateCRC32(self, dataBlocks):
        for dataBlock in dataBlocks:
            chunkStr = dataBlock    #[str(x) for x in dataBlock]
            for i in chunkStr:
                if (self.isFirstCall == True):
                    self.isFirstCall = False
                    self.calCrcValue = self.initCRCValue
                self.calCrcValue = zlib.crc32(i.to_bytes(1,'big'), self.calCrcValue)

    def getCalCRC32Value(self):
        self.isFirstCall = True
        return self.calCrcValue
    #targetCRC is list of 4 bytes in length
    def verifyChecksum(self, targetCRCArr):
        targetCRC = 0
        crcValue =  self.getCalCRC32Value()
        print("calculated checksum is " + hex(crcValue))
        targetCRC = (targetCRCArr[0] << 24) + (targetCRCArr[1] << 16) + (targetCRCArr[2] << 8) + targetCRCArr[3]
        if (targetCRC == crcValue):
            retStr = ("................Checksum is passed .............")
        else:
            retStr = ("xxxxxxxxxxxxxxx Checksum DOES NOT match xxxxxxxx")
        return retStr