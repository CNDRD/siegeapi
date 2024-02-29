from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Literal, Optional, Union

from urllib import parse
import aiohttp
import base64
import time
import json
import os

from .exceptions import FailedToConnect, InvalidRequest
from .player import Player

PLATFORMS = ["uplay", "xbl", "psn"]

class Auth:
    """ Holds the authentication information """

    @staticmethod
    def get_basic_token(email: str, password: str) -> str:
        return base64.b64encode(f"{email}:{password}".encode("utf-8")).decode("utf-8")

    def __init__(
            self,
            email: Optional[str] = None,
            password: Optional[str] = None,
            token: Optional[str] = None,
            appid: Optional[str] = None,
            creds_path: Optional[str] = None,
            cachetime: int = 120,
            max_connect_retries: int = 1,
            session: Optional[aiohttp.ClientSession] = None,
            refresh_session_period: int = 180
    ):
        self.session: aiohttp.ClientSession = session or aiohttp.ClientSession()
        self.max_connect_retries: int = max_connect_retries
        self.refresh_session_period: int = refresh_session_period

        if token:
            self.token: str = token 
        elif email and password:
            self.token: str = Auth.get_basic_token(email, password)
        else:
            raise ValueError("Either 'token' or ('email' and 'password') must be provided")
        
        self.creds_path: str = creds_path or f"{os.getcwd()}/creds/{self.token}.json"
        self.appid: str = appid or 'e3d5ea9e-50bd-43b7-88bf-39794f4e3d40'
        self.sessionid: str = ""
        self.key: Optional[str] = ""
        self.new_key: str = ""
        self.spaceid: str = ""
        self.spaceids: Dict[str, str] = {
            "uplay": "0d2ae42d-4c27-4cb7-af6c-2099062302bb",
            "psn": "0d2ae42d-4c27-4cb7-af6c-2099062302bb",
            "xbl": "0d2ae42d-4c27-4cb7-af6c-2099062302bb"
        }
        self.profileid: str = ""
        self.userid: str = ""
        self.expiration: str = ""
        self.new_expiration: str = ""

        self.cachetime: int = cachetime
        self.cache = {}

        self._login_cooldown: int = 0
        self._session_start: float = time.time()

    async def _find_players(self, name: Optional[str], platform: Literal["uplay", "xbl", "psn"], uid: Optional[str]) -> List[Player]:
        """ Get a list of players matching the search term on a given platform.
        Must provide either name or uid, but not both.

        Raises:
            TypeError: If neither name nor uid is provided, if both are provided, or if platform is None.
            InvalidRequest: If the returned API request  is missing the 'profiles' key.

        Returns:
            List[Player]: A list of player objects matching the search term.
        """        
        if (not name and not uid) or (name and uid):
            await self.close()
            raise TypeError("Exactly one non-empty parameter should be provided (name or uid)")

        if not platform:
            await self.close()
            raise TypeError("'platform' cannot be None")

        if platform not in PLATFORMS:
            await self.close()
            raise TypeError(f"'platform' has to be one of the following: {PLATFORMS}; Not {platform}")

        if name:
            data = await self.get(f"https://public-ubiservices.ubi.com/v3/profiles?"
                                  f"nameOnPlatform={parse.quote(name)}&platformType={parse.quote(platform)}")
        else:
            data = await self.get(f"https://public-ubiservices.ubi.com/v3/users/{uid}/profiles?"
                                  f"platformType={parse.quote(platform)}")
        
        if not isinstance(data, dict):
            await self.close()
            raise InvalidRequest(f"Expected a JSON object, got {type(data)}")

        if "profiles" in data:
            results = [Player(self, x) for x in data.get("profiles",{}) if x.get("platformType", "") == platform]
            if not results:
                await self.close()
                raise InvalidRequest("No results")
            return results
        else:
            raise InvalidRequest(f"Missing key profiles in returned JSON object {str(data)}")

    async def _ensure_session_valid(self) -> None:
        if not self.session:
            await self.refresh_session()
        elif 0 <= self.refresh_session_period <= (time.time() - self._session_start):
            await self.refresh_session()

    async def refresh_session(self) -> None:
        """ Closes the current session and opens a new one """
        if self.session:
            try:
                await self.session.close()
            except:
                pass

        self.session = aiohttp.ClientSession()
        self._session_start = time.time()

    async def get_session(self) -> aiohttp.ClientSession:
        """Retrieves the current session, ensuring it's valid first.

        Returns:
            aiohttp.ClientSession: The current session.
        """
        await self._ensure_session_valid()
        return self.session

    def save_creds(self) -> None:
        """Saves the credentials to a file."""

        if not os.path.exists(os.path.dirname(self.creds_path)):
            os.makedirs(os.path.dirname(self.creds_path))

        if not os.path.exists(self.creds_path):
            with open(self.creds_path, 'w') as f:
                json.dump({}, f)

        # write to file, overwriting the old one
        with open(self.creds_path, 'w') as f:
            json.dump({
                "sessionid": self.sessionid,
                "key": self.key,
                "new_key": self.new_key,
                "spaceid": self.spaceid,
                "profileid": self.profileid,
                "userid": self.userid,
                "expiration": self.expiration,
                "new_expiration": self.new_expiration,
            }, f, indent=4)

    def load_creds(self) -> None:
        """Loads the credentials from a file."""

        if not os.path.exists(self.creds_path):
            return

        with open(self.creds_path, "r") as f:
            data = json.load(f)

        self.sessionid = data.get("sessionid", "")
        self.key = data.get("key", "")
        self.new_key = data.get("new_key", "")
        self.spaceid = data.get("spaceid", "")
        self.profileid = data.get("profileid", "")
        self.userid = data.get("userid", "")
        self.expiration = data.get("expiration", "")
        self.new_expiration = data.get("new_expiration", "")

        self._login_cooldown = 0

    async def connect(self, _new: bool = False) -> None:
        """Connect to the Ubisoft API.
        This method will automatically called when needed."""
        self.load_creds()

        if self._login_cooldown > time.time():
            raise FailedToConnect("Login on cooldown")

        # If keys are still valid, don't connect again
        if _new:
            if self.new_key and datetime.fromisoformat(self.new_expiration[:26]+"+00:00") > datetime.now(timezone.utc):
                return
        else:
            if self.key and datetime.fromisoformat(self.expiration[:26]+"+00:00") > datetime.now(timezone.utc):
                await self.connect(_new=True)
                return

        session = await self.get_session()
        headers = {
            "User-Agent": "UbiServices_SDK_2020.Release.58_PC64_ansi_static",
            "Content-Type": "application/json; charset=UTF-8",
            "Ubi-AppId": self.appid,
            "Authorization": "Basic " + self.token
        }

        if _new:
            headers["Ubi-AppId"] = self.appid
            headers["Authorization"] = f"Ubi_v1 t={self.key}"

        resp = await session.post(
            url="https://public-ubiservices.ubi.com/v3/profiles/sessions",
            headers=headers,
            data=json.dumps({"rememberMe": True})
        )

        data = await resp.json()

        if "ticket" in data:
            if _new:
                self.new_key = data.get('ticket')
                self.new_expiration = data.get('expiration')
            else:
                self.key = data.get("ticket")
                self.expiration = data.get("expiration")
            self.profileid = data.get('profileId')
            self.sessionid = data.get("sessionId")
            self.spaceid = data.get("spaceId")
            self.userid = data.get("userId")
        else:
            message = "Unknown Error"
            if "message" in data and "httpCode" in data:
                message = f"HTTP {data['httpCode']}: {data['message']}"
            elif "message" in data:
                message = data["message"]
            elif "httpCode" in data:
                message = str(data["httpCode"])
            raise FailedToConnect(message)

        self.save_creds()
        await self.connect(_new=True)

    async def close(self) -> None:
        """Closes the session associated with the auth object. """
        self.save_creds()
        await self.session.close()

    async def get(self, *args, retries: int = 0, json_: bool = True, new: bool = False, **kwargs) -> Union[dict, str]:
        """Sends a GET request to the Ubisoft API.
        Intended for internal use only."""
        if (not self.key and not new) or (not self.new_key and new):
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

        authorization = kwargs["headers"].get("Authorization") or f"Ubi_v1 t={self.new_key if new else self.key}"
        appid = kwargs["headers"].get("Ubi-AppId") or self.appid

        kwargs["headers"]["Authorization"] = authorization
        kwargs["headers"]["Ubi-AppId"] = appid
        kwargs["headers"]["Ubi-LocaleCode"] = kwargs["headers"].get("Ubi-LocaleCode", "en-us")
        kwargs["headers"]["Ubi-SessionId"] = kwargs["headers"].get("Ubi-SessionId", self.sessionid)
        kwargs["headers"]["User-Agent"] = kwargs["headers"].get("User-Agent", "UbiServices_SDK_2020.Release.58_PC64_ansi_static")
        kwargs["headers"]["Connection"] = kwargs["headers"].get("Connection", "keep-alive")
        kwargs["headers"]["expiration"] = kwargs["headers"].get("expiration", self.expiration)

        session = await self.get_session()
        resp = await session.get(*args, **kwargs)

        if json_:
            try:
                data = await resp.json()
            except Exception:
                text = await resp.text()
                message = text.split("h1>")
                message = message[1][:-2] if len(message) > 1 else text
                raise InvalidRequest(f"Received a text response, expected JSON response. Message: {message}")

            if "httpCode" in data:
                if data["httpCode"] == 401:
                    if retries >= self.max_connect_retries:
                        # wait 30 seconds before sending another request
                        # pyright type checker doesn't like the below line
                        self._login_cooldown = 30 + time.time() # type: ignore

                    # key no longer works, so remove key and let the following .get() call refresh it
                    self.key = None
                    return await self.get(*args, retries=retries + 1, **kwargs)
                else:
                    msg = data.get("message", "")
                    if data["httpCode"] == 404:
                        msg = f"Missing resource {data.get('resource', args[0])}"
                    raise InvalidRequest(f"HTTP {data['httpCode']}: {msg}", code=data["httpCode"])
            pprint(data)
            return data
        else:
            return await resp.text()

    async def get_player(self, name: Optional[str] = None, uid: Optional[str] = None, platform: Literal["uplay", "xbl", "psn"] = "uplay") -> Player:
        """Get a player object by name or uid.
        Calls get_players and returns the first element.

        Args:
            name (Optional[str]): The username of the player. Defaults to None.
            uid (Optional[str]): The UID of the player. Defaults to None.
            platform (Literal[uplay, xbl, psn]): The playform the player plays on. Defaults to "uplay".

        Returns:
            Player: The player object.
        """
        results = await self._find_players(name=name, platform=platform, uid=uid)
        return results[0]

    async def get_player_batch(self, names: Optional[List[str]] = None, uids: Optional[List[str]] = None, platform: Literal["uplay", "xbl", "psn"] = "uplay") -> Dict[str, Player]:
        """Get a dictionary of players by name or uid.
        Note that all players must share the same provided platform.

        Args:
            name (Optional[str]): List of usernames to lookup. Defaults to None.
            uid (Optional[str]): List of UIDs to lookup. Defaults to None.
            platform (Literal[uplay, xbl, psn]): The playform the players plays on. Defaults to "uplay".

        Returns:
            Dict[str, Player]: A dictionary of player objects, with the form {uid: player}.
        """
        players = {}
        if names is not None:
            for name in names:
                player = await self.get_player(name=name, platform=platform)
                players[player.id] = player

        if uids is not None:
            for uid in uids:
                player = await self.get_player(uid=uid, platform=platform)
                players[player.id] = player
        return players
