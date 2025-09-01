from datetime import datetime, timezone

from aiohttp import ClientSession
from urllib import parse
import base64
import json
import os

from .exceptions import FailedToConnect, InvalidRequest
from .player import Player





class AuthData:
    def __init__(self, auth_data: dict, appid: str) -> None:
        self._data = auth_data

        self.application_id = appid
        self.platform_type = auth_data.get('platformType', None)
        self.ticket = auth_data.get('ticket', None)
        self.two_factor_authentication_ticket = auth_data.get('twoFactorAuthenticationTicket', None)
        self.profile_id = auth_data.get('profileId', None)
        self.user_id = auth_data.get('userId', None)
        self.name_on_platform = auth_data.get('nameOnPlatform', None)
        self.environment = auth_data.get('environment', None)
        self.expiration = auth_data.get('expiration', None) # 2025-05-30T18:55:04.2418966Z
        self.space_id = auth_data.get('spaceId', None)
        self.client_ip = auth_data.get('clientIp', None)
        self.client_ip_country = auth_data.get('clientIpCountry', None)
        self.server_time = auth_data.get('serverTime', None)
        self.session_id = auth_data.get('sessionId', None)
        self.session_key = auth_data.get('sessionKey', None)
        self.remember_me_ticket = auth_data.get('rememberMeTicket', None)

    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) > datetime.fromisoformat(self.expiration.replace("Z", "+00:00"))





