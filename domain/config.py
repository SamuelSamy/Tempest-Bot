import json

class Config:
    
    def __init__(self):
        
        with open("data/config.json") as file:
            config_settings = json.load(file)

        self.__token = config_settings["token"]
        self.__prefix = config_settings["prefix"]


    @property
    def token(self):
        return self.__token


    @property
    def prefix(self):
        return self.__prefix