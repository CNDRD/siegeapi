from typing import List


class TrendBlockDuration:
    MONTHLY = "months"
    WEEKLY = "weeks"
    DAILY = "days"


class TrendBlocks:
    def __init__(self, data: dict):
        self.stats_period: List[str] = data.get("statsPeriod", [])
        self.matches_played: List[int] = data.get("matchesPlayed", [])
        self.rounds_played: List[int] = data.get("roundsPlayed", [])
        self.minutes_played: List[int] = data.get("minutesPlayed", [])
        self.matches_won: List[int] = data.get("matchesWon", [])
        self.matches_lost: List[int] = data.get("matchesLost", [])
        self.rounds_won: List[int] = data.get("roundsWon", [])
        self.rounds_lost: List[int] = data.get("roundsLost", [])
        self.kills: List[int] = data.get("kills", [])
        self.assists: List[int] = data.get("assists", [])
        self.death: List[int] = data.get("death", [])
        self.headshots: List[int] = data.get("headshots", [])
        self.melee_kills: List[int] = data.get("meleeKills", [])
        self.team_kills: List[int] = data.get("teamKills", [])
        self.opening_kills: List[int] = data.get("openingKills", [])
        self.opening_deaths: List[int] = data.get("openingDeaths", [])
        self.trades: List[int] = data.get("trades", [])
        self.opening_kill_trades: List[int] = data.get("openingKillTrades", [])
        self.opening_death_trades: List[int] = data.get("openingDeathTrades", [])
        self.revives: List[int] = data.get("revives", [])
        self.distance_travelled: List[int] = data.get("distanceTravelled", [])
        self.win_loss_ratio: List[float] = data.get("winLossRatio", [])
        self.kill_death_ratio: List[float] = data.get("killDeathRatio", [])
        self.headshot_accuracy: List[float] = data.get("headshotAccuracy", [])
        self.kills_per_round: List[float] = data.get("killsPerRound", [])
        self.rounds_with_kill: List[float] = data.get("roundsWithAKill", [])
        self.rounds_with_multi_kill: List[float] = data.get("roundsWithMultiKill", [])
        self.rounds_with_opening_kill: List[float] = data.get("roundsWithOpeningKill", [])
        self.rounds_with_opening_death: List[float] = data.get("roundsWithOpeningDeath", [])
        self.rounds_with_kost: List[float] = data.get("roundsWithKOST", [])
        self.rounds_survived: List[float] = data.get("roundsSurvived", [])
        self.rounds_with_ace: List[float] = data.get("roundsWithAnAce", [])
        self.rounds_with_clutch: List[float] = data.get("roundsWithClutch", [])
        self.time_alive_per_match: List[float] = data.get("timeAlivePerMatch", [])
        self.time_dead_per_match: List[float] = data.get("timeDeadPerMatch", [])
        self.distance_per_round: List[float] = data.get("distancePerRound", [])

    def __repr__(self) -> str:
        return str(vars(self))


class TrendsGameMode:
    def __init__(self, data: dict, name: str):
        self.name = name
        self.all = TrendBlocks(next(iter(data.get("teamRoles", {}).get("all", [])), {}))
        self.attacker = TrendBlocks(next(iter(data.get("teamRoles", {}).get("attacker", [])), {}))
        self.defender = TrendBlocks(next(iter(data.get("teamRoles", {}).get("defender", [])), {}))

    def __repr__(self) -> str:
        return str(vars(self))


class Trends:
    def __init__(self, data: dict):
        self.all = TrendsGameMode(data.get("platforms").get("PC").get("gameModes").get("all", {}), "all")
        self.casual = TrendsGameMode(data.get("platforms").get("PC").get("gameModes").get("casual", {}), "casual")
        self.ranked = TrendsGameMode(data.get("platforms").get("PC").get("gameModes").get("ranked", {}), "ranked")
        self.unranked = TrendsGameMode(data.get("platforms").get("PC").get("gameModes").get("unranked", {}), "unranked")
        self.newcomer = TrendsGameMode(data.get("platforms").get("PC").get("gameModes").get("unranked", {}), "newcomer")
        self._start_date: str = str(data.get("startDate", ""))
        self._end_date: str = str(data.get("endDate", ""))

    def get_timespan_dates(self) -> dict[str: str]:
        return {"start_date": self._start_date, "end_date": self._end_date}

    def __repr__(self) -> str:
        return str(vars(self))
