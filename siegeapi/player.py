from __future__ import annotations

from .exceptions import InvalidRequest, InvalidAttributeCombination
from .utils import get_total_xp, get_xp_to_next_lvl
from .ranks import Rank
from .gamemode import Gamemodes
from .operators import Operators
from .trends import Trends, TrendBlockDuration
from .weapons import Weapons
from .maps import Maps
from .constants import seasons as seasons_const

import aiohttp
import re

platform_url_names = {"uplay": "OSBOR_PC_LNCH_A", "psn": "OSBOR_PS4_LNCH_A", "xbl": "OSBOR_XBOXONE_LNCH_A"}
date_pattern = re.compile(r"^((2[0-9])\d{2})(0[1-9]|1[012])([012][0-9]|3[01])$")


class UrlBuilder:
    def __init__(self, spaceid: str, platform_url: str, player_id: str):
        self.spaceid: str = spaceid
        self.platform_url: str = platform_url
        self.player_id: str = player_id
        self.start_date: str = ""
        self.end_date: str = ""

    def set_timespan_dates(self, start_date: str, end_date: str) -> None:
        self.start_date = f"&startDate={start_date}"
        self.end_date = f"&endDate={end_date}"

    def playtime(self) -> str:
        return f"https://public-ubiservices.ubi.com/v1/profiles/stats?" \
               f"profileIds={self.player_id}" \
               f"&spaceId={self.spaceid}" \
               f"&statNames=PPvPTimePlayed,PPvETimePlayed,PTotalTimePlayed"

    def level_xp_alphapack(self) -> str:
        return f"https://public-ubiservices.ubi.com/v1/spaces/{self.spaceid}/sandboxes/{self.platform_url}/r6playerprofile/" \
               f"playerprofile/progressions?profile_ids={self.player_id}"

    def boards(self, season: int, board_id: str, region: str) -> str:
        return f"https://public-ubiservices.ubi.com/v1/spaces/{self.spaceid}/" \
               f"sandboxes/{self.platform_url}/r6karma/players?" \
               f"board_id=pvp_{board_id}" \
               f"&profile_ids={self.player_id}" \
               f"&region_id={region}" \
               f"&season_id={season}"

    def trends(self, block_duration: TrendBlockDuration = TrendBlockDuration.WEEKLY) -> str:
        return f"https://r6s-stats.ubisoft.com/v1/current/trend/{self.player_id}?" \
               f"gameMode=all,ranked,casual,unranked,newcomer" \
               f"&teamRole=all,attacker,defender" \
               f"&trendType={block_duration}" \
               f"{self.start_date}" \
               f"{self.end_date}"

    def weapons(self) -> str:
        return f"https://r6s-stats.ubisoft.com/v1/current/weapons/{self.player_id}?" \
               f"gameMode=all,ranked,casual,unranked,newcomer" \
               f"&platform=PC" \
               f"&teamRole=all" \
               f"{self.start_date}" \
               f"{self.end_date}"

    def operators(self) -> str:
        return f"https://r6s-stats.ubisoft.com/v1/current/operators/{self.player_id}?" \
               f"gameMode=all,ranked,casual,unranked,newcomer" \
               f"&platform=PC" \
               f"&teamRole=attacker,defender" \
               f"{self.start_date}" \
               f"{self.end_date}"

    def gamemodes(self) -> str:
        return f"https://r6s-stats.ubisoft.com/v1/current/summary/{self.player_id}?" \
               f"gameMode=all,ranked,unranked,casual,newcomer" \
               f"&platform=PC" \
               f"{self.start_date}" \
               f"{self.end_date}"

    def maps(self) -> str:
        return f"https://r6s-stats.ubisoft.com/v1/current/maps/{self.player_id}?" \
               f"gameMode=all,ranked,casual,unranked,newcomer" \
               f"&platform=PC" \
               f"&teamRole=all,attacker,defender" \
               f"{self.start_date}" \
               f"{self.end_date}"

    def skill_records(self, seasons: str, boards: str, regions: str):
        return f"https://public-ubiservices.ubi.com/v1/spaces/{self.spaceid}/" \
               f"sandboxes/{self.platform_url}/r6karma/player_skill_records?" \
               f"board_ids={boards}" \
               f"&season_ids={seasons}" \
               f"&region_ids={regions}" \
               f"&profile_ids={self.player_id}"


