import aiohttp
import time
import json
import base64
from urllib import parse
import datetime

from .exceptions import FailedToConnect, InvalidRequest
from .player import Player, PlayerBatch


class Auth:
    """ Holds the authentication information """

    @staticmethod
    def get_basic_token(email: str, password: str) -> str:
        return base64.b64encode(f"{email}:{password}".encode("utf-8")).decode("utf-8")

    def __init__(
            self,
            email: str = None,
            password: str = None,
            token: str = None,
            appid: str = None,
            cachetime: int = 120,
            max_connect_retries: int = 1,
            session: aiohttp.ClientSession() = None,
            refresh_session_period: int = 180
    ):
        self.session: aiohttp.ClientSession() = session or aiohttp.ClientSession()
        self.max_connect_retries: int = max_connect_retries
        self.refresh_session_period: int = refresh_session_period

        self.token: str = token or Auth.get_basic_token(email, password)
        self.appid: str = appid or "39baebad-39e5-4552-8c25-2c9b919064e2"
        self.sessionid: str = ""
        self.key: str = ""
        self.uncertain_spaceid: str = ""
        self.spaceids: dict[str:str] = {
            "uplay": "5172a557-50b5-4665-b7db-e3f2e8c5041d",
            "psn": "05bfb3f7-6c21-4c42-be1f-97a33fb5cf66",
            "xbl": "98a601e5-ca91-4440-b1c5-753f601a2c90"
        }
        self.profileid: str = ""
        self.userid: str = ""

        self.cachetime: int = cachetime
        self.cache = {}

        self._login_cooldown: int = 0
        self._session_start: float = time.time()

    async def close(self) -> None:
        """ Closes the session associated with the auth object """
        await self.session.close()

    async def refresh_session(self) -> None:
        """ Closes the current session and opens a new one """
        if self.session:
            try:
                await self.session.close()
            except:
                pass

        self.session = aiohttp.ClientSession()
        self._session_start = time.time()

    async def _ensure_session_valid(self) -> None:
        if not self.session:
            await self.refresh_session()
        elif 0 <= self.refresh_session_period <= (time.time() - self._session_start):
            await self.refresh_session()

    async def get_session(self) -> aiohttp.ClientSession():
        """ Retrieves the current session, ensuring it's valid first """
        await self._ensure_session_valid()
        return self.session

    async def connect(self) -> None:
        """ Connect to Ubisoft, automatically called when needed """
        if self._login_cooldown > time.time():
            raise FailedToConnect("Login on cooldown")

        session = await self.get_session()
        resp = await session.post("https://public-ubiservices.ubi.com/v3/profiles/sessions", headers={
            "Content-Type": "application/json",
            "Ubi-AppId": self.appid,
            "Authorization": "Basic " + self.token
        }, data=json.dumps({"rememberMe": True}))

        data = await resp.json()

        if "ticket" in data:
            self.key = data.get("ticket")
            self.sessionid = data.get("sessionId")
            self.uncertain_spaceid = data.get("spaceId")
        else:
            message = "Unknown Error"
            if "message" in data and "httpCode" in data:
                message = f"HTTP {data['httpCode']}: {data['message']}"
            elif "message" in data:
                message = data["message"]
            elif "httpCode" in data:
                message = str(data["httpCode"])
            raise FailedToConnect(message)

    async def get(self, *args, retries=0, referer=None, json=True, **kwargs) -> dict | str:
        if not self.key:
            last_error = None
            for _ in range(self.max_connect_retries):
                try:
                    await self.connect()
                    break
                except FailedToConnect as e:
                    last_error = e
            else:
                # assume this error is going uncaught, so we close the session
                await self.close()

                if last_error:
                    raise last_error
                else:
                    raise FailedToConnect("Unknown Error")

        if "headers" not in kwargs:
            kwargs["headers"] = {}
        kwargs["headers"]["Authorization"] = "Ubi_v1 t=" + self.key
        kwargs["headers"]["Ubi-AppId"] = self.appid
        kwargs["headers"]["Ubi-SessionId"] = self.sessionid
        kwargs["headers"]["Connection"] = "keep-alive"
        kwargs["headers"]["expiration"] = f"{(datetime.datetime.utcnow()+datetime.timedelta(hours=2.0)).isoformat()}Z"
        kwargs["headers"]["Ubi-LocaleCode"] = "x"

        if referer is not None:
            if isinstance(referer, Player):
                referer = f"https://game-rainbow6.ubi.com/en-gb/uplay/player-statistics/{referer.id}/multiplayer"
            kwargs["headers"]["Referer"] = str(referer)

        session = await self.get_session()
        resp = await session.get(*args, **kwargs)

        if json:
            try:
                data = await resp.json()
            except:
                text = await resp.text()
                message = text.split("h1>")
                message = message[1][:-2] if len(message) > 1 else text
                raise InvalidRequest(f"Received a text response, expected JSON response. Message: {message}")

            if "httpCode" in data:
                if data["httpCode"] == 401:
                    if retries >= self.max_connect_retries:
                        # wait 30 seconds before sending another request
                        self._login_cooldown = time.time() + 30

                    # key no longer works, so remove key and let the following .get() call refresh it
                    self.key = None
                    return await self.get(*args, retries=retries + 1, **kwargs)
                else:
                    msg = data.get("message", "")
                    if data["httpCode"] == 404:
                        msg = f"Missing resource {data.get('resource', args[0])}"
                    raise InvalidRequest(f"HTTP {data['httpCode']}: {msg}", code=data["httpCode"])

            return data
        else:
            return await resp.text()

    async def get_players(self, name=None, platform=None, uid=None) -> list[Player]:
        """ Get a list of players matching the search term on a given platform """

        if name is None and uid is None:
            raise TypeError("name and uid are both None, exactly one must be given")

        if name is not None and uid is not None:
            raise TypeError("cannot search by uid and name at the same time, please give one or the other")

        if platform is None:
            raise TypeError("platform cannot be None")

        if name:
            data = await self.get(f"https://public-ubiservices.ubi.com/v3/profiles?"
                                  f"nameOnPlatform={parse.quote(name)}&platformType={parse.quote(platform)}")
        else:
            data = await self.get(f"https://public-ubiservices.ubi.com/v3/users/{uid}/profiles?"
                                  f"platformType={parse.quote(platform)}")

        if "profiles" in data:
            results = [Player(self, x) for x in data["profiles"] if x.get("platformType", "") == platform]
            if len(results) == 0:
                raise InvalidRequest("No results")
            return results
        else:
            raise InvalidRequest(f"Missing key profiles in returned JSON object {str(data)}")

    async def get_player(self, name=None, platform=None, uid=None) -> Player:
        """ Calls get_players and returns the first element """

        results = await self.get_players(name=name, platform=platform, uid=uid)
        return results[0]

    async def get_player_batch(self, platform, names=None, uids=None) -> PlayerBatch:
        players = {}
        if names is not None:
            for name in names:
                player = await self.get_player(name=name, platform=platform)
                players[player.id] = player

        if uids is not None:
            for uid in uids:
                player = await self.get_player(uid=uid, platform=platform)
                players[player.id] = player
        return PlayerBatch(players)
