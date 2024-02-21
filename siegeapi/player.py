from __future__ import annotations
from typing import Dict, List, Optional, Tuple

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

PLATFORM_URL_NAMES = {"uplay": "OSBOR_PC_LNCH_A", "psn": "OSBOR_PS4_LNCH_A", "xbl": "OSBOR_XBOXONE_LNCH_A", "xplay": "OSBOR_XPLAY_LNCH_A"}
DATE_PATTERN = re.compile(r"^((2\d)\d{2})(0[1-9]|1[012])([012]\d|3[01])$")


class Player:
    def __init__(self, auth: aiohttp.ClientSession, data: dict):

        self.id: str = data.get("profileId","")
        self.uid: str = data.get("userId","")

        self._auth: aiohttp.ClientSession = auth
        self._platform: str = data.get("platformType","")
        self._platform_url: str = PLATFORM_URL_NAMES[self._platform]
        self._spaceid: str = self._auth.spaceids[self._platform]
        self._platform_group: str = "PC" if self._platform == "uplay" else "Console"
        self._url_builder: UrlBuilder = UrlBuilder(self._spaceid, self._platform_url, self.uid, self._platform_group)

        self.profile_pic_url_146: str = f"https://ubisoft-avatars.akamaized.net/{self.uid}/default_146_146.png"
        self.profile_pic_url_256: str = f"https://ubisoft-avatars.akamaized.net/{self.uid}/default_256_256.png"
        self.profile_pic_url_500: str = f"https://ubisoft-avatars.akamaized.net/{self.uid}/default_tall.png"
        self.profile_pic_url: str = self.profile_pic_url_256
        self.linked_accounts: List[LinkedAccount] = []

        self.name: str = data.get("nameOnPlatform","")
        self.level: int = 0
        self.alpha_pack: float = 0
        self.xp: int = 0
        self.total_xp: int = 0
        self.xp_to_level_up: int = 0

        self.total_time_played: int = 0
        self.total_time_played_hours: int = 0
        self.pvp_time_played: int = 0
        self.pve_time_played: int = 0

        self.rank_skill_records: Dict[int, Dict[str, Optional[Rank]]] | Dict = {}
        self.casual_skill_records: Dict[int, Dict[str,Optional[Rank]]] | Dict = {}

        self.ranked_summary: dict = {}
        self.casual_summary: dict = {}
        self.unranked_summary: dict = {}
        self.all_summary: dict = {}

        self.unranked_profile: Optional[FullProfile] = None
        self.ranked_profile: Optional[FullProfile] = None
        self.casual_profile: Optional[FullProfile] = None
        self.warmup_profile: Optional[FullProfile] = None
        self.event_profile: Optional[FullProfile] = None

        self.weapons: Optional[Weapons] = None
        self.trends: Optional[Trends] = None
        self.operators: Optional[Operators] = None
        self.maps: Optional[Maps] = None

    def set_timespan_dates(self, start_date: str, end_date: str) -> None:
        """YYYYMMDD"""
        if not DATE_PATTERN.match(start_date):
            raise ValueError(f"Date for start_date '{start_date}' is invalid. The date format is 'YYYYMMDD'.")
        if not DATE_PATTERN.match(end_date):
            raise ValueError(f"Date for end_date '{end_date}' is invalid. The date format is 'YYYYMMDD'.")
        else:
            self._url_builder.set_timespan_dates(start_date, end_date)

    async def load_linked_accounts(self):
        data = await self._auth.get(self._url_builder.linked_accounts())
        if not isinstance(data, dict):
            raise ValueError(f"Failed to load linked accounts. Response: {data}")

        for account in data.get("profiles", []):
            self.linked_accounts.append(LinkedAccount(account))
        return self.linked_accounts

    async def load_progress(self) -> tuple[int, int]:
        data = await self._auth.get(self._url_builder.xp_lvl(), new=True)
        if not isinstance(data, dict):
            raise ValueError(f"Failed to load progress. Response: {data}")
        self.level = int(data.get("level", 0))
        self.xp = int(data.get("xp", 0))
        self.total_xp: int = get_total_xp(self.level, self.xp)
        self.xp_to_level_up: int = get_xp_to_next_lvl(self.level) - self.xp
        return self.xp, self.level

    async def load_playtime(self) -> None:
        data = await self._auth.get(self._url_builder.playtime())
        if not isinstance(data, dict):
            raise ValueError(f"Failed to load playtime. Response: {data}")

        stats = data.get("profiles", [])[0].get("stats", {})

        self.level = int(stats.get("PClearanceLevel", {}).get("value", 0))
        self.pvp_time_played = int(stats.get("PPvPTimePlayed", {}).get("value", 0))
        self.pve_time_played = int(stats.get("PPvETimePlayed", {}).get("value", 0))
        self.total_time_played = int(stats.get("PTotalTimePlayed", {}).get("value", 0))
        self.total_time_played_hours = self.total_time_played // 3600 if self.total_time_played else 0

    async def load_skill_records(self, seasons: Optional[List[int]] = None, boards: Optional[List[str]] = None, regions: Optional[List[str]] = None) -> None:
        """Can get data only for seasons 6 (Health - Y2S2) until 27 (Brutal Swarm - Y7S3) because of ranked 2.0"""
        _all_seasons = ",".join([str(s) for s in range(6, 28)])

        if seasons and not set(list(range(6, 28))).issuperset(set(seasons)):
            raise ValueError(f"Seasons can only be between 6 and 27. You gave {seasons}")

        _seasons: str = ",".join([str(s) for s in seasons]) if seasons else _all_seasons
        _boards: str = ",".join(boards) if boards else "pvp_ranked,pvp_casual"
        _regions: str = ",".join(regions) if regions else "emea,ncsa,apac,global"
        data = await self._auth.get(self._url_builder.skill_records(_seasons, _boards, _regions))

        if not isinstance(data, dict):
            raise ValueError(f"Failed to load skill records. Response: {data}")
        
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

    async def load_summaries(self, gamemodes: Optional[List[str]] = None, team_roles: Optional[List[str]] = None) -> None:
        _gamemodes: str = ",".join(gamemodes) if gamemodes else "all,ranked,unranked,casual"
        _team_roles: str = ",".join(team_roles) if team_roles else "all,Attacker,Defender"
        data = await self._auth.get(self._url_builder.seasonal_summaries(_gamemodes, _team_roles))
        if not isinstance(data, dict):
            raise ValueError(f"Failed to load summaries. Response: {data}")

        data_gamemodes = data.get('profileData',{}).get(self.uid,{}).get("platforms",{}).get(self._platform_group,{}).get("gameModes",[])

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
        resp = await self._auth.get(self._url_builder.trends())
        if isinstance(resp, dict):
            self.trends = Trends(resp)
            return self.trends
        raise ValueError(f"Failed to load trends. Response: {resp}")

    async def load_weapons(self) -> Weapons:
        resp = await self._auth.get(self._url_builder.weapons())
        if isinstance(resp, dict):
            self.weapons = Weapons(resp)
            return self.weapons
        raise ValueError(f"Failed to load weapons. Response: {resp}")

    async def load_operators(self, op_about: bool = False) -> Operators:
        resp = await self._auth.get(self._url_builder.operators())
        if isinstance(resp, dict):
            self.operators = Operators(resp, op_about)
            return self.operators
        raise ValueError(f"Failed to load operators. Response: {resp}")

    async def load_maps(self) -> Maps:
        resp = await self._auth.get(self._url_builder.maps())
        if isinstance(resp, dict):
            self.maps = Maps(resp)
            return self.maps
        raise ValueError(f"Failed to load maps. Response: {resp}")

    async def load_ranked_v2(self) -> Tuple[Optional[FullProfile], Optional[FullProfile], Optional[FullProfile], Optional[FullProfile], Optional[FullProfile]]:
        """ Returns a tuple of FullProfile objects for each profile board (unranked, ranked, casual, warmup, event) """

        data = await self._auth.get(self._url_builder.full_profiles(), new=True)
        if not isinstance(data, dict):
            raise ValueError(f"Failed to load full profiles. Response: {data}") # maybe return None instead?
        
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
