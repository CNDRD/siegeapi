from __future__ import annotations


class Map:
    def __init__(self, data: dict):
        self.map_name: str = data.get("statsDetail")
        self.matches_played: int = data.get("matchesPlayed")
        self.rounds_played: int = data.get("roundsPlayed")
        self.minutes_played: int = data.get("minutesPlayed")
        self.matches_won: int = data.get("matchesWon")
        self.matches_lost: int = data.get("matchesLost")
        self.rounds_won: int = data.get("roundsWon")
        self.rounds_lost: int = data.get("roundsLost")
        self.kills: int = data.get("kills")
        self.assists: int = data.get("assists")
        self.death: int = data.get("death")
        self.headshots: int = data.get("headshots")
        self.melee_kills: int = data.get("meleeKills")
        self.team_kills: int = data.get("teamKills")
        self.opening_kills: int = data.get("openingKills")
        self.opening_deaths: int = data.get("openingDeaths")
        self.trades: int = data.get("trades")
        self.opening_kill_trades: int = data.get("openingKillTrades")
        self.opening_death_trades: int = data.get("openingDeathTrades")
        self.revives: int = data.get("revives")
        self.distance_travelled: int = data.get("distanceTravelled")
        self.win_loss_ratio: float = data.get("winLossRatio")
        self.kill_death_ratio: float = round((data.get("killDeathRatio").get("value") * 100), 2)
        self.headshot_accuracy: float = round((data.get("headshotAccuracy").get("value") * 100), 2)
        self.kills_per_round: float = round((data.get("killsPerRound").get("value") * 100), 2)
        self.rounds_with_a_kill: float = round((data.get("roundsWithAKill").get("value") * 100), 2)
        self.rounds_with_multi_kill: float = round((data.get("roundsWithMultiKill").get("value") * 100), 2)
        self.rounds_with_opening_kill: float = round((data.get("roundsWithOpeningKill").get("value") * 100), 2)
        self.rounds_with_opening_death: float = round((data.get("roundsWithOpeningDeath").get("value") * 100), 2)
        self.rounds_with_kost: float = round((data.get("roundsWithKOST").get("value") * 100), 2)
        self.rounds_survived: float = round((data.get("roundsSurvived").get("value") * 100), 2)
        self.rounds_with_an_ace: float = round((data.get("roundsWithAnAce").get("value") * 100), 2)
        self.rounds_with_clutch: float = round((data.get("roundsWithClutch").get("value") * 100), 2)
        self.time_alive_per_match: float = data.get("timeAlivePerMatch")
        self.time_dead_per_match: float = data.get("timeDeadPerMatch")
        self.distance_per_round: float = data.get("distancePerRound")

    def __repr__(self) -> str:
        return str(vars(self))


class MapRoles:
    def __init__(self, data: dict):
        self.all: list = [Map(map_) for map_ in data.get("teamRoles", {}).get("all", [])]
        self.attacker: list = [Map(map_) for map_ in data.get("teamRoles", {}).get("attacker", [])]
        self.defender: list = [Map(map_) for map_ in data.get("teamRoles", {}).get("defender", [])]


class Maps:
    def __init__(self, data: dict):
        self.all: MapRoles = MapRoles(data.get("platforms").get("PC").get("gameModes").get("all", {}))
        self.casual: MapRoles = MapRoles(data.get("platforms").get("PC").get("gameModes").get("casual", {}))
        self.ranked: MapRoles = MapRoles(data.get("platforms").get("PC").get("gameModes").get("ranked", {}))
        self.unranked: MapRoles = MapRoles(data.get("platforms").get("PC").get("gameModes").get("unranked", {}))
        self.newcomer: MapRoles = MapRoles(data.get("platforms").get("PC").get("gameModes").get("newcomer", {}))

    def __repr__(self) -> str:
        return str(vars(self))
