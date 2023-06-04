from __future__ import annotations


class LinkedAccount:
    def __init__(self, data):
        self.profile_id: str = data.get("profileId", "")
        self.user_id: str = data.get("userId", "")
        self.platform_type: str = data.get("platformType", "")
        self.id_on_platform: str = data.get("idOnPlatform", "")
        self.name_on_platform: str = data.get("nameOnPlatform", "")
