from __future__ import annotations

from .utils import season_code_to_id, get_total_xp, get_xp_to_next_lvl
from .linked_accounts import LinkedAccount
from .rank_profile import FullProfile
from .url_builder import UrlBuilder
from .operators import Operators
from .summaries import Summary
from .weapons import Weapons
from .trends import Trends
from .ranks import Rank
from .maps import Maps

import aiohttp
import re

platform_url_names = {"uplay": "OSBOR_PC_LNCH_A", "psn": "OSBOR_PS4_LNCH_A", "xbl": "OSBOR_XBOXONE_LNCH_A", "xplay": "OSBOR_XPLAY_LNCH_A"}
date_pattern = re.compile(r"^((2\d)\d{2})(0[1-9]|1[012])([012]\d|3[01])$")


class Player:
    def __init__(self, auth: aiohttp.ClientSession(), data: dict):

        self.id: str = data.get("profileId")

        self._auth: aiohttp.ClientSession() = auth
        self._platform: str = data.get("platformType")
        self._platform_url: str = platform_url_names[self._platform]
        self._spaceid: str = self._auth.spaceids[self._platform]
        self._platform_group: str = "PC" if self._platform == "uplay" else "Console"
        self._url_builder: UrlBuilder = UrlBuilder(self._spaceid, self._platform_url, self.id, self._platform_group)

        self.profile_pic_url_146: str = f"https://ubisoft-avatars.akamaized.net/{self.id}/default_146_146.png"
        self.profile_pic_url_256: str = f"https://ubisoft-avatars.akamaized.net/{self.id}/default_256_256.png"
        self.profile_pic_url_500: str = f"https://ubisoft-avatars.akamaized.net/{self.id}/default_tall.png"
        self.profile_pic_url: str = self.profile_pic_url_256
        self.linked_accounts: list[LinkedAccount] = []

        self.name: str = data.get("nameOnPlatform")
        self.level: int = 0
        self.alpha_pack: float = 0
        self.xp: int = 0
        self.total_xp: int = 0
        self.xp_to_level_up: int = 0

        self.total_time_played: int = 0
        self.total_time_played_hours: int = 0
        self.pvp_time_played: int = 0
        self.pve_time_played: int = 0

        self.rank_skill_records: dict[int: dict[str: Rank | None]] | dict = {}
        self.casual_skill_records: dict[int: dict[str: Rank | None]] | dict = {}

        self.ranked_summary: dict = {}
        self.casual_summary: dict = {}
        self.unranked_summary: dict = {}
        self.all_summary: dict = {}

        self.unranked_profile: FullProfile | None = None
        self.ranked_profile: FullProfile | None = None
        self.casual_profile: FullProfile | None = None
        self.warmup_profile: FullProfile | None = None
        self.event_profile: FullProfile | None = None

        self.weapons: Weapons | None = None
        self.trends: Trends | None = None
        self.operators: Operators | None = None
        self.maps: Maps | None = None

    def set_timespan_dates(self, start_date: str, end_date: str) -> None:
        """YYYYMMDD"""
        if not date_pattern.match(start_date):
            raise ValueError(f"Date for start_date '{start_date}' is invalid. The date format is 'YYYYMMDD'.")
        if not date_pattern.match(end_date):
            raise ValueError(f"Date for end_date '{end_date}' is invalid. The date format is 'YYYYMMDD'.")
        else:
            self._url_builder.set_timespan_dates(start_date, end_date)

    async def load_linked_accounts(self):
        data = await self._auth.get(self._url_builder.linked_accounts())
        for account in data.get("profiles", []):
            self.linked_accounts.append(LinkedAccount(account))
        return self.linked_accounts

    async def load_progress(self) -> tuple[int, int]:
        data = await self._auth.get(self._url_builder.xp_lvl(), new=True)
        self.level = int(data.get("level", 0))
        self.xp = int(data.get("xp", 0))
        self.total_xp: int = get_total_xp(self.level, self.xp)
        self.xp_to_level_up: int = get_xp_to_next_lvl(self.level) - self.xp
        return self.xp, self.level

    async def load_playtime(self) -> None:
        data = await self._auth.get(self._url_builder.playtime())
        stats = data.get("profiles", [])[0].get("stats", {})

        self.level = int(stats.get("PClearanceLevel", {}).get("value", 0))
        self.pvp_time_played = int(stats.get("PPvPTimePlayed", {}).get("value", 0))
        self.pve_time_played = int(stats.get("PPvETimePlayed", {}).get("value", 0))
        self.total_time_played = int(stats.get("PTotalTimePlayed", {}).get("value", 0))
        self.total_time_played_hours = self.total_time_played // 3600 if self.total_time_played else 0

    async def load_skill_records(self, seasons: list[int] = None, boards: list[str] = None, regions: list[str] = None) -> None:
        """Can get data only for seasons 6 (Health - Y2S2) until 27 (Brutal Swarm - Y7S3) because of ranked 2.0"""
        _all_seasons = ",".join([str(s) for s in range(6, 28)])

        if seasons and not set(list(range(6, 28))).issuperset(set(seasons)):
            raise ValueError(f"Seasons can only be between 6 and 27. You gave {seasons}")

        seasons = ",".join([str(s) for s in seasons]) if seasons else _all_seasons
        boards = ",".join(boards) if boards else "pvp_ranked,pvp_casual"
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
                    played = (rank_obj.wins + rank_obj.losses + rank_obj.abandons) != 0

                    if board_id == "pvp_ranked":
                        self.rank_skill_records.setdefault(season_id, {})
                        self.rank_skill_records[season_id]["global"] = rank_obj if played else None
                        self.rank_skill_records[season_id][region_id] = rank_obj if played else None
                    elif board_id == "pvp_casual":
                        self.casual_skill_records.setdefault(season_id, {})
                        self.casual_skill_records[season_id][region_id] = rank_obj if played else None

    async def load_summaries(self, gamemodes: list[str] = None, team_roles: list[str] = None) -> None:
        gamemodes = ",".join(gamemodes) if gamemodes else "all,ranked,unranked,casual"
        team_roles = ",".join(team_roles) if team_roles else "all,Attacker,Defender"
        data = await self._auth.get(self._url_builder.seasonal_summaries(gamemodes, team_roles))

        data_gamemodes = data.get('profileData').get(self.id).get("platforms").get(self._platform_group).get("gameModes")

        for gamemode in data_gamemodes:
            roles = data_gamemodes[gamemode]['teamRoles']

            for role in roles:
                for season in roles[role]:
                    season_id = season_code_to_id(f"{season['seasonYear']}{season['seasonNumber']}")

                    if gamemode == "ranked":
                        self.ranked_summary.setdefault(season_id, {}).setdefault(role, {})
                        self.ranked_summary[season_id][role] = Summary(season)
                    elif gamemode == "unranked":
                        self.unranked_summary.setdefault(season_id, {}).setdefault(role, {})
                        self.unranked_summary[season_id][role] = Summary(season)
                    elif gamemode == "casual":
                        self.casual_summary.setdefault(season_id, {}).setdefault(role, {})
                        self.casual_summary[season_id][role] = Summary(season)
                    elif gamemode == "all":
                        self.all_summary.setdefault(season_id, {}).setdefault(role, {})
                        self.all_summary[season_id][role] = Summary(season)

    async def load_trends(self) -> Trends:
        self.trends = Trends(await self._auth.get(self._url_builder.trends()))
        return self.trends

    async def load_weapons(self) -> Weapons:
        self.weapons = Weapons(await self._auth.get(self._url_builder.weapons()))
        return self.weapons

    async def load_operators(self, op_about: bool = False) -> Operators:
        self.operators = Operators(await self._auth.get(self._url_builder.operators()), op_about)
        return self.operators

    async def load_maps(self) -> Maps:
        self.maps = Maps(await self._auth.get(self._url_builder.maps()))
        return self.maps

    async def load_ranked_v2(self) -> tuple[FullProfile | None, FullProfile | None, FullProfile | None, FullProfile | None, FullProfile | None]:
        """ Returns a tuple of FullProfile objects for each profile board (unranked, ranked, casual, warmup, event) """

        data = await self._auth.get(self._url_builder.full_profiles(), new=True)
        boards = data.get('platform_families_full_profiles', [])[0].get('board_ids_full_profiles', [])

        for board in boards:

            if board.get('board_id') == 'unranked':
                self.unranked_profile = FullProfile(board.get('full_profiles', [])[0])
            elif board.get('board_id') == 'ranked':
                self.ranked_profile = FullProfile(board.get('full_profiles', [])[0])
            elif board.get('board_id') == 'casual':
                self.casual_profile = FullProfile(board.get('full_profiles', [])[0])
            elif board.get('board_id') == 'warmup':
                self.warmup_profile = FullProfile(board.get('full_profiles', [])[0])
            elif board.get('board_id') == 'event':
                self.event_profile = FullProfile(board.get('full_profiles', [])[0])

        return self.unranked_profile, self.ranked_profile, self.casual_profile, self.warmup_profile, self.event_profile
