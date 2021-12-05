from .platforms import PlatformURLNames
from .exceptions import InvalidRequest
from .ranks import Rank, get_rank_constants
from .gamemode import Gamemode
from .weapons import Weapon
from .operators import Operator

from .constants import *
import aiohttp


class UrlBuilder:
    def __init__(self, spaceid, platform_url, player_ids):
        self.spaceid: str = spaceid
        self.platform_url: str = platform_url
        self.player_ids: list[str] = player_ids

    def fetch_statistic_url(self, statistics) -> str:
        return f"https://public-ubiservices.ubi.com/v1/spaces/{self.spaceid}/sandboxes/{self.platform_url}/playerstats2/statistics?" \
               f"populations={self.player_ids}&statistics={','.join(statistics)}"

    def load_level_url(self) -> str:
        return f"https://public-ubiservices.ubi.com/v1/spaces/{self.spaceid}/sandboxes/{self.platform_url}/r6playerprofile/" \
               f"playerprofile/progressions?profile_ids={self.player_ids}"

    def load_rank_url(self, region, season) -> str:
        return f"https://public-ubiservices.ubi.com/v1/spaces/{self.spaceid}/sandboxes/{self.platform_url}/r6karma/players?" \
               f"board_id=pvp_ranked&profile_ids={self.player_ids}&region_id={region}&season_id={season}"

    def load_casual_url(self, region, season) -> str:
        return f"https://public-ubiservices.ubi.com/v1/spaces/{self.spaceid}/sandboxes/{self.platform_url}/r6karma/players?" \
               f"board_id=pvp_casual&profile_ids={self.player_ids}&region_id={region}&season_id={season}"

    def load_operator_url(self, statistics) -> str:
        return f"https://public-ubiservices.ubi.com/v1/spaces/{self.spaceid}/sandboxes/{self.platform_url}/playerstats2/statistics?" \
               f"populations={self.player_ids}&statistics={statistics}"

    def load_weapon_type_url(self) -> str:
        return f"https://public-ubiservices.ubi.com/v1/spaces/{self.spaceid}/sandboxes/{self.platform_url}/playerstats2/statistics?" \
               f"populations={self.player_ids}&statistics=weapontypepvp_kills,weapontypepvp_headshot,weapontypepvp_bulletfired,weapontypepvp_bullethit"

    def load_playtime_url(self, statistics) -> str:
        return f"https://public-ubiservices.ubi.com/v1/profiles/stats?profileIds={self.player_ids}&spaceId={self.spaceid}&statNames={','.join(statistics)}"


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
        self._last_data = None

        self.id: str = data.get("profileId")
        self.userid: str = data.get("userId")
        self.platform: str = data.get("platformType")
        self.platform_url: str = PlatformURLNames[self.platform]

        self.spaceid: str = self.auth.spaceids[self.platform]
        self.url_builder: UrlBuilder = UrlBuilder(self.spaceid, self.platform_url, self.id)
        self.profile_pic_url: str = f"https://ubisoft-avatars.akamaized.net/{self.id}/default_256_256.png"

        self.name: str = data.get("nameOnPlatform")
        self.xp: int = 0
        self.level: int = 0
        self.lootbox_probability: int = 0
        self.deaths: int = 0
        self.penetration_kills: int = 0
        self.matches_won: int = 0
        self.bullets_hit: int = 0
        self.melee_kills: int = 0
        self.bullets_fired: int = 0
        self.matches_played: int = 0
        self.kill_assists: int = 0
        self.time_played: int = 0
        self.pvp_time_played: int = 0
        self.pve_time_played: int = 0
        self.not_updated_time_played: int = 0
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
        self.gamemodes: dict = {}
        self.weapons: list = []

        self.casual: Gamemode | None = None
        self.ranked: Gamemode | None = None
        self.thunt: Gamemode | None = None

    async def load_playtime(self) -> dict[str: int]:
        data = await self.auth.get(self.url_builder.load_playtime_url(PLAYTIME_URL_STATS))
        self.pvp_time_played = data['profiles'][0]['stats']["PPvPTimePlayed"]["value"]
        self.pve_time_played = data['profiles'][0]['stats']["PPvETimePlayed"]["value"]
        self.time_played = data['profiles'][0]['stats']["PTotalTimePlayed"]["value"]
        stats = {
            "PVPTimePlayed": self.pvp_time_played,
            "PVETimePlayed": self.pve_time_played,
            "TotalTimePlayed": self.time_played,
        }
        return stats

    async def _fetch_statistics(self, statistics: list, data=None) -> dict[str: str | int | float]:

        if not data:
            data = await self.auth.get(self.url_builder.fetch_statistic_url(statistics))
            self._last_data = data

        if "results" not in data or self.id not in data["results"]:
            raise InvalidRequest(f"Missing results key in returned JSON object {str(data)}")

        data = data["results"][self.id]
        stats = {}

        for x in data:
            statistic = x.split(":")[0]
            if statistic in statistics:
                stats[statistic] = data[x]
        return stats

    async def load_general(self) -> None:
        """ Loads players' general stats """

        stats = await self._fetch_statistics(stat_names.GENERAL_URL_STATS)

        statname: str = "generalpvp_"
        self.deaths = stats.get(f"{statname}death", 0)
        self.penetration_kills = stats.get(f"{statname}penetrationkills", 0)
        self.matches_won = stats.get(f"{statname}matchwon", 0)
        self.bullets_hit = stats.get(f"{statname}bullethit", 0)
        self.melee_kills = stats.get(f"{statname}meleekills", 0)
        self.bullets_fired = stats.get(f"{statname}bulletfired", 0)
        self.matches_played = stats.get(f"{statname}matchplayed", 0)
        self.kill_assists = stats.get(f"{statname}killassists", 0)
        self.not_updated_time_played = stats.get(f"{statname}timeplayed", 0)
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

    async def load_level(self, data=None) -> None:
        """ Load the players' XP, level & alpha pack % """

        if not data:
            data = await self.auth.get(self.url_builder.load_level_url())
            self._last_data = data

        if "player_profiles" in data and len(data["player_profiles"]) > 0:
            # self.xp = data["player_profiles"][0].get("xp", 0)
            self.level = data["player_profiles"][0].get("level", 0)
            self.lootbox_probability = data["player_profiles"][0].get("lootbox_probability", 0)
        else:
            raise InvalidRequest(f"Missing key player_profiles in returned JSON object {str(data)}")

    async def load_casual(self, region='EU', season=-1, data=None) -> Rank:
        """ Loads the players' rank for this region and season """

        if not data:
            data = await self.auth.get(self.url_builder.load_casual_url(region, season))
            self._last_data = data

        if season < 0:
            season = len(seasons) + season

        rank_definitions = get_rank_constants(season)

        if "players" in data and self.id in data["players"]:
            regionkey = f"{region}:{season}"
            self.casuals[regionkey] = Rank(data["players"][self.id], rank_definitions)
            return self.casuals[regionkey]
        else:
            raise InvalidRequest(f"Missing players key in returned JSON object {str(data)}")

    async def load_rank(self, region='EU', season=-1, data=None) -> Rank:
        """ Loads the players rank for the given and season """

        if not data:
            data = await self.auth.get(self.url_builder.load_rank_url(region, season))
            self._last_data = data

        if season < 0:
            season = len(seasons) + season

        rank_definitions = get_rank_constants(season)

        if "players" in data and self.id in data["players"]:
            regionkey = f"{region}:{season}"
            self.ranks[regionkey] = Rank(data["players"][self.id], rank_definitions)
            return self.ranks[regionkey]
        else:
            raise InvalidRequest(f"Missing players key in returned JSON object {str(data)}")

    async def _load_thunt(self) -> None:
        """ Loads the players' stats for terrorist hunt"""
        stats = await self._fetch_statistics(stat_names.THUNT_URL_STATS)

        self.thunt = Gamemode("terrohunt")

        statname = "generalpve_"
        self.thunt.deaths = stats.get(f"{statname}death", 0)
        self.thunt.penetration_kills = stats.get(f"{statname}penetrationkills", 0)
        self.thunt.matches_won = stats.get(f"{statname}matchwon", 0)
        self.thunt.bullets_hit = stats.get(f"{statname}bullethit", 0)
        self.thunt.melee_kills = stats.get(f"{statname}meleekills", 0)
        self.thunt.bullets_fired = stats.get(f"{statname}bulletfired", 0)
        self.thunt.matches_played = stats.get(f"{statname}matchplayed", 0)
        self.thunt.kill_assists = stats.get(f"{statname}killassists", 0)
        self.thunt.time_played = stats.get(f"{statname}timeplayed", 0)
        self.thunt.revives = stats.get(f"{statname}revive", 0)
        self.thunt.kills = stats.get(f"{statname}kills", 0)
        self.thunt.headshots = stats.get(f"{statname}headshot", 0)
        self.thunt.matches_lost = stats.get(f"{statname}matchlost", 0)
        self.thunt.dbno_assists = stats.get(f"{statname}dbnoassists", 0)
        self.thunt.suicides = stats.get(f"{statname}suicide", 0)
        self.thunt.barricades_deployed = stats.get(f"{statname}barricadedeployed", 0)
        self.thunt.reinforcements_deployed = stats.get(f"{statname}reinforcementdeploy", 0)
        self.thunt.total_xp = stats.get(f"{statname}totalxp", 0)
        self.thunt.rappel_breaches = stats.get(f"{statname}rappelbreach", 0)
        self.thunt.distance_travelled = stats.get(f"{statname}distancetravelled", 0)
        self.thunt.revives_denied = stats.get(f"{statname}revivedenied", 0)
        self.thunt.dbnos = stats.get(f"{statname}dbno", 0)
        self.thunt.gadgets_destroyed = stats.get(f"{statname}gadgetdestroy", 0)
        self.thunt.areas_secured = stats.get(f"{statname}servershacked", 0)
        self.thunt.areas_defended = stats.get(f"{statname}serverdefender", 0)
        self.thunt.areas_contested = stats.get(f"{statname}serveraggression", 0)
        self.thunt.hostages_rescued = stats.get(f"{statname}hostagerescue", 0)
        self.thunt.hostages_defended = stats.get(f"{statname}hostagedefense", 0)
        self.thunt.blind_kills = stats.get(f"{statname}blindkills", 0)

    async def load_gamemodes(self) -> None:
        """ Loads the totals for players' ranked, casual and thunt gamemodes """
        stats = await self._fetch_statistics(stat_names.RANKED_CASUAL_URL_STATS)

        self.ranked = Gamemode("ranked", stats)
        self.casual = Gamemode("casual", stats)
        await self._load_thunt()

    async def load_weapon_types(self, data=None) -> None:
        """ Load the players' weapon type stats """

        if not data:
            data = await self.auth.get(self.url_builder.load_weapon_type_url())
            self._last_data = data

        if "results" not in data or self.id not in data["results"]:
            raise InvalidRequest(f"Missing key results in returned JSON object {str(data)}")

        data = data["results"][self.id]
        self.weapons = [Weapon(i, data) for i in range(1, 8)]

    async def load_all_operators(self) -> dict[str: Operator]:
        # ask the api for all the basic stat names WITHOUT a postfix to ask for all (I assume)
        statistics = list(OPERATOR_URL_STATS)

        # also add in all the unique
        for op in operator_dict:
            for ability in operator_dict[op]["unique_stats"]:
                statistics.append(f"{ability['id']}:{operator_dict[op]['id']}:infinite")

        statistics = ",".join(statistics)

        data = await self.auth.get(self.url_builder.load_operator_url(statistics))

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

    async def load_everything(self) -> tuple[Rank, Rank, dict[str: Operator]]:
        await self.load_playtime()
        await self.load_general()
        await self.load_level()
        casual = await self.load_casual()
        rank = await self.load_rank()
        await self.load_gamemodes()
        await self.load_weapon_types()
        all_operators = await self.load_all_operators()
        return casual, rank, all_operators
