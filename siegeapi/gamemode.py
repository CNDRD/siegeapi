from __future__ import annotations
from .default_stats import DefaultStats


class Gamemode(DefaultStats):
    def __init__(self, data: dict):
        data = data.get("teamRoles", {}).get("all", [{}])[0]
        super().__init__(data)


class Gamemodes:
    def __init__(self, data: dict):
        self.all: Gamemode = Gamemode(data.get("platforms").get("PC").get("gameModes").get("all", {}))
        self.casual: Gamemode = Gamemode(data.get("platforms").get("PC").get("gameModes").get("casual", {}))
        self.ranked: Gamemode = Gamemode(data.get("platforms").get("PC").get("gameModes").get("ranked", {}))
        self.unranked: Gamemode = Gamemode(data.get("platforms").get("PC").get("gameModes").get("unranked", {}))
        self.newcomer: Gamemode = Gamemode(data.get("platforms").get("PC").get("gameModes").get("newcomer", {}))
        self._start_date: str = str(data.get("startDate", ""))
        self._end_date: str = str(data.get("endDate", ""))

    def get_timespan_dates(self) -> dict[str: str]:
        return {"start_date": self._start_date, "end_date": self._end_date}

    def __repr__(self) -> str:
        return str(vars(self))
