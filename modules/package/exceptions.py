class TypeException(Exception):
    
    def __init__(self, message):
        self.__message = message

    def __str__(self):
        return self.__message


class UnexpectedError(Exception):
    
    def __init__(self, message):
        self.__message = message

    def __str__(self):
        return self.__message


class TimeException(Exception):
    
    def __init__(self, message):
        self.__message = message

    def __str__(self):
        return self.__message


class DMException(Exception):
    
    def __init__(self, message):
        self.__message = message

    def __str__(self):
        return self.__message


class MmeberNotFoundException(Exception):
    
    def __init__(self, message):
        self.__message = message

    def __str__(self):
        return self.__message


class MemberNotAffectedByModeration(Exception):

    def __init__(self, message):
        self.__message = message

    def __str__(self):
        return self.__message


class CaseException(Exception):

    def __init__(self, message):
        self.__message = message

    def __str__(self):
        return self.__message


class LevelingError(Exception):

    def __init__(self, message):
        self.__message = message

    def __str__(self):
        return self.__message

class MuteException(Exception):

    def __init__(self, message):
        self.__message = message

    def __str__(self):
        return self.__message


class StarboardException(Exception):
    def __init__(self, message):
            self.__message = message

    def __str__(self):
        return self.__message


class WordError(Exception):
    def __init__(self, message):
            self.__message = message

    def __str__(self):
        return self.__message

class PunishmentException(Exception):
    def __init__(self, message):
            self.__message = message

    def __str__(self):
        return self.__message