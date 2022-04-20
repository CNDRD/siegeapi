
class FailedToConnect(Exception):
    pass


class InvalidRequest(Exception):
    def __init__(self, *args, code=0, **kwargs):
        super().__init__(*args, **kwargs)
        self.code = code


class InvalidAttributeCombination(Exception):
    pass
