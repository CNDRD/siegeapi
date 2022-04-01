from __future__ import annotations

from .exceptions import InvalidRequest
from .utils import get_total_xp, get_xp_to_next_lvl
from .ranks import Rank
from .gamemode import Gamemodes
from .operators import Operators
from .trends import Trends, TrendBlockDuration
from .weapons import Weapons
from .maps import Maps

import aiohttp
import re

platform_url_names = {"uplay": "OSBOR_PC_LNCH_A", "psn": "OSBOR_PS4_LNCH_A", "xbl": "OSBOR_XBOXONE_LNCH_A"}
date_pattern = re.compile(r"^((2[0-9])\d{2})(0[1-9]|1[012])([012][1-9]|3[01])$")


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

        self.ranks: dict = {}
        self.casuals: dict = {}
        self.newcomers: dict = {}
        self.events: dict = {}
        self.deathmatch: dict = {}

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

    async def load_ranked(self, season: int = -1, region: str = "emea") -> Rank:
        data = await self._auth.get(self._url_builder.boards(season, "ranked", region))
        if data["players"] == {}:
            raise InvalidRequest(f"There is no such data for the given combination of season ({season}) and region ({region})")

        self.ranks[f"{region}:{season}"] = Rank(data["players"][self.id])
        return self.ranks[f"{region}:{season}"]

    async def load_casual(self, season: int = -1, region: str = "emea") -> Rank:
        data = await self._auth.get(self._url_builder.boards(season, "casual", region))
        if data["players"] == {}:
            raise InvalidRequest(f"There is no such data for the given combination of season ({season}) and region ({region})")

        self.casuals[f"{region}:{season}"] = Rank(data["players"][self.id])
        return self.casuals[f"{region}:{season}"]

    async def load_newcomer(self, season: int = -1, region: str = "emea") -> Rank:
        data = await self._auth.get(self._url_builder.boards(season, "newcomer", region))
        if data["players"] == {}:
            raise InvalidRequest(f"There is no such data for the given combination of season ({season}) and region ({region})")

        self.newcomers[f"{region}:{season}"] = Rank(data["players"][self.id])
        return self.newcomers[f"{region}:{season}"]

    async def load_events(self, season: int = -1, region: str = "emea") -> Rank:
        data = await self._auth.get(self._url_builder.boards(season, "event", region))
        if data["players"] == {}:
            raise InvalidRequest(f"There is no such data for the given combination of season ({season}) and region ({region})")

        self.events[f"{region}:{season}"] = Rank(data["players"][self.id])
        return self.events[f"{region}:{season}"]

    async def load_deathmatch(self, season: int = -1, region: str = "emea") -> Rank:
        data = await self._auth.get(self._url_builder.boards(season, "warmup", region))
        if data["players"] == {}:
            raise InvalidRequest(f"There is no such data for the given combination of season ({season}) and region ({region})")

        self.deathmatch[f"{region}:{season}"] = Rank(data["players"][self.id])
        return self.deathmatch[f"{region}:{season}"]

    async def load_trends(self, block_duration: TrendBlockDuration = TrendBlockDuration.WEEKLY) -> Trends:
        self.trends = Trends(await self._auth.get(self._url_builder.trends(block_duration)))
        return self.trends

    async def load_weapons(self) -> Weapons:
        self.weapons = Weapons(await self._auth.get(self._url_builder.weapons()))
        return self.weapons

    async def load_operators(self) -> Operators:
        self.operators = Operators(await self._auth.get(self._url_builder.operators()))
        return self.operators

    async def load_gamemodes(self) -> Gamemodes:
        self.gamemodes = Gamemodes(await self._auth.get(self._url_builder.gamemodes()))
        return self.gamemodes

    async def load_maps(self) -> Maps:
        self.maps = Maps(await self._auth.get(self._url_builder.maps()))
        return self.maps
