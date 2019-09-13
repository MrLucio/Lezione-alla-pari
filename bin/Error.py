class Error:

    def __init__(self, type, message=""):

        self._type = type
        self._message = message

    def get_type(self):
        return self._type

    def get_message(self):
        return self._message

    @staticmethod
    def is_error(value):
        if isinstance(value, Error):
            return True
        return False

    def __bool__(self):
        return False

    def __str__(self):
        return(
            "{err_type}: {err_message}".format(
                err_type=self._type, err_message=self._message
            )
        )
