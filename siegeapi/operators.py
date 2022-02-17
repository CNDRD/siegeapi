from .constants import operator_dict


def _get_from_operators_const(name: str, what: str) -> str:
    return operator_dict[name][what]


class Operator:
    def __init__(self, name, stats=None, unique_stats=None):
        self.name = name.lower()
        self.readable = _get_from_operators_const(self.name, 'name')

        stats = stats or {}
        self.wins = stats.get("roundwon", 0)
        self.losses = stats.get("roundlost", 0)
        self.kills = stats.get("kills", 0)
        self.deaths = stats.get("death", 0)
        self.headshots = stats.get("headshot", 0)
        self.melees = stats.get("meleekills", 0)
        self.dbnos = stats.get("dbno", 0)
        self.xp = stats.get("totalxp", 0)
        self.time_played = stats.get("timeplayed", 0)
        self.atkdef = _get_from_operators_const(self.name, 'side')
        self.icon = _get_from_operators_const(self.name, 'icon_url')

        if unique_stats is not None:
            self.unique_stats = unique_stats
        else:
            self.unique_stats = {}

    def get_dict(self) -> dict[str: int | str]:
        return vars(self)
