import sys
from PyQt5.QtCore import QThread, pyqtSignal, QObject, QCoreApplication
#from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog, QGridLayout
from PyQt5.QtSerialPort import QSerialPortInfo
from PyQt5.uic import loadUi
from configparser import ConfigParser


import queue
import os
#import reflash folder
import sys
#sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs/designer')))
import libs.designer.icons_qrc as icons_qrc
#sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs/reflash')))
import libs.reflash.Flashing as Flashing

import time

##############################################################################
####                            local variable                            ####
##############################################################################
gui_designer_path = os.path.join(os.getcwd(), 'Flasher.ui')
config_path = os.path.join(os.getcwd(), "config.ini")

ex = None

DownloadSequence = Flashing.DownloadSequence()

class FlashThread(QThread):
    FlashProgrress= pyqtSignal(int, str)
    
    def __init__(self, callback):
        super().__init__()
        self.FlashProgrress.connect(callback)

    def run(self):
        DownloadSequence.Flashing(self.callout)
    
    def callout(self, progress = None, info = None):
        self.FlashProgrress.emit(progress, info)
            
class LoadBinaryThread(QThread):
    LoadBinarySignal = pyqtSignal(int, int)

    def __init__(self, LoadBinaryCallout):
        super().__init__()
        self.LoadBinarySignal.connect(LoadBinaryCallout)

    def run(self):
        DownloadSequence.LoadBinary(self.LBCallout)

    def LBCallout(self, startaddress = None, size = None):
        print(startaddress)
        self.LoadBinarySignal.emit(startaddress, size)
    

class MainWindow(QDialog):
    def __init__(self):
        self.__Flashconfig = None
        self.__loadConfiguration()

        super(MainWindow, self).__init__()
        loadUi(gui_designer_path, self)
        self.setFixedSize(959, 530)
        #layoutgrid = QGridLayout()
        #self.setLayout(layoutgrid)
        ####
        self.BrowseApp.clicked.connect(self.browsefiles)
        self.BrowseLog.clicked.connect(self.browselogfile)
        self.ConnectButton.clicked.connect(self.connectSerial)
        self.Download.clicked.connect(self.startdownload)
        self.DisplayText.append("Welcome to DNGA pre-dev!")
        #progress bar
        self.ProgressBar.setMaximum(100)

        for info in QSerialPortInfo.availablePorts():
            self.PortName.addItem(info.portName())

        for baudrate in QSerialPortInfo.standardBaudRates():
            self.Baudrate.addItem(str(baudrate), baudrate)
    #communcation
    def getSerialConfig(self):
        return self.PortName.currentText(), self.Baudrate.currentData()

    def connectSerial(self):
        serport, serbaud = self.getSerialConfig()
        self.__Flashconfig['uart']['port'] = serport
        self.__Flashconfig['uart']['baudrate'] = str(serbaud)
        
        self.__updateConfiguration()
    #hex file
    def browsefiles(self):
        currentpath = os.getcwd()
        filename = QFileDialog.getOpenFileName(self, 'Open file', currentpath, 'Hex files (*.hex)')
        self.FileName.setText(filename[0])
        
        self.__Flashconfig['flash']['hexfile'] = filename[0]
        self.__updateConfiguration()

        self.LoadBinThread = LoadBinaryThread(self.displayBinInfo)
        self.LoadBinThread.start()
    #log file
    def browselogfile(self):
        currentpath = os.getcwd()
        filename = QFileDialog.getExistingDirectory(self, 'Open folder')
        self.FileLogName.setText(filename)
        
        self.__Flashconfig['log']['logpath'] = filename
        self.__updateConfiguration() 
    #download
    def startdownload(self):
        self.startDownloadSequence()

    def startDownloadSequence(self):
        self.FlashThread = FlashThread(self.handleProgress)
        self.FlashThread.start()

    #progress
    def handleProgress(self, progress, info):
        self.setProgressValue(progress)
        self.displayText(info)
            

    def setProgressValue(self, val):
        if val is not None:
            value = val
            self.ProgressBar.setValue(value)

    #display
    def displayText(self, text = None):
        if len(text) != 0:
            self.DisplayText.append(text)

    def displayBinInfo(self, address, size):
        if (address != None) and (size != None):
            self.BinFileStart.setText(hex(address))
            self.BinFileSize.setText(hex(size))
    ##
    # @brief used to load the local configuration options and override them with any passed in from a config file
    def __loadConfiguration(self):
        # load the base config
        baseConfig = config_path
        self.__Flashconfig = ConfigParser()
        if os.path.exists(baseConfig):
            self.__Flashconfig.read(baseConfig)
        else:
            raise FileNotFoundError("No base config file")
    def __updateConfiguration(self):
        baseConfig = config_path
        with open(baseConfig, 'w') as configfile:
            self.__Flashconfig.write(configfile)
        configfile.close()

    def __resetConfiguration(self):
        self.__Flashconfig['flash']['hexfile'] = 'dummy'
        self.__Flashconfig['log']['logpath'] = 'dummy'
        self.__updateConfiguration()


def main():
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
if __name__ == '__main__':
   main()