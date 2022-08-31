from __future__ import annotations

from .constants import WEAPONS_DICT


class Weapon:
    def __init__(self, data: dict):
        self.name: str = data.get("weaponName")
        self.kills: int = data.get("kills")
        self.headshots: int = data.get("headshots")
        self.hs_accuracy: float = data.get("headshotAccuracy")
        self.rounds_played: int = data.get("roundsPlayed")
        self.rounds_won: int = data.get("roundsWon")
        self.rounds_lost: float = data.get("roundsLost")
        self.rounds_with_kill: float = data.get("roundsWithAKill")
        self.rounds_with_multi_kill: float = data.get("roundsWithMultiKill")

        if weapon := WEAPONS_DICT.get(self.name):
            self.ubi_url: str = f"https://staticctf.akamaized.net/J3yJr34U2pZ2Ieem48Dwy9uqj5PNUQTn/{weapon.get('icon_url')}"
            self.imgur_url: str = weapon.get("imgur_url")
            self.type: str = weapon.get("type")
        else:
            self.ubi_url: str = "Missing Asset"
            self.imgur_url: str = "Missing Asset"
            self.type: str = "Missing Asset"

    def __repr__(self) -> str:
        return str(vars(self))


class WeaponsGameMode:
    def __init__(self, data: dict):
        self.primary: list = self._get_weapons_list(data.get("weaponSlots", {}).get("primaryWeapons", {}).get("weaponTypes", [{}])[0].get("weapons", []))
        self.secondary: list = self._get_weapons_list(data.get("weaponSlots", {}).get("secondaryWeapons", {}).get("weaponTypes", [{}])[0].get("weapons", []))

    @staticmethod
    def _get_weapons_list(data: list[dict] | None) -> list[Weapon] | None:
        return None if not data else [Weapon(weapon) for weapon in data]

    def __repr__(self) -> str:
        return str(vars(self))


class WeaponsRole:
    def __init__(self, data: dict):
        self.attacker: WeaponsGameMode = WeaponsGameMode(data.get("teamRoles", {}).get("attacker", {}))
        self.defender: WeaponsGameMode = WeaponsGameMode(data.get("teamRoles", {}).get("defender", {}))

    def __repr__(self) -> str:
        return str(vars(self))


class Weapons:
    def __init__(self, data: dict):
        self.all: WeaponsRole = WeaponsRole(data.get("platforms").get("PC").get("gameModes").get("all", {}))
        self.casual: WeaponsRole = WeaponsRole(data.get("platforms").get("PC").get("gameModes").get("casual", {}))
        self.ranked: WeaponsRole = WeaponsRole(data.get("platforms").get("PC").get("gameModes").get("ranked", {}))
        self.unranked: WeaponsRole = WeaponsRole(data.get("platforms").get("PC").get("gameModes").get("unranked", {}))
        self.newcomer: WeaponsRole = WeaponsRole(data.get("platforms").get("PC").get("gameModes").get("newcomer", {}))
        self._start_date: str = str(data.get("startDate", ""))
        self._end_date: str = str(data.get("endDate", ""))

    def get_timespan_dates(self) -> dict:
        return {"start_date": self._start_date, "end_date": self._end_date}

    def __repr__(self) -> str:
        return str(vars(self))
