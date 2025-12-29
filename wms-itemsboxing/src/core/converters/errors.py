class ConversionError(RuntimeError):

    def __init__(self, message):
        RuntimeError.__init__(self, message)


class UnexpectedType(ConversionError):

    def __init__(self, obj: object, expected: str = None):
        message = f"Object of type '{type(obj).__name__}' can't be converted"
        if expected != None:
            message += f". Expected type: '{expected}'"
        ConversionError.__init__(self, message)


class InputConversionError(ConversionError):

    def __init__(self, parent: Exception):
        ConversionError.__init__(
            self, f"Couldn't convert input model: {type(parent).__name__}: {parent}.")


class OutputConversionError(ConversionError):

    def __init__(self, parent: Exception):
        ConversionError.__init__(
            self, f"Couldn't convert output model: {type(parent).__name__}: {parent}.")
