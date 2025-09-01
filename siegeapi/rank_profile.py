
from .utils import season_id_to_code, get_rank_from_mmr, get_rank_constants



class FullProfile:
    def __init__(self, data):
        profile = data.get("profile", {})
        season_stats = data.get("season_statistics", {})
        match_outcomes = season_stats.get("match_outcomes", {})

        self.max_rank_id: int = profile.get("max_rank", 0)
        self.max_rank_points: int = profile.get("max_rank_points", 0)
        self.rank_id: int = profile.get("rank", 0)
        self.rank_points: int = profile.get("rank_points", 0)
        self.top_rank_position: int = profile.get("top_rank_position", 0)
        self.season_id: int = profile.get("season_id", 0)

        rank_constants = get_rank_constants(self.season_id)
        _, prev_, next_, _ = get_rank_from_mmr(self.rank_points)
        self.max_rank: str = rank_constants[self.max_rank_id].get("name", '')
        self.rank: str = rank_constants[self.rank_id].get("name", '')
        self.prev_rank_points: int = prev_
        self.next_rank_points: int = next_
        self.season_code: str = season_id_to_code(self.season_id)

        self.kills: int = season_stats.get("kills", 0)
        self.deaths: int = season_stats.get("deaths", 0)
        self.abandons: int = match_outcomes.get("abandons", 0)
        self.losses: int = match_outcomes.get("losses", 0)
        self.wins: int = match_outcomes.get("wins", 0)

    def get_dict(self) -> dict[str, str | int | float]:
        return vars(self)

    def __repr__(self) -> str:
        return str(vars(self))
    