class QBExpcetion(Exception):
    """Base exception"""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class QBXMLError(QBExpcetion):
    pass


class QBXMLProcessingError(QBExpcetion):
    pass


class QBXMLRequestError(QBExpcetion):
    pass
