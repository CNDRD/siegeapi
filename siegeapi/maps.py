from __future__ import annotations
from .default_stats import DefaultStats


class Map(DefaultStats):
    def __init__(self, data: dict):
        super().__init__(data)
        self.map_name: str = data.get("statsDetail")

    def __repr__(self) -> str:
        return str(vars(self))


class MapRoles:
    def __init__(self, data: dict):
        self.all: list = [Map(map_) for map_ in data.get("teamRoles", {}).get("all", [])]
        self.attacker: list = [Map(map_) for map_ in data.get("teamRoles", {}).get("Attacker", [])]
        self.defender: list = [Map(map_) for map_ in data.get("teamRoles", {}).get("Defender", [])]

    def __repr__(self) -> str:
        return str(vars(self))


class Maps:
    def __init__(self, data: dict):
        self.all: MapRoles = MapRoles(data.get("platforms").get("PC").get("gameModes").get("all", {}))
        self.casual: MapRoles = MapRoles(data.get("platforms").get("PC").get("gameModes").get("casual", {}))
        self.ranked: MapRoles = MapRoles(data.get("platforms").get("PC").get("gameModes").get("ranked", {}))
        self.unranked: MapRoles = MapRoles(data.get("platforms").get("PC").get("gameModes").get("unranked", {}))
        self._start_date: str = str(data.get("startDate", ""))
        self._end_date: str = str(data.get("endDate", ""))

    def get_timespan_dates(self) -> dict[str: str]:
        return {"start_date": self._start_date, "end_date": self._end_date}

    def __repr__(self) -> str:
        return str(vars(self))
