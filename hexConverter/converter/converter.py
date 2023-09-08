import re, os
import subprocess
from configparser import ConfigParser

pattern_S7 = re.compile(r'^S7')
pattern_S3 = re.compile(r'S3')
pattern_S5 = re.compile(r'^S5')

PADDING_BYTE = 'FFFF'

S19_ADDRESS_START_INDEX = 4
S19_ADDRESS_END_INDEX = 12

working_path = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(working_path, "config.ini")
HEXVIEW_EXE = os.path.join(working_path, r'..\util\HexView\hexview.exe')

class s19Parser:
    def __init__(self, inputpath = None):
        self.startAddress = 0x00000000
        self.endAddress = 0x00000000
        self.ipath = inputpath

    def getStartAddress(self):
        with open (self.ipath, 'r+') as file:
            lines = file.readlines()
        for line in lines:
            if (None != re.match(pattern_S3, line)):
                self.startAddress = int(line[S19_ADDRESS_START_INDEX:S19_ADDRESS_END_INDEX], 16)
                return self.startAddress

    def getEndAddress(self):
        with open (self.ipath, 'r+') as file:
            lines = file.readlines()
        for line in lines:
            if (None != re.match(pattern_S7, line)):
                prev_line = lines[lines.index(line)-1]
                if (None != re.match(pattern_S5, prev_line)):
                    prev_line = lines[lines.index(prev_line)-1]
        
                self.endAddress = int(prev_line[S19_ADDRESS_START_INDEX:S19_ADDRESS_END_INDEX], 16)
                return self.endAddress

class hewViewCommand:
    def __init__(self, inputpath = None):
        self.ipath = inputpath

    def fillPadding(self, inputfile, start, end, outputfile, padding): 
        command = self.ipath + ' ' + inputfile + ' /FR:' + start + '-' + end + ' /FP:' + padding + ' /XI:32:0 /s' + ' -o ' + outputfile
        print(command)
        subprocess.call(command, shell=False)

def __loadconfig():
    # load the base config
    baseConfig = config_path
    config = ConfigParser()
    if os.path.exists(baseConfig):
        config.read(baseConfig)
    else:
        raise FileNotFoundError("No base config file")
    return config

def main():
    print("Start to convert s19 to hex file for reflashing....")
    configfile = __loadconfig()
    S19_INPUT_FILE = configfile['Input']['input_path']
    if configfile['Output']['output_path'].find('default') != -1:
        OUTPUT_FILE = os.path.join(working_path, '..\output\startupkit_2m.hex')
    else:
         OUTPUT_FILE = configfile['Output']['output_path']
    app_s19 = s19Parser(S19_INPUT_FILE)
    start_address = app_s19.getStartAddress()
    end_address = app_s19.getEndAddress()
    #if end_address < 0x10067fff:
    #    end_address = 0x10067fff
    #print(hex(start_address) +"   hihi  " + hex(end_address))
    #convert
    myhexview = hewViewCommand(HEXVIEW_EXE)
    myhexview.fillPadding(S19_INPUT_FILE, hex(start_address), hex(end_address), OUTPUT_FILE, PADDING_BYTE)

if __name__=='__main__':
    main()
