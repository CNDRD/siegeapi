from .platforms import PlatformURLNames
from .exceptions import InvalidRequest
from .ranks import Rank, _get_rank_constants
from .gamemode import Gamemode
from .weapon_types import WeaponType
from .operators import Operator
from .trends import Trends, TrendBlockDuration
from .weapons import Weapons

from .constants import *
import aiohttp


class UrlBuilder:
    def __init__(self, spaceid, platform_url, player_ids):
        self.spaceid: str = spaceid
        self.platform_url: str = platform_url
        self.player_ids: list[str] = player_ids

    def fetch_statistic_url(self, statistics: list) -> str:
        return f"https://public-ubiservices.ubi.com/v1/spaces/{self.spaceid}/sandboxes/{self.platform_url}/playerstats2/statistics?" \
               f"populations={self.player_ids}&statistics={','.join(statistics)}"

    def create_level_url(self) -> str:
        return f"https://public-ubiservices.ubi.com/v1/spaces/{self.spaceid}/sandboxes/{self.platform_url}/r6playerprofile/" \
               f"playerprofile/progressions?profile_ids={self.player_ids}"

    def create_rank_url(self, region, season) -> str:
        return f"https://public-ubiservices.ubi.com/v1/spaces/{self.spaceid}/sandboxes/{self.platform_url}/r6karma/players?" \
               f"board_id=pvp_ranked&profile_ids={self.player_ids}&region_id={region}&season_id={season}"

    def create_casual_url(self, region, season) -> str:
        return f"https://public-ubiservices.ubi.com/v1/spaces/{self.spaceid}/sandboxes/{self.platform_url}/r6karma/players?" \
               f"board_id=pvp_casual&profile_ids={self.player_ids}&region_id={region}&season_id={season}"

    def create_operator_url(self, statistics: list) -> str:
        return f"https://public-ubiservices.ubi.com/v1/spaces/{self.spaceid}/sandboxes/{self.platform_url}/playerstats2/statistics?" \
               f"populations={self.player_ids}&statistics={','.join(statistics)}"

    def create_weapon_type_url(self, statistics: list) -> str:
        return f"https://public-ubiservices.ubi.com/v1/spaces/{self.spaceid}/sandboxes/{self.platform_url}/playerstats2/statistics?" \
               f"populations={self.player_ids}&statistics={','.join(statistics)}"

    def create_playtime_url(self, statistics) -> str:
        return f"https://public-ubiservices.ubi.com/v1/profiles/stats?" \
               f"profileIds={self.player_ids}&spaceId={self.spaceid}&statNames={','.join(statistics)}"

    def create_level_only_url(self) -> str:
        return f"https://public-ubiservices.ubi.com/v1/profiles/{self.player_ids}/stats/PClearanceLevel?spaceId={self.spaceid}"

    def create_trends_url(self, block_duration: TrendBlockDuration) -> str:
        return f"https://r6s-stats.ubisoft.com/v1/current/trend/{self.player_ids}?" \
               f"gameMode=all,ranked,casual,unranked&teamRole=all,attacker,defender&trendType={block_duration}"

    def create_online_status_url(self) -> str:
        return f"https://public-ubiservices.ubi.com/v1/users/onlineStatuses?UserIds={self.player_ids}"

    def create_weapons_url(self) -> str:
        return f"https://r6s-stats.ubisoft.com/v1/current/weapons/{self.player_ids}?" \
               f"gameMode=all,ranked,casual,unranked&platform=PC&teamRole=all"


