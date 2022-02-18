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
            self.image_url: str = f"https://staticctf.akamaized.net/J3yJr34U2pZ2Ieem48Dwy9uqj5PNUQTn/{weapon.get('icon_url')}"
            self.type: str = weapon.get("type")
        else:
            self.image_url: str = "Missing Asset"
            self.type: str = "Missing Asset"

    def __repr__(self) -> str:
        return str(vars(self))


class WeaponsGameMode:
    def __init__(self, data: dict):
        self.primary: list = self._get_weapons_list(data.get("teamRoles", {}).get("all", {}).get("weaponSlots", {}).get("primaryWeapons", {}).get("weaponTypes", {}))
        self.secondary: list = self._get_weapons_list(data.get("teamRoles", {}).get("all", {}).get("weaponSlots", {}).get("secondaryWeapons", {}).get("weaponTypes", {}))

    def _get_weapons_list(self, data: list[dict]) -> list[Weapon]:
        return [Weapon(weapon) for weaponType in data for weapon in weaponType.get("weapons")]

    def __repr__(self) -> str:
        return str(vars(self))


class Weapons:
    def __init__(self, data: dict):
        self.all: WeaponsGameMode = WeaponsGameMode(data.get("platforms").get("PC").get("gameModes").get("all", {}))
        self.casual: WeaponsGameMode = WeaponsGameMode(data.get("platforms").get("PC").get("gameModes").get("casual", {}))
        self.ranked: WeaponsGameMode = WeaponsGameMode(data.get("platforms").get("PC").get("gameModes").get("ranked", {}))
        self.unranked: WeaponsGameMode = WeaponsGameMode(data.get("platforms").get("PC").get("gameModes").get("unranked", {}))

    def __repr__(self) -> str:
        return str(vars(self))
