class TexchException(Exception):
    pass


class NoInputDataException(TexchException):
    pass


class NoMethodSetException(TexchException):
    pass


class NotRunYetException(TexchException):
    pass


class NotTrueLabelsSetException(TexchException):
    pass


class NotCorrectEstimatorException(TexchException):
    pass


class ProxyObjectException(TexchException):
    pass


class PreprocessingException(TexchException):
    pass
