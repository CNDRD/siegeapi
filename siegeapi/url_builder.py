

class UrlBuilder:
    def __init__(self, spaceid: str, platform_url: str, player_id: str):
        self.spaceid: str = spaceid
        self.platform_url: str = platform_url
        self.player_id: str = player_id
        self.start_date: str = ""
        self.end_date: str = ""

    def set_timespan_dates(self, start_date: str, end_date: str) -> None:
        self.start_date = f"&startDate={start_date}"
        self.end_date = f"&endDate={end_date}"

    def playtime(self) -> str:
        return f"https://public-ubiservices.ubi.com/v1/profiles/stats?" \
               f"profileIds={self.player_id}" \
               f"&spaceId={self.spaceid}" \
               f"&statNames=PPvPTimePlayed,PPvETimePlayed,PTotalTimePlayed"

    def level_xp_alphapack(self) -> str:
        return f"https://public-ubiservices.ubi.com/v1/spaces/{self.spaceid}/sandboxes/{self.platform_url}/r6playerprofile/" \
               f"playerprofile/progressions?profile_ids={self.player_id}"

    def skill_records(self, seasons: str, boards: str, regions: str):
        return f"https://public-ubiservices.ubi.com/v1/spaces/{self.spaceid}/" \
               f"sandboxes/{self.platform_url}/r6karma/player_skill_records?" \
               f"board_ids={boards}" \
               f"&season_ids={seasons}" \
               f"&region_ids={regions}" \
               f"&profile_ids={self.player_id}"

    def boards(self, season: int, board_id: str, region: str) -> str:
        return f"https://public-ubiservices.ubi.com/v1/spaces/{self.spaceid}/" \
               f"sandboxes/{self.platform_url}/r6karma/players?" \
               f"board_id=pvp_{board_id}" \
               f"&profile_ids={self.player_id}" \
               f"&region_id={region}" \
               f"&season_id={season}"

    def trends(self) -> str:
        return f"https://prod.datadev.ubisoft.com/v1/profiles/{self.player_id}/playerstats?" \
               f"spaceId={self.spaceid}" \
               f"&view=current" \
               f"&aggregation=movingpoint" \
               f"&trendType=daily" \
               f"&gameMode=all,ranked,casual,unranked,newcomer" \
               f"&platform=PC" \
               f"&teamRole=all,attacker,defender" \
               f"{self.start_date}" \
               f"{self.end_date}"

    def weapons(self) -> str:
        return f"https://prod.datadev.ubisoft.com/v1/profiles/{self.player_id}/playerstats?" \
               f"spaceId={self.spaceid}" \
               f"&view=current" \
               f"&aggregation=weapons" \
               f"&gameMode=all,ranked,casual,unranked,newcomer" \
               f"&platform=PC" \
               f"&teamRole=attacker,defender" \
               f"{self.start_date}" \
               f"{self.end_date}"

    def operators(self) -> str:
        return f"https://prod.datadev.ubisoft.com/v1/profiles/{self.player_id}/playerstats?" \
               f"spaceId={self.spaceid}" \
               f"&view=current" \
               f"&aggregation=operators" \
               f"&gameMode=all,ranked,casual,unranked,newcomer" \
               f"&platform=PC" \
               f"&teamRole=all,Attacker,Defender" \
               f"{self.start_date}" \
               f"{self.end_date}"

    def maps_(self) -> str:
        return f"https://r6s-stats.ubisoft.com/v1/current/maps/{self.player_id}?" \
               f"gameMode=all,ranked,casual,unranked,newcomer" \
               f"&platform=PC" \
               f"&teamRole=all,attacker,defender" \
               f"{self.start_date}" \
               f"{self.end_date}"

    def maps(self) -> str:
        return f"https://prod.datadev.ubisoft.com/v1/profiles/{self.player_id}/playerstats?" \
               f"spaceId={self.spaceid}" \
               f"&view=current" \
               f"&aggregation=maps" \
               f"&gameMode=all,ranked,casual,unranked,newcomer" \
               f"&platform=PC" \
               f"&teamRole=all,Attacker,Defender" \
               f"{self.start_date}" \
               f"{self.end_date}"
