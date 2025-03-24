class APIBaseException(Exception):
    def __init__(self, message: str = ""):
        self.message = message
        super().__init__(self.message)


class RequestFailedException(APIBaseException):
    pass


class InvalidResponseException(APIBaseException):
    pass