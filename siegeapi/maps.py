from __future__ import annotations
from typing import Dict
from .default_stats import DefaultStats


class Map(DefaultStats):
    def __init__(self, data: dict):
        super().__init__(data)
        self.map_name: str = data.get("statsDetail","")

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
        platform_data = data.get("platforms", {})
        platform_data = platform_data.get(list(platform_data.keys())[0] if len(platform_data.keys()) > 0 else "PC", {})

        self.all: MapRoles = MapRoles(platform_data.get("gameModes", {}).get("all", {}))
        self.casual: MapRoles = MapRoles(platform_data.get("gameModes", {}).get("casual", {}))
        self.ranked: MapRoles = MapRoles(platform_data.get("gameModes", {}).get("ranked", {}))
        self.unranked: MapRoles = MapRoles(platform_data.get("gameModes", {}).get("unranked", {}))
        self._start_date: str = str(data.get("startDate", ""))
        self._end_date: str = str(data.get("endDate", ""))

    def get_timespan_dates(self) -> Dict[str, str]:
        return {"start_date": self._start_date, "end_date": self._end_date}

    def __repr__(self) -> str:
        return str(vars(self))
