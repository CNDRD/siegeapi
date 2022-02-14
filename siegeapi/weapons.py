from .constants import WEAPONS_DICT


class Weapon:
    def __init__(self, data):
        self.name: str = data.get("weaponName")
        self.kills: int = data.get("kills")
        self.headshots: int = data.get("headshots")
        self.hs_accuracy: float = data.get("headshotAccuracy")
        self.rounds_played: int = data.get("roundsPlayed")
        self.rounds_won: int = data.get("roundsWon")
        self.rounds_lost: float = data.get("roundsLost")
        self.rounds_with_kill: float = data.get("roundsWithAKill")
        self.rounds_with_multi_kill: float = data.get("roundsWithMultiKill")

        weapon = WEAPONS_DICT.get(self.name)
        self.image_url: str = f"https://staticctf.akamaized.net/J3yJr34U2pZ2Ieem48Dwy9uqj5PNUQTn/{weapon.get('icon_url')}"
        self.type: str = weapon.get("type")


class WeaponSlots:
    ...


class Weapons:
    ...
