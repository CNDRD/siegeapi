
class TrendBlockDuration:
    MONTHLY = "months"
    WEEKLY = "weeks"
    DAILY = "days"


class TrendBlocks:
    def __init__(self, data: dict):
        self.stats_period: list[str] = data.get("statsPeriod", [])
        self.matches_played: list[int] = data.get("matchesPlayed", [])
        self.rounds_played: list[int] = data.get("roundsPlayed", [])
        self.minutes_played: list[int] = data.get("minutesPlayed", [])
        self.matches_won: list[int] = data.get("matchesWon", [])
        self.matches_lost: list[int] = data.get("matchesLost", [])
        self.rounds_won: list[int] = data.get("roundsWon", [])
        self.rounds_lost: list[int] = data.get("roundsLost", [])
        self.kills: list[int] = data.get("kills", [])
        self.assists: list[int] = data.get("assists", [])
        self.death: list[int] = data.get("death", [])
        self.headshots: list[int] = data.get("headshots", [])
        self.melee_kills: list[int] = data.get("meleeKills", [])
        self.team_kills: list[int] = data.get("teamKills", [])
        self.opening_kills: list[int] = data.get("openingKills", [])
        self.opening_deaths: list[int] = data.get("openingDeaths", [])
        self.trades: list[int] = data.get("trades", [])
        self.opening_kill_trades: list[int] = data.get("openingKillTrades", [])
        self.opening_death_trades: list[int] = data.get("openingDeathTrades", [])
        self.revives: list[int] = data.get("revives", [])
        self.distance_travelled: list[int] = data.get("distanceTravelled", [])
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

    def __repr__(self) -> str:
        return str(vars(self))
