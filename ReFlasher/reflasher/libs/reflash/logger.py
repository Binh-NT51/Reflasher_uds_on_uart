import logging
import sys
from datetime import datetime
from os import path, getcwd
from configparser import ConfigParser

config_path = path.join(getcwd(), "config.ini")
#config_path_exe = = path.dirname(path.abspath(__file__)) + "/config.ini"

class logger():
    def __init__(self):
        self.__config = None
        self.__loadConfiguration()
        if self.__config["log"]["logpath"].find("dummy") == -1:
            filehandler = self.__config["log"]["logpath"] +"/" + '{:%Y-%m-%d-%H-%M-%S}.log'.format(datetime.now())
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s [%(levelname)s] %(message)s",
                handlers=[
                    logging.FileHandler(filehandler),
                    logging.StreamHandler(sys.stdout)]
        )
    def writeLog(self, message):
        if self.__config["log"]["logpath"].find("dummy") == -1:
            logging.info(message)
        ##
    # @brief used to load the local configuration options and override them with any passed in from a config file
    def __loadConfiguration(self):
        # load the base config
        baseConfig = config_path
        self.__config = ConfigParser()
        if path.exists(baseConfig):
            self.__config.read(baseConfig)
        else:
            raise FileNotFoundError("No base config file")
        
