from __future__ import annotations


class DefaultStats:
    def __init__(self, data):
        self.matches_played: int = data.get("matchesPlayed", 0)
        self.rounds_played: int = data.get("roundsPlayed", 0)
        self.minutes_played: int = data.get("minutesPlayed", 0)
        self.matches_won: int = data.get("matchesWon", 0)
        self.matches_lost: int = data.get("matchesLost", 0)
        self.rounds_won: int = data.get("roundsWon", 0)
        self.rounds_lost: int = data.get("roundsLost", 0)
        self.kills: int = data.get("kills", 0)
        self.assists: int = data.get("assists", 0)
        self.death: int = data.get("death", 0)
        self.headshots: int = data.get("headshots", 0)
        self.melee_kills: int = data.get("meleeKills", 0)
        self.team_kills: int = data.get("teamKills", 0)
        self.opening_kills: int = data.get("openingKills", 0)
        self.opening_deaths: int = data.get("openingDeaths", 0)
        self.trades: int = data.get("trades", 0)
        self.opening_kill_trades: int = data.get("openingKillTrades", 0)
        self.opening_death_trades: int = data.get("openingDeathTrades", 0)
        self.revives: int = data.get("revives", 0)
        self.distance_travelled: int = data.get("distanceTravelled", 0)
        self.win_loss_ratio: float = data.get("winLossRatio", 0)
        self.kill_death_ratio: float = round((data.get("killDeathRatio", {}).get("value", 0) * 100), 2)
        self.headshot_accuracy: float = round((data.get("headshotAccuracy", {}).get("value", 0) * 100), 2)
        self.kills_per_round: float = round((data.get("killsPerRound", {}).get("value", 0) * 100), 2)
        self.rounds_with_a_kill: float = round((data.get("roundsWithAKill", {}).get("value", 0) * 100), 2)
        self.rounds_with_multi_kill: float = round((data.get("roundsWithMultiKill", {}).get("value", 0) * 100), 2)
        self.rounds_with_opening_kill: float = round((data.get("roundsWithOpeningKill", {}).get("value", 0) * 100), 2)
        self.rounds_with_opening_death: float = round((data.get("roundsWithOpeningDeath", {}).get("value", 0) * 100), 2)
        self.rounds_with_kost: float = round((data.get("roundsWithKOST", {}).get("value", 0) * 100), 2)
        self.rounds_survived: float = round((data.get("roundsSurvived", {}).get("value", 0) * 100), 2)
        self.rounds_with_an_ace: float = round((data.get("roundsWithAnAce", {}).get("value", 0) * 100), 2)
        self.rounds_with_clutch: float = round((data.get("roundsWithClutch", {}).get("value", 0) * 100), 2)
        self.time_alive_per_match: float = data.get("timeAlivePerMatch", 0)
        self.time_dead_per_match: float = data.get("timeDeadPerMatch", 0)
        self.distance_per_round: float = data.get("distancePerRound", 0)

    def __repr__(self) -> str:
        return str(vars(self))
