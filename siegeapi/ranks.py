from .constants.ranks import *


def get_rank_constants(season_number: int = -1) -> list[dict[str: str | int]]:
    if 1 <= season_number <= 3:
        return ranks_v1
    if 4 == season_number:
        return ranks_v2
    if 5 <= season_number <= 14:
        return ranks_v3
    if 15 <= season_number <= 22:
        return ranks_v4
    if season_number <= 23:
        return ranks_v5
    return ranks_v5


class Rank:
    def __init__(self, data, rank_definitions):
        self.kills: int = data.get("kills", 0)
        self.deaths: int = data.get("deaths", 0)
        self.last_mmr_change: float = data.get("last_match_mmr_change", 0)
        self.prev_rank_mmr: float = data.get("previous_rank_mmr", 0)
        self.next_rank_mmr: float = data.get("next_rank_mmr", 0)
        self.mmr: float = data.get("mmr", 0)
        self.max_mmr: float = data.get("max_mmr", 0)
        self.wins: int = data.get("wins", 0)
        self.losses: int = data.get("losses", 0)
        self.rank_id: int = data.get("rank")
        self.season: int = data.get("season", -1)
        self.rank: str = rank_definitions[self.rank_id]["name"]
        self.max_rank_id: int = data.get("max_rank")
        self.max_rank: str = rank_definitions[self.max_rank_id]["name"]
        self.region: str = data.get("region")
        self.abandons: int = data.get("abandons", 0)
        self.skill_mean: float = data.get("skill_mean", 0)
        self.skill_stdev: float = data.get("skill_stdev", 0)

    def get_dict(self) -> dict[str: str | int | float]:
        return vars(self)
