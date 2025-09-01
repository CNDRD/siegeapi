
from .rank_profile import FullProfile



class Player:
    def __init__(self, auth, data: dict):
        self._auth = auth

        self.profile_id: str = data.get('profileId', '')
        self.user_id: str = data.get('userId', '')
        self._platform: str = data.get("platformType","")
        self.name: str = data.get("nameOnPlatform", "")

        self.profile_pic_url_146: str = f"https://ubisoft-avatars.akamaized.net/{self.user_id}/default_146_146.png"
        self.profile_pic_url_256: str = f"https://ubisoft-avatars.akamaized.net/{self.user_id}/default_256_256.png"
        self.profile_pic_url_500: str = f"https://ubisoft-avatars.akamaized.net/{self.user_id}/default_tall.png"
        self.profile_pic_url: str = self.profile_pic_url_256

        self._xplay_spaceid: str = '0d2ae42d-4c27-4cb7-af6c-2099062302bb'
        self._platform_group: str = 'pc' if self._platform == 'uplay' else 'console'

        self.total_time_played: int = 0
        self.total_time_played_hours: int = 0
        self.pvp_time_played: int = 0
        self.pve_time_played: int = 0

        self.full_profiles: dict[str, FullProfile | None] = {}
    
    

    # ---------------
    #  Full Profiles

    async def load_full_profiles(self) -> None:
        url = f"https://public-ubiservices.ubi.com/v2/spaces/{self._xplay_spaceid}/title/r6s/skill/full_profiles?" \
               f"profile_ids={self.user_id}" \
               f"&platform_families={self._platform_group}"
        
        data = await self._auth.get(url, advanced=True)

        if not isinstance(data, dict):
            raise ValueError(f"Failed to load full profiles. Response: {data}")
        
        boards = data.get('platform_families_full_profiles', [])[0].get('board_ids_full_profiles', [])

        board_renames = {
            'living_game_mode': 'dual_front',
        }

        for board in boards:
            board_id = board.get('board_id')

            if board_id in board_renames:
                board_id = board_renames[board_id]
            
            full_profile = FullProfile(board.get('full_profiles', [])[0]) if board.get('full_profiles') else None
            self.full_profiles[board_id] = full_profile

    def list_full_profiles(self) -> list[str]:
        return list(self.full_profiles.keys())

    def get_full_profile(self, board_id: str) -> FullProfile | None:
        return self.full_profiles.get(board_id) if board_id in self.full_profiles else None



    # ----------
    #  Playtime

    async def load_playtime(self) -> None:
        url = f"https://public-ubiservices.ubi.com/v1/profiles/stats?" \
                f"profileIds={self.user_id}" \
                f"&spaceId={self._xplay_spaceid}" \
                f"&statNames=PPvPTimePlayed,PPvETimePlayed,PTotalTimePlayed"

        data = await self._auth.get(url)

        if not isinstance(data, dict):
            raise ValueError(f"Failed to load playtime. Response: {data}")

        stats = data.get('profiles', [])[0].get('stats', {})

        self.pvp_time_played = int(stats.get("PPvPTimePlayed", {}).get("value", 0))
        self.pve_time_played = int(stats.get("PPvETimePlayed", {}).get("value", 0))
        self.total_time_played = int(stats.get("PTotalTimePlayed", {}).get("value", 0))
        self.total_time_played_hours = self.total_time_played // 3600 if self.total_time_played else 0