class PlayerBatch:
    """ Accumulates requests for multiple players' stats in to a single request, saving time """

    def __init__(self, players):
        self.players = players
        self.player_ids = [player_id for player_id in players]
        self._player_objs = [players[player_id] for player_id in players]

        if len(players) == 0:
            raise ValueError("batch must contain at least one player")

    def __iter__(self):
        return iter(self._player_objs)

    def __getitem__(self, name):
        return self.players[name]

    def __getattr__(self, name):
        root_player = self.players[self.player_ids[0]]
        root_method = getattr(root_player, name)

        async def _proxy(*args, **kwargs):
            results = {}

            # temporarily override url builder so we get data for all players
            root_player.url_builder.player_ids = ",".join(self.player_ids)

            root_result = await root_method(*args, **kwargs)
            results[root_player.id] = root_result

            data = root_player._last_data
            kwargs["data"] = data

            for player_id in self.players:
                if player_id != root_player.id:
                    results[player_id] = await getattr(self.players[player_id], name)(*args, **kwargs)

            # reset root player url builder to default state
            root_player.url_builder.player_ids = root_player.id

            return results

        return _proxy


class Player:
    def __init__(self, auth: aiohttp.ClientSession(), data: dict):
        self.auth: aiohttp.ClientSession() = auth

        self.id: str = data.get("profileId")
        self.userid: str = data.get("userId")
        self.platform: str = data.get("platformType")
        self.platform_url: str = PlatformURLNames[self.platform]
        self.spaceid: str = self.auth.spaceids[self.platform]
        self.url_builder: UrlBuilder = UrlBuilder(self.spaceid, self.platform_url, self.id)

        self.profile_pic_url_146: str = f"https://ubisoft-avatars.akamaized.net/{self.id}/default_146_146.png"
        self.profile_pic_url_256: str = f"https://ubisoft-avatars.akamaized.net/{self.id}/default_256_256.png"
        self.profile_pic_url_500: str = f"https://ubisoft-avatars.akamaized.net/{self.id}/default_tall.png"
        self.profile_pic_url: str = self.profile_pic_url_256

        self.name: str = data.get("nameOnPlatform")
        self.level: int = 0
        self.alpha_pack: int = 0
        self.deaths: int = 0
        self.penetration_kills: int = 0
        self.matches_won: int = 0
        self.bullets_hit: int = 0
        self.melee_kills: int = 0
        self.matches_played: int = 0
        self.kill_assists: int = 0
        self.time_played: int = 0
        self.pvp_time_played: int = 0
        self.pve_time_played: int = 0
        self._not_updated_time_played: int = 0
        self.revives: int = 0
        self.kills: int = 0
        self.headshots: int = 0
        self.matches_lost: int = 0
        self.dbno_assists: int = 0
        self.suicides: int = 0
        self.barricades_deployed: int = 0
        self.reinforcements_deployed: int = 0
        self.total_xp: int = 0
        self.rappel_breaches: int = 0
        self.distance_travelled: int = 0
        self.revives_denied: int = 0
        self.dbnos: int = 0
        self.gadgets_destroyed: int = 0
        self.blind_kills: int = 0

        self.ranks: dict = {}
        self.casuals: dict = {}
        self.operators: dict = {}
        self.weapon_types: list = []
        self.weapons: Weapons | None = None

        self.casual: Gamemode | None = None
        self.ranked: Gamemode | None = None
        self.thunt: Gamemode | None = None

        self.trends: Trends | None = None

    async def load_weapons(self) -> Weapons:
        self.weapons = Weapons(await self.auth.get(self.url_builder.create_weapons_url()))
        return self.weapons

    async def _fetch_statistics(self, statistics: list) -> dict[str: str | int | float]:

        data = await self.auth.get(self.url_builder.fetch_statistic_url(statistics))

        if "results" not in data or self.id not in data["results"]:
            raise InvalidRequest(f"Missing results key in returned JSON object {str(data)}")

        data = data["results"][self.id]
        stats = {}

        for x in data:
            statistic = x.split(":")[0]
            if statistic in statistics:
                stats[statistic] = data[x]
        return stats

    async def is_currently_online(self) -> dict[str: bool | str]:
        """Checks if the user is currently in game and if the user is 'online' / 'away' / 'dnd'"""
        data = await self.auth.get(self.url_builder.create_online_status_url())
        statuses = data["onlineStatuses"][0]

        for connection in statuses["connections"]:
            if connection["applicationId"] in SIEGE_APP_IDS:
                return {"in_game": True, "status": statuses["onlineStatus"]}
        return {"in_game": False, "status": statuses["onlineStatus"]}

    async def load_general(self) -> None:
        """ Loads players' general stats """

        stats = await self._fetch_statistics(GENERAL_URL_STATS)

        statname: str = "generalpvp_"
        self.deaths = stats.get(f"{statname}death", 0)
        self.penetration_kills = stats.get(f"{statname}penetrationkills", 0)
        self.matches_won = stats.get(f"{statname}matchwon", 0)
        self.bullets_hit = stats.get(f"{statname}bullethit", 0)
        self.melee_kills = stats.get(f"{statname}meleekills", 0)
        self.matches_played = stats.get(f"{statname}matchplayed", 0)
        self.kill_assists = stats.get(f"{statname}killassists", 0)
        self._not_updated_time_played = stats.get(f"{statname}timeplayed", 0)
        self.revives = stats.get(f"{statname}revive", 0)
        self.kills = stats.get(f"{statname}kills", 0)
        self.headshots = stats.get(f"{statname}headshot", 0)
        self.matches_lost = stats.get(f"{statname}matchlost", 0)
        self.dbno_assists = stats.get(f"{statname}dbnoassists", 0)
        self.suicides = stats.get(f"{statname}suicide", 0)
        self.barricades_deployed = stats.get(f"{statname}barricadedeployed", 0)
        self.reinforcements_deployed = stats.get(f"{statname}reinforcementdeploy", 0)
        self.total_xp = stats.get(f"{statname}totalxp", 0)
        self.rappel_breaches = stats.get(f"{statname}rappelbreach", 0)
        self.distance_travelled = stats.get(f"{statname}distancetravelled", 0)
        self.revives_denied = stats.get(f"{statname}revivedenied", 0)
        self.dbnos = stats.get(f"{statname}dbno", 0)
        self.gadgets_destroyed = stats.get(f"{statname}gadgetdestroy", 0)
        self.blind_kills = stats.get(f"{statname}blindkills")

    async def load_trends(self, block_duration: TrendBlockDuration = TrendBlockDuration.WEEKLY) -> Trends:
        self.trends = Trends(await self.auth.get(self.url_builder.create_trends_url(block_duration)))
        return self.trends

    async def load_level(self) -> None:
        data = await self.auth.get(self.url_builder.create_level_only_url())
        self.level = data["stats"]["PClearanceLevel"]["value"]
        return self.level

    async def load_playtime(self) -> dict[str: int]:
        data = await self.auth.get(self.url_builder.create_playtime_url(PLAYTIME_URL_STATS))
        self.pvp_time_played = data['profiles'][0]['stats']["PPvPTimePlayed"]["value"]
        self.pve_time_played = data['profiles'][0]['stats']["PPvETimePlayed"]["value"]
        self.time_played = data['profiles'][0]['stats']["PTotalTimePlayed"]["value"]
        return self.pvp_time_played, self.pve_time_played, self.time_played

    async def load_alpha_pack(self) -> float:
        data = await self.auth.get(self.url_builder.create_level_url())

        if "player_profiles" in data and len(data["player_profiles"]) > 0:
            self.alpha_pack = data["player_profiles"][0].get("lootbox_probability", 0)
        else:
            raise InvalidRequest(f"Missing key player_profiles in returned JSON object {str(data)}")

        return self.alpha_pack

    async def load_casual(self, region='emea', season=-1, data=None) -> Rank:
        """ Loads the players' rank for this region and season """

        if not data:
            data = await self.auth.get(self.url_builder.create_casual_url(region, season))

        if season < 0:
            season = len(seasons) + season

        rank_definitions = _get_rank_constants(season)

        if "players" in data and self.id in data["players"]:
            regionkey = f"{region}:{season}"
            self.casuals[regionkey] = Rank(data["players"][self.id], rank_definitions)
            return self.casuals[regionkey]
        else:
            raise InvalidRequest(f"Missing players key in returned JSON object {str(data)}")

    async def load_rank(self, region='emea', season=-1, data=None) -> Rank:
        """ Loads the players rank for the given and season """

        if not data:
            data = await self.auth.get(self.url_builder.create_rank_url(region, season))

        if season < 0:
            season = len(seasons) + season

        rank_definitions = _get_rank_constants(season)

        if "players" in data and self.id in data["players"]:
            regionkey = f"{region}:{season}"
            self.ranks[regionkey] = Rank(data["players"][self.id], rank_definitions)
            return self.ranks[regionkey]
        else:
            raise InvalidRequest(f"Missing players key in returned JSON object {str(data)}")

    async def load_gamemodes(self) -> (Gamemode, Gamemode, Gamemode):
        """ Loads the totals for players' ranked, casual and thunt gamemodes """
        stats = await self._fetch_statistics(RANKED_CASUAL_THUNT_URL_STATS)
        self.ranked = Gamemode("ranked", stats)
        self.casual = Gamemode("casual", stats)
        self.thunt = Gamemode("terrohunt", stats)
        return self.ranked, self.casual, self.thunt

    async def load_weapon_types(self, data=None) -> None:
        """ Load the players' weapon type stats """

        if not data:
            data = await self.auth.get(self.url_builder.create_weapon_type_url(WEAPON_TYPE_STATS))

        if "results" not in data or self.id not in data["results"]:
            raise InvalidRequest(f"Missing key results in returned JSON object {str(data)}")

        data = data["results"][self.id]
        self.weapons = [WeaponType(i, data) for i in range(1, 8)]

    async def load_operators(self) -> dict[str: Operator]:
        # ask the api for all the basic stat names WITHOUT a postfix to ask for all (I assume)
        statistics = list(OPERATOR_URL_STATS)

        # also add in all the unique
        for op in operator_dict:
            for ability in operator_dict[op]["unique_stats"]:
                statistics.append(f"{ability['id']}:{operator_dict[op]['id']}:infinite")

        data = await self.auth.get(self.url_builder.create_operator_url(statistics))

        if "results" not in data or self.id not in data["results"]:
            raise InvalidRequest(f"Missing results key in returned JSON object {str(data)}")

        data = data["results"][self.id]

        processed_data = self._process_data(data, operator_dict)

        for operator_name in operator_dict:
            op = operator_dict[operator_name]
            base_data = self._process_basic_data(processed_data, op)
            unique_data = self._process_unique_data(data, op)
            self.operators[operator_name] = Operator(op["safename"], base_data, unique_data)

        return self.operators

    @staticmethod
    def _process_data(data: dict[str: int], op_dict: dict[str: dict[str: str | int | list[str] | list[dict[str: str]]]]) -> dict[str: int]:
        processed_data = {}
        for opd in op_dict:
            op = operator_dict[opd]
            for stat in data:
                stat_ed = stat.replace(":infinite", "")
                if stat_ed.endswith(op["id"]):
                    # .replace() cuz Ubi throws in a rogue ':' once in a while..
                    processed_data[f"{opd}_{stat_ed[12:-4]}".replace(':', '')] = data[stat]
        return processed_data

    @staticmethod
    def _process_basic_data(data: dict[str: int], operator: dict[str: str | int | list[str] | list[dict[str: str]]]) -> dict[str: int]:
        basic_data = {}
        for stat in data:
            if stat.startswith(operator["safename"]):
                basic_data[f"{stat[len(operator['safename']) + 1:]}"] = data[stat]
        return basic_data

    @staticmethod
    def _process_unique_data(data: dict[str: int], operator: dict[str: str | int | list[str] | list[dict[str: str]]]) -> dict[str: int]:
        unique_data = {}

        for ability in operator["unique_stats"]:
            # Currently hard-coded to only return PVP stats
            match = f"{ability['id']}:{operator['id']}:infinite"
            ab_name = ability["id"].replace("operatorpvp_", "")

            if match in data:
                unique_data[ab_name] = {"value": data[match]}
            else:
                # the stupid API just doesn't return anything if we have zero of that stat
                unique_data[ab_name] = {"value": 0}
            unique_data[ab_name]["name"] = ability["name"]

        return unique_data
