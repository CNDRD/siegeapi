from __future__ import annotations


class TrendBlockDuration:
    MONTHLY = "months"
    WEEKLY = "weeks"
    DAILY = "days"


class TrendBlocks:
    def __init__(self, data: dict):
        self.stats_period: list[str] = data.get("statsPeriod", [])
        self.matches_played: list[str] = data.get("matchesPlayed", [])
        self.rounds_played: list[str] = data.get("roundsPlayed", [])
        self.minutes_played: list[str] = data.get("minutesPlayed", [])
        self.matches_won: list[str] = data.get("matchesWon", [])
        self.matches_lost: list[str] = data.get("matchesLost", [])
        self.rounds_won: list[str] = data.get("roundsWon", [])
        self.rounds_lost: list[str] = data.get("roundsLost", [])
        self.kills: list[str] = data.get("kills", [])
        self.assists: list[str] = data.get("assists", [])
        self.death: list[str] = data.get("death", [])
        self.headshots: list[str] = data.get("headshots", [])
        self.melee_kills: list[str] = data.get("meleeKills", [])
        self.team_kills: list[str] = data.get("teamKills", [])
        self.opening_kills: list[str] = data.get("openingKills", [])
        self.opening_deaths: list[str] = data.get("openingDeaths", [])
        self.trades: list[str] = data.get("trades", [])
        self.opening_kill_trades: list[str] = data.get("openingKillTrades", [])
        self.opening_death_trades: list[str] = data.get("openingDeathTrades", [])
        self.revives: list[str] = data.get("revives", [])
        self.distance_travelled: list[str] = data.get("distanceTravelled", [])
        self.win_loss_ratio: list[float] = data.get("winLossRatio", [])
        self.kill_death_ratio: list[float] = data.get("killDeathRatio", [])
        self.headshot_accuracy: list[float] = data.get("headshotAccuracy", [])
        self.kills_per_round: list[float] = data.get("killsPerRound", [])
        self.rounds_with_kill: list[float] = data.get("roundsWithAKill", [])
        self.rounds_with_multi_kill: list[float] = data.get("roundsWithMultiKill", [])
        self.rounds_with_opening_kill: list[float] = data.get("roundsWithOpeningKill", [])
        self.rounds_with_opening_death: list[float] = data.get("roundsWithOpeningDeath", [])
        self.rounds_with_kost: list[float] = data.get("roundsWithKOST", [])
        self.rounds_survived: list[float] = data.get("roundsSurvived", [])
        self.rounds_with_ace: list[float] = data.get("roundsWithAnAce", [])
        self.rounds_with_clutch: list[float] = data.get("roundsWithClutch", [])
        self.time_alive_per_match: list[float] = data.get("timeAlivePerMatch", [])
        self.time_dead_per_match: list[float] = data.get("timeDeadPerMatch", [])
        self.distance_per_round: list[float] = data.get("distancePerRound", [])

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

    def get_timespan_dates(self) -> dict:
        return {"start_date": self._start_date, "end_date": self._end_date}

    def __repr__(self) -> str:
        return str(vars(self))
