from .default_stats import DefaultStats


class Summary(DefaultStats):
    def __init__(self, data: dict):
        super().__init__(data)

    def __repr__(self) -> str:
        return str(vars(self))
