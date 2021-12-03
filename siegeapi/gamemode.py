
class Gamemode:
    """ Contains information about a specific game queue """
    def __init__(self, name, stats=None):
        self.name = name

        statname = f"{name}pvp_"

        stats = stats or {}
        self.won = stats.get(f"{statname}matchwon", 0)
        self.lost = stats.get(f"{statname}matchlost", 0)
        self.time_played = stats.get(f"{statname}timeplayed", 0)
        self.played = stats.get(f"{statname}matchplayed", 0)
        self.kills = stats.get(f"{statname}kills", 0)
        self.deaths = stats.get(f"{statname}death", 0)

    def get_dict(self) -> dict[str: int]:
        return vars(self)
