from __future__ import annotations
from typing import Dict


class UrlBuilder:
    def __init__(self, spaceid: str, platform_url: str, player_id: str, player_uid: str, platform_group: str, spaceids: Dict[str, str]):
        self.spaceid: str = spaceid
        self.spaceids: str = spaceids
        self.xplay_spaceid: str = spaceids.get("xplay", "0d2ae42d-4c27-4cb7-af6c-2099062302bb")
        self.platform_url: str = platform_url
        self.platform_group: str = platform_group
        self.uid: str = player_uid
        self.id: str = player_id
        self.player_id: str = player_uid if self.platform_group == "PC" else player_id
        self.start_date: str = ""
        self.end_date: str = ""

    def set_timespan_dates(self, start_date: str, end_date: str) -> None:
        self.start_date = f"&startDate={start_date}"
        self.end_date = f"&endDate={end_date}"

    def linked_accounts(self) -> str:
        return f"https://public-ubiservices.ubi.com/v3/users/{self.uid}/profiles"

    def xp_lvl(self) -> str:
        return f"https://public-ubiservices.ubi.com/v1/spaces/{self.xplay_spaceid}/title/r6s/rewards/public_profile?" \
               f"profile_id={self.uid}"

    def playtime(self) -> str:
        return f"https://public-ubiservices.ubi.com/v1/profiles/stats?" \
               f"profileIds={self.uid}" \
               f"&spaceId={self.xplay_spaceid}" \
               f"&statNames=PPvPTimePlayed,PPvETimePlayed,PTotalTimePlayed,PClearanceLevel"

    def skill_records(self, seasons: str, boards: str, regions: str):
        return f"https://public-ubiservices.ubi.com/v1/spaces/{self.spaceid}/" \
               f"sandboxes/{self.platform_url}/r6karma/player_skill_records?" \
               f"board_ids={boards}" \
               f"&season_ids={seasons}" \
               f"&region_ids={regions}" \
               f"&profile_ids={self.player_id}"

    def trends(self) -> str:
        return f"https://prod.datadev.ubisoft.com/v1/profiles/{self.uid}/playerstats?" \
               f"spaceId={self.spaceid}" \
               f"&view=current" \
               f"&aggregation=movingpoint" \
               f"&trendType=daily" \
               f"&gameMode=all,ranked,casual,unranked" \
               f"&platformGroup={self.platform_group}" \
               f"&teamRole=all,attacker,defender" \
               f"{self.start_date}" \
               f"{self.end_date}"

    def weapons(self) -> str:
        return f"https://prod.datadev.ubisoft.com/v1/profiles/{self.uid}/playerstats?" \
               f"spaceId={self.xplay_spaceid}" \
               f"&view=current" \
               f"&aggregation=weapons" \
               f"&gameMode=all,ranked,casual,unranked" \
               f"&platformGroup={self.platform_group}" \
               f"&teamRole=all,attacker,defender" \
               f"{self.start_date}" \
               f"{self.end_date}"

    def operators(self) -> str:
        return f"https://prod.datadev.ubisoft.com/v1/profiles/{self.uid}/playerstats?" \
               f"spaceId={self.xplay_spaceid}" \
               f"&view=current" \
               f"&aggregation=operators" \
               f"&gameMode=all,ranked,casual,unranked" \
               f"&platformGroup={self.platform_group}" \
               f"&teamRole=all,Attacker,Defender" \
               f"{self.start_date}" \
               f"{self.end_date}"

    def maps(self) -> str:
        return f"https://prod.datadev.ubisoft.com/v1/profiles/{self.uid}/playerstats?" \
               f"spaceId={self.xplay_spaceid}" \
               f"&view=current" \
               f"&aggregation=maps" \
               f"&gameMode=all,ranked,casual,unranked" \
               f"&platformGroup={self.platform_group}" \
               f"&teamRole=all,Attacker,Defender" \
               f"{self.start_date}" \
               f"{self.end_date}"

    def seasonal_summaries(self, gamemodes: str, team_roles: str) -> str:
        return f"https://prod.datadev.ubisoft.com/v1/users/{self.uid}/playerstats?" \
               f"spaceId={self.xplay_spaceid}" \
               f"&view=seasonal" \
               f"&aggregation=summary" \
               f"&gameMode={gamemodes}" \
               f"&platformGroup={self.platform_group}" \
               f"&teamRole={team_roles}"

    def full_profiles(self) -> str:
        return f"https://public-ubiservices.ubi.com/v2/spaces/{self.xplay_spaceid}/title/r6s/skill/full_profiles?" \
               f"profile_ids={self.uid}" \
               f"&platform_families={self.platform_group.lower()}"

    def persona(self) -> str:
        return f"https://public-ubiservices.ubi.com/v1/profiles/{self.player_id}/persona?spaceId={self.xplay_spaceid}"