class Auth:
    """ Holds the authentication information """

    def __init__(
        self,
        email: str,
        password: str,
        token: str | None = None,
        creds_path: str | None = None,
        session: ClientSession | None = None,
        base_appid: str | None = None,
        advanced_appid: str | None = None,
        extra_get_kwargs: dict | None = None,
        max_get_retries: int = 3
    ):
        if token:
            self._token: str = token 
        elif email and password:
            self._token: str = base64.b64encode(f"{email}:{password}".encode("utf-8")).decode("utf-8")
        else:
            raise ValueError("Either 'token' or ('email' and 'password') must be provided")

        self._base_appid: str = base_appid or "4391c956-8943-48eb-8859-07b0778f47b9"
        self._advanced_appid: str = advanced_appid or "e3d5ea9e-50bd-43b7-88bf-39794f4e3d40"

        self._extra_get_kwargs: dict = extra_get_kwargs or {}
        self._max_get_retries: int = max_get_retries
        self._session: ClientSession | None = session or None
        self._base_auth: AuthData | None = None
        self._advanced_auth: AuthData | None = None

        self._creds_path = creds_path or f"{os.getcwd()}/creds/"
        self._creds_path += '/' if not self._creds_path.endswith('/') else ''

        self._creds_path_token = f"{self._creds_path}{self._token}"
        self._base_auth_path = f"{self._creds_path_token}/{self._base_appid}.json"
        self._advanced_auth_path = f"{self._creds_path_token}/{self._advanced_appid}.json"

        self._load_auth_data_from_disk()

    def _get_session(self) -> ClientSession:
        """
        Get the aiohttp ClientSession.
        """
        if not self._session:
            self._session = ClientSession()
        return self._session

    async def close(self) -> None:
        """
        Close the aiohttp ClientSession if it exists.
        """
        if self._session:
            await self._session.close()
            self._session = None

    def _load_auth_data_from_disk(self) -> None:
        """
        Load the authentication data from the filesystem if they exist.
        """
        if not os.path.exists(self._creds_path_token):
            os.makedirs(self._creds_path_token)
            return
        
        if os.path.exists(self._base_auth_path):
            with open(self._base_auth_path, 'r') as f:
                data = json.load(f)
                self._base_auth = AuthData(data, self._base_appid)

        if os.path.exists(self._advanced_auth_path):
            with open(self._advanced_auth_path, 'r') as f:
                data = json.load(f)
                self._advanced_auth = AuthData(data, self._advanced_appid)

    async def get_auth(self, advanced: bool = False) -> AuthData:
        """
        Get authentication data.
        """
        
        if advanced and not self._base_auth:
            self._base_auth = await self.get_auth(advanced=False)

        sesh = self._get_session()
        auth_data = self._advanced_auth if advanced else self._base_auth
        appid = self._advanced_appid if advanced else self._base_appid
        authorization = f"Ubi_v1 t={self._base_auth.ticket}" if advanced else f"Basic {self._token}"

        # Check if the auth_data is already set and not expired
        if auth_data is not None or (auth_data and not auth_data.is_expired()):
            return auth_data

        # The auth_data is expired or not set, so let's get a new one
        response = await sesh.post(
            "https://public-ubiservices.ubi.com/v3/profiles/sessions",
            headers={
                "Authorization": authorization,
                "Ubi-AppId": appid,
                "User-Agent": "UbiServices_SDK_2020.Release.58_PC64_ansi_static",
                "Content-Type": "application/json"
            },
            json={
                "rememberMe": True
            }
        )

        if response.status != 200:
            raise Exception(f"Failed to authenticate: {response.status} {await response.text()}")
        
        data = await response.json()
        auth_data = AuthData(data, appid)

        if advanced:
            self._advanced_auth = auth_data
        else:
            self._base_auth = auth_data

        # We also cache the auth_data in the filesystem
        if not os.path.exists(self._creds_path):
            os.makedirs(self._creds_path)
        
        file_path = self._advanced_auth_path if advanced else self._base_auth_path

        with open(file_path, 'w') as f:
            f.write(json.dumps(auth_data._data, indent=4))
        
        return auth_data

    async def connect(self, advanced: bool = False) -> None:
        """
        Connect to the Ubisoft services
        """
        self._load_auth_data_from_disk()
        await self.get_auth(advanced=advanced)

    async def get(self, *args, advanced: bool = False, retries: int = 0, **kwargs) -> dict | str:
        if retries > self._max_get_retries:
            raise FailedToConnect("Max retries exceeded")

        await self.connect(advanced=advanced)

        kwargs.update(self._extra_get_kwargs)
        kwargs['headers'] = {} if 'headers' not in kwargs else kwargs['headers']

        auth_data = self._advanced_auth if advanced else self._base_auth

        kwargs["headers"]["Ubi-LocaleCode"] = kwargs["headers"].get("Ubi-LocaleCode", "en-us")
        kwargs["headers"]["Ubi-SessionId"] = kwargs["headers"].get("Ubi-SessionId", auth_data.session_id)
        kwargs["headers"]["User-Agent"] = kwargs["headers"].get("User-Agent", "UbiServices_SDK_2020.Release.58_PC64_ansi_static")
        kwargs["headers"]["Connection"] = kwargs["headers"].get("Connection", "keep-alive")
        kwargs["headers"]["expiration"] = kwargs["headers"].get("expiration", auth_data.expiration)

        kwargs['headers'].update({
            'Authorization': f"Ubi_v1 t={auth_data.ticket}",
            'Ubi-AppId': auth_data.application_id,
        })

        sesh = self._get_session()
        response = await sesh.get(*args, **kwargs)

        # This is maybe putting too much trust into Ubi lmao.. we'll see won't we
        if response.status == 204:
            return {}

        try:
            resp = await response.json()
            if 'error' in resp:
                raise InvalidRequest(f"Invalid request: {resp['error']['message']}")
            return resp
        except Exception:
            text = await response.text()
            if "Invalid session" in text:
                # The session is invalid, so we need to reconnect
                await self.connect(advanced=advanced)
                return await self.get(*args, advanced=advanced, retries=retries + 1, **kwargs)
            return text

    async def _search_players(self, name: str | None, uid: str | None, platform: str = 'uplay') -> list[Player]:
        if (not name and not uid) or (name and uid):
            raise TypeError("Exactly one non-empty parameter should be provided (name or uid)")

        if not platform in ['uplay', 'console']:
            raise ValueError("Platform must be either 'uplay' or 'console'")

        if name:
            data = await self.get(f"https://public-ubiservices.ubi.com/v3/profiles?nameOnPlatform={parse.quote(name)}&platformType={parse.quote(platform)}")
        else:
            data = await self.get(f"https://public-ubiservices.ubi.com/v3/users/{uid}/profiles?platformType={parse.quote(platform)}")
        
        if not isinstance(data, dict):
            raise InvalidRequest(f"Expected a JSON object, got {type(data)}")
        
        if "profiles" in data:
            results = [Player(self, x) for x in data.get("profiles", {}) if x.get("platformType", "") == platform and x.get("userId") is not None]
            if not results:
                raise InvalidRequest("No results")
            return results
        else:
            raise InvalidRequest(f"Missing key profiles in returned JSON object {str(data)}")
        
    async def get_player(self, name: str | None = None, uid: str | None = None, platform: str = 'uplay') -> Player:
        results = await self._search_players(name, uid, platform)
        if len(results) > 1:
            raise InvalidRequest(f"Multiple results found for {name or uid} on {platform}: {[p.name_on_platform for p in results]}")
        return results[0]
