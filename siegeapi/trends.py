from __future__ import annotations


class TrendDataPoint:
    def __init__(self, data: dict):
        self.low: float = data.get("high", 0)
        self.high: float = data.get("high", 0)
        self.average: float = data.get("average", 0)
        self.trend: dict[str, float] = data.get("trend", {})
        self.actuals: dict[str, float] = data.get("actuals", {})

    def __repr__(self) -> str:
        return str(vars(self))


class TrendData:
    def __init__(self, data: dict):
        self.win_loss_ratio: TrendDataPoint = TrendDataPoint(data.get("winLossRatio", {}))
        self.kill_death_ratio: TrendDataPoint = TrendDataPoint(data.get("killDeathRatio", {}))
        self.headshot_accuracy: TrendDataPoint = TrendDataPoint(data.get("headshotAccuracy", {}))
        self.kills_per_round: TrendDataPoint = TrendDataPoint(data.get("killsPerRound", {}))
        self.rounds_with_a_kill: TrendDataPoint = TrendDataPoint(data.get("roundsWithAKill", {}))
        self.rounds_with_multi_kill: TrendDataPoint = TrendDataPoint(data.get("roundsWithMultiKill", {}))
        self.rounds_with_opening_kill: TrendDataPoint = TrendDataPoint(data.get("roundsWithOpeningKill", {}))
        self.rounds_with_opening_death: TrendDataPoint = TrendDataPoint(data.get("roundsWithOpeningDeath", {}))
        self.rounds_with_kost: TrendDataPoint = TrendDataPoint(data.get("roundsWithKOST", {}))
        self.rounds_survived: TrendDataPoint = TrendDataPoint(data.get("roundsSurvived", {}))
        self.ratio_time_alive_per_match: TrendDataPoint = TrendDataPoint(data.get("ratioTimeAlivePerMatch", {}))
        self.distance_per_round: TrendDataPoint = TrendDataPoint(data.get("distancePerRound", {}))

    def __repr__(self) -> str:
        return str(vars(self))


class TrendsGameMode:
    def __init__(self, data: dict):
        self.all: TrendData = TrendData(data.get("teamRoles", {}).get("all", [{}])[0])
        self.attacker: TrendData = TrendData(data.get("teamRoles", {}).get("attacker", [{}])[0])
        self.defender: TrendData = TrendData(data.get("teamRoles", {}).get("defender", [{}])[0])

    def __repr__(self) -> str:
        return str(vars(self))


class Trends:
    def __init__(self, data: dict):
        self.all: TrendsGameMode = TrendsGameMode(data.get("platforms").get("PC").get("gameModes").get("all", {}))
        self.casual: TrendsGameMode = TrendsGameMode(data.get("platforms").get("PC").get("gameModes").get("casual", {}))
        self.ranked: TrendsGameMode = TrendsGameMode(data.get("platforms").get("PC").get("gameModes").get("ranked", {}))
        self.unranked: TrendsGameMode = TrendsGameMode(data.get("platforms").get("PC").get("gameModes").get("unranked", {}))
        self.newcomer: TrendsGameMode = TrendsGameMode(data.get("platforms").get("PC").get("gameModes").get("newcomer", {}))
        self._start_date: str = str(data.get("startDate", ""))
        self._end_date: str = str(data.get("endDate", ""))

    def get_timespan_dates(self) -> dict:
        return {"start_date": self._start_date, "end_date": self._end_date}

    def __repr__(self) -> str:
        return str(vars(self))
