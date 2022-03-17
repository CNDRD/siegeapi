from __future__ import annotations

from .exceptions import InvalidRequest
from .utils import get_total_xp, get_xp_to_next_lvl
from .ranks import Rank
from .gamemode import Gamemodes
from .operators import Operators
from .trends import Trends, TrendBlockDuration
from .weapons import Weapons
from .maps import Maps

from datetime import date
import aiohttp

PlatformURLNames = {"uplay": "OSBOR_PC_LNCH_A", "psn": "OSBOR_PS4_LNCH_A", "xbl": "OSBOR_XBOXONE_LNCH_A"}


class UrlBuilder:
    def __init__(self, spaceid: str, platform_url: str, player_id: str):
        self.spaceid: str = spaceid
        self.platform_url: str = platform_url
        self.player_id: str = player_id
        self.siege_release: str = "20151201"
        self.today: str = date.today().strftime("%Y%m%d")

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

    def trends(self, block_duration: TrendBlockDuration = TrendBlockDuration.WEEKLY, start_date: str = None, end_date: str = None) -> str:
        return f"https://r6s-stats.ubisoft.com/v1/current/trend/{self.player_id}?" \
               f"gameMode=all,ranked,casual,unranked" \
               f"&teamRole=all,attacker,defender" \
               f"&trendType={block_duration}" \
               f"&startDate={start_date or self.siege_release}" \
               f"&endDate={end_date or self.today}"

    def weapons(self, start_date: str = None, end_date: str = None) -> str:
        return f"https://r6s-stats.ubisoft.com/v1/current/weapons/{self.player_id}?" \
               f"gameMode=all,ranked,casual,unranked" \
               f"&platform=PC" \
               f"&teamRole=all" \
               f"&startDate={start_date or self.siege_release}" \
               f"&endDate={end_date or self.today}"

    def operators(self, start_date: str = None, end_date: str = None):
        return f"https://r6s-stats.ubisoft.com/v1/current/operators/{self.player_id}?" \
               f"gameMode=all,ranked,casual,unranked" \
               f"&platform=PC" \
               f"&teamRole=attacker,defender" \
               f"&startDate={start_date or self.siege_release}" \
               f"&endDate={end_date or self.today}"

    def gamemodes(self, start_date: str = None, end_date: str = None):
        return f"https://r6s-stats.ubisoft.com/v1/current/summary/{self.player_id}?" \
               f"gameMode=all,ranked,unranked,casual" \
               f"&platform=PC" \
               f"&startDate={start_date or self.siege_release}" \
               f"&endDate={end_date or self.today}"

    def maps(self, start_date: str = None, end_date: str = None):
        return f"https://r6s-stats.ubisoft.com/v1/current/maps/{self.player_id}?" \
               f"gameMode=all,ranked,casual,unranked" \
               f"&platform=PC" \
               f"&teamRole=all,attacker,defender" \
               f"&startDate={start_date or self.siege_release}" \
               f"&endDate={end_date or self.today}"


class Player:
    def __init__(self, auth: aiohttp.ClientSession(), data: dict):

        self.id: str = data.get("profileId")

        self._auth: aiohttp.ClientSession() = auth
        self._platform: str = data.get("platformType")
        self._platform_url: str = PlatformURLNames[self._platform]
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

        self.weapons: Weapons | None = None
        self.trends: Trends | None = None
        self.operators: Operators | None = None
        self.gamemodes: Gamemodes | None = None
        self.maps: Maps | None = None

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
