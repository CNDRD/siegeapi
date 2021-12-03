from typing import Callable


class WeaponTypes:
    """ Weapon Types """
    ASSAULT_RIFLE: int = 1
    SUBMACHINE_GUN: int = 2
    LIGHT_MACHINE_GUN: int = 3
    MARKSMAN_RIFLE: int = 4
    HANDGUN: int = 5
    SHOTGUN: int = 6
    MACHINE_PISTOL: int = 7


WeaponNames = {
    1: "Assault Rifle",
    2: "Submachine Gun",
    3: "Light Machine Gun",
    4: "Marksman Rifle",
    5: "Handgun",
    6: "Shotgun",
    7: "Machine Pistol"
}


class Weapon:
    def __init__(self, weapon_type, stats=None):
        self.type = weapon_type
        self.name = WeaponNames.get(self.type, "Unknown")

        stat_name: Callable[[str], str] = lambda name: f"weapontypepvp_{name}:{self.type}:infinite"
        stats = stats or {}
        self.kills = stats.get(stat_name("kills"), 0)
        self.headshots = stats.get(stat_name("headshot"), 0)
        self.hits = stats.get(stat_name("bullethit"), 0)
        self.shots = stats.get(stat_name("bulletfired"), 0)

    def get_dict(self) -> dict[str: str | int]:
        return vars(self)
