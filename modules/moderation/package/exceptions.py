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