class Player:
    def __init__(self, auth: aiohttp.ClientSession(), data: dict):

        self.id: str = data.get("profileId")

        self._auth: aiohttp.ClientSession() = auth
        self._platform: str = data.get("platformType")
        self._platform_url: str = platform_url_names[self._platform]
        self._spaceid: str = self._auth.spaceids[self._platform]
        self._url_builder: UrlBuilder = UrlBuilder(self._spaceid, self._platform_url, self.id)

        self.profile_pic_url_146: str = f"https://ubisoft-avatars.akamaized.net/{self.id}/default_146_146.png"
        self.profile_pic_url_256: str = f"https://ubisoft-avatars.akamaized.net/{self.id}/default_256_256.png"
        self.profile_pic_url_500: str = f"https://ubisoft-avatars.akamaized.net/{self.id}/default_tall.png"
        self.profile_pic_url: str = self.profile_pic_url_256

        self.name: str = data.get("nameOnPlatform")
        self.level: int = 0
        self.alpha_pack: float = 0
        self.xp: int = 0
        self.total_xp: int = 0
        self.xp_to_level_up: int = 0

        self.total_time_played: int = 0
        self.pvp_time_played: int = 0
        self.pve_time_played: int = 0

        self.ranks: dict[int: dict[str: Rank | None]] | dict = {}
        self.casuals: dict[int: dict[str: Rank | None]] | dict = {}
        self.newcomers: dict[int: dict[str: Rank | None]] | dict = {}
        self.events: dict[int: dict[str: Rank | None]] | dict = {}
        self.deathmatch: dict[int: dict[str: Rank | None]] | dict = {}

        self.weapons: Weapons | None = None
        self.trends: Trends | None = None
        self.operators: Operators | None = None
        self.gamemodes: Gamemodes | None = None
        self.maps: Maps | None = None

    def set_timespan_dates(self, start_date: str, end_date: str) -> None:
        if not date_pattern.match(start_date):
            raise ValueError(f"Date for start_date '{start_date}' is invalid. The date format is 'YYYYMMDD'.")
        if not date_pattern.match(end_date):
            raise ValueError(f"Date for end_date '{end_date}' is invalid. The date format is 'YYYYMMDD'.")
        else:
            self._url_builder.set_timespan_dates(start_date, end_date)

    async def load_playtime(self) -> None:
        data = await self._auth.get(self._url_builder.playtime())
        stats = data.get("profiles", [])[0].get("stats", {})

        self.pvp_time_played = int(stats.get("PPvPTimePlayed", {}).get("value", 0))
        self.pve_time_played = int(stats.get("PPvETimePlayed", {}).get("value", 0))
        self.total_time_played = int(stats.get("PTotalTimePlayed", {}).get("value", 0))

    async def load_progress(self) -> None:
        data = await self._auth.get(self._url_builder.level_xp_alphapack())

        self.alpha_pack = int(data.get("player_profiles", [])[0].get("lootbox_probability", 0)) / 100
        self.level = int(data.get("player_profiles", [])[0].get("level", 0))
        self.xp = int(data.get("player_profiles", [])[0].get("xp", 0))
        self.total_xp: int = get_total_xp(self.level, self.xp)
        self.xp_to_level_up: int = get_xp_to_next_lvl(self.level) - self.xp

    async def load_skill_records(self, seasons: list[int] = None, boards: list[str] = None, regions: list[str] = None) -> None:
        _all_seasons = ",".join([str(s) for s in range(6, list(seasons_const)[-1])])

        seasons = ",".join([str(s) for s in seasons]) if seasons else _all_seasons
        boards = ",".join(boards) if boards else "pvp_ranked,pvp_casual,pvp_newcomer,pvp_warmup"
        regions = ",".join(regions) if regions else "emea,ncsa,apac,global"
        data = await self._auth.get(self._url_builder.skill_records(seasons, boards, regions))

        for season in data["seasons_player_skill_records"]:
            season_id = season["season_id"]

            for region in season["regions_player_skill_records"]:
                region_id = region["region_id"]

                for board in region["boards_player_skill_records"]:
                    board_id = board["board_id"]
                    rank_obj = Rank(board["players_skill_records"][0]) if board["players_skill_records"] else Rank({})

                    # If user didn't play in this season and region
                    played = (rank_obj.wins + rank_obj.losses) != 0

                    if board_id == "pvp_ranked":
                        self.ranks.setdefault(season_id, {})
                        self.ranks[season_id]["global"] = rank_obj if played else None
                        self.ranks[season_id][region_id] = rank_obj if played else None
                    elif board_id == "pvp_casual":
                        self.casuals.setdefault(season_id, {})
                        self.casuals[season_id][region_id] = rank_obj if played else None
                    elif board_id == "pvp_newcomer":
                        self.newcomers.setdefault(season_id, {})
                        self.newcomers[season_id][region_id] = rank_obj if played else None
                    elif board_id == "pvp_event":
                        self.events.setdefault(season_id, {})
                        self.events[season_id][region_id] = rank_obj if played else None
                    else:
                        self.deathmatch.setdefault(season_id, {})
                        self.deathmatch[season_id][region_id] = rank_obj if played else None

    async def load_ranked(self, season: int = -1, region: str = "emea") -> Rank:
        if season <= 17 and region == "global":
            raise InvalidAttributeCombination("Season ID must be greater or equal to 18 when checking the 'global' region")

        # Check if we already have this combo loaded
        if self.ranks.get(season, {}).get(region):
            return self.ranks[season][region]

        data = await self._auth.get(self._url_builder.skill_records(str(season), "pvp_ranked", region))
        season_id = data["seasons_player_skill_records"][0]["season_id"]
        data = data["seasons_player_skill_records"][0]["regions_player_skill_records"][0]["boards_player_skill_records"][0]["players_skill_records"]
        rank_obj = Rank(data[0]) if data else Rank({})

        self.ranks.setdefault(season_id, {})
        self.ranks[season_id][region] = rank_obj
        return self.ranks[season_id][region]

    async def load_casual(self, season: int = -1, region: str = "emea") -> Rank:
        if season <= 17 and region == "global":
            raise InvalidAttributeCombination("Season ID must be greater or equal to 18 when checking the 'global' region")

        # Check if we already have this combo loaded
        if self.ranks.get(season, {}).get(region):
            return self.ranks[season][region]

        data = await self._auth.get(self._url_builder.skill_records(str(season), "pvp_casual", region))
        season_id = data["seasons_player_skill_records"][0]["season_id"]
        data = data["seasons_player_skill_records"][0]["regions_player_skill_records"][0]["boards_player_skill_records"][0]["players_skill_records"]
        rank_obj = Rank(data[0]) if data else Rank({})

        self.casuals.setdefault(season_id, {})
        self.casuals[season_id][region] = rank_obj
        return self.casuals[season_id][region]

    async def load_newcomer(self, season: int = -1, region: str = "emea") -> Rank:
        if season <= 17 and region == "global":
            raise InvalidAttributeCombination("Season ID must be greater or equal to 18 when checking the 'global' region")

        # Check if we already have this combo loaded
        if self.ranks.get(season, {}).get(region):
            return self.ranks[season][region]

        data = await self._auth.get(self._url_builder.skill_records(str(season), "pvp_newcomer", region))
        season_id = data["seasons_player_skill_records"][0]["season_id"]
        data = data["seasons_player_skill_records"][0]["regions_player_skill_records"][0]["boards_player_skill_records"][0]["players_skill_records"]
        rank_obj = Rank(data[0]) if data else Rank({})

        self.newcomers.setdefault(season_id, {})
        self.newcomers[season_id][region] = rank_obj
        return self.newcomers[season_id][region]

    async def load_events(self, season: int = -1, region: str = "emea") -> Rank:
        if season <= 17 and region == "global":
            raise InvalidAttributeCombination("Season ID must be greater or equal to 18 when checking the 'global' region")

        # Check if we already have this combo loaded
        if self.ranks.get(season, {}).get(region):
            return self.ranks[season][region]

        data = await self._auth.get(self._url_builder.skill_records(str(season), "pvp_event", region))
        season_id = data["seasons_player_skill_records"][0]["season_id"]
        data = data["seasons_player_skill_records"][0]["regions_player_skill_records"][0]["boards_player_skill_records"][0]["players_skill_records"]
        rank_obj = Rank(data[0]) if data else Rank({})

        self.events.setdefault(season_id, {})
        self.events[season_id][region] = rank_obj
        return self.events[season_id][region]

    async def load_deathmatch(self, season: int = -1, region: str = "emea") -> Rank:
        if season <= 17 and region == "global":
            raise InvalidAttributeCombination("Season ID must be greater or equal to 18 when checking the 'global' region")

        # Check if we already have this combo loaded
        if self.ranks.get(season, {}).get(region):
            return self.ranks[season][region]

        data = await self._auth.get(self._url_builder.skill_records(str(season), "pvp_warmup", region))
        season_id = data["seasons_player_skill_records"][0]["season_id"]
        data = data["seasons_player_skill_records"][0]["regions_player_skill_records"][0]["boards_player_skill_records"][0]["players_skill_records"]
        rank_obj = Rank(data[0]) if data else Rank({})

        self.deathmatch.setdefault(season_id, {})
        self.deathmatch[season_id][region] = rank_obj
        return self.deathmatch[season_id][region]

    async def load_trends(self, block_duration: TrendBlockDuration = TrendBlockDuration.WEEKLY) -> Trends:
        self.trends = Trends(await self._auth.get(self._url_builder.trends(block_duration)))
        return self.trends

    async def load_weapons(self) -> Weapons:
        self.weapons = Weapons(await self._auth.get(self._url_builder.weapons()))
        return self.weapons

    async def load_operators(self, op_about: bool = False) -> Operators:
        self.operators = Operators(await self._auth.get(self._url_builder.operators()), op_about)
        return self.operators

    async def load_gamemodes(self) -> Gamemodes:
        self.gamemodes = Gamemodes(await self._auth.get(self._url_builder.gamemodes()))
        return self.gamemodes

    async def load_maps(self) -> Maps:
        self.maps = Maps(await self._auth.get(self._url_builder.maps()))
        return self.maps
