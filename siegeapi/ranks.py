from __future__ import annotations

from .constants.seasons import seasons
from .utils import get_rank_constants, get_rank_from_mmr


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
        self.rank_id: int = data.get("rank", 0)
        self.season: int = data.get("season", -10000)
        _rank_definitions = get_rank_constants(self.season)
        self.rank: str = _rank_definitions[self.rank_id]["name"]
        self.max_rank_id: int = data.get("max_rank", 0)
        self.max_rank: str = _rank_definitions[self.max_rank_id]["name"]
        self.region: str = data.get("region", "missing")
        self.abandons: int = data.get("abandons", 0)
        self.skill_mean: float = data.get("skill_mean", 0)
        self.skill_stdev: float = data.get("skill_stdev", 0)
        self.season_name: str = seasons[self.season]["name"] or seasons[0]["name"]
        self.season_code: str = seasons[self.season]["code"] or seasons[0]["code"]

        # For casual where the API doesn't return this data
        if self.prev_rank_mmr == 0 and self.next_rank_mmr == 0:
            self.rank, self.prev_rank_mmr, self.next_rank_mmr, self.rank_id = get_rank_from_mmr(self.mmr)
            self.max_rank_id = self.max_mmr = 0
            self.max_rank = "Undefined"

    def get_dict(self) -> dict[str: str | int | float]:
        return vars(self)
