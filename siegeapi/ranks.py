from __future__ import annotations
from typing import Tuple, List

from .constants.ranks import *
from .constants.seasons import seasons


def _get_rank_constants(season_number: int = -1) -> List[dict[str: str | int]]:
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


def _get_rank_from_mmr(mmr: int | float, season: int = -1) -> Tuple[str, int, int, int]:
    for rank_id, r in enumerate(_get_rank_constants(season)):
        if r["min_mmr"] <= int(mmr) <= r["max_mmr"]:
            return r["name"], r["min_mmr"], r["max_mmr"]+1, rank_id
    return "Unranked", 0, 0, 0


class Rank:
    def __init__(self, data):
        self.kills: int = data.get("kills", 0)
        self.deaths: int = data.get("deaths", 0)
        self.last_mmr_change: int = int(data.get("last_match_mmr_change", 0))
        self.prev_rank_mmr: int = int(data.get("previous_rank_mmr", 0))
        self.next_rank_mmr: int = int(data.get("next_rank_mmr", 0))
        self.mmr: int = int(data.get("mmr", 0))
        self.max_mmr: int = int(data.get("max_mmr", 0))
        self.wins: int = data.get("wins", 0)
        self.losses: int = data.get("losses", 0)
        self.rank_id: int = data.get("rank")
        self.season: int = data.get("season", -1)
        _rank_definitions = _get_rank_constants(self.season)
        self.rank: str = _rank_definitions[self.rank_id]["name"]
        self.max_rank_id: int = data.get("max_rank")
        self.max_rank: str = _rank_definitions[self.max_rank_id]["name"]
        self.region: str = data.get("region")
        self.abandons: int = data.get("abandons", 0)
        self.skill_mean: float = data.get("skill_mean", 0)
        self.skill_stdev: float = data.get("skill_stdev", 0)
        self.season_name: str = seasons[self.season]["name"] or seasons[0]["name"]
        self.season_code: str = seasons[self.season]["code"] or seasons[0]["code"]

        # For casual where the API doesn't return this data
        if self.prev_rank_mmr == 0 and self.next_rank_mmr == 0:
            self.rank, self.prev_rank_mmr, self.next_rank_mmr, self.rank_id = _get_rank_from_mmr(self.mmr)
            self.max_rank_id = self.max_mmr = -1
            self.max_rank = "Undefined"

    def get_dict(self) -> dict[str: str | int | float]:
        return vars(self)
