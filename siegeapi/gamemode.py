
class Gamemode:
    """ Contains information about a specific game queue """
    def __init__(self, name, stats=None):
        self.name = name

        if name == "ranked" or name == "casual":
            statname = f"{name}pvp_"
            stats = stats or {}
            self.won = stats.get(f"{statname}matchwon", 0)
            self.lost = stats.get(f"{statname}matchlost", 0)
            self.time_played = stats.get(f"{statname}timeplayed", 0)
            self.played = stats.get(f"{statname}matchplayed", 0)
            self.kills = stats.get(f"{statname}kills", 0)
            self.deaths = stats.get(f"{statname}death", 0)

        else:
            statname = "generalpve_"
            self.deaths = stats.get(f"{statname}death", 0)
            self.penetration_kills = stats.get(f"{statname}penetrationkills", 0)
            self.matches_won = stats.get(f"{statname}matchwon", 0)
            self.bullets_hit = stats.get(f"{statname}bullethit", 0)
            self.melee_kills = stats.get(f"{statname}meleekills", 0)
            self.bullets_fired = stats.get(f"{statname}bulletfired", 0)
            self.matches_played = stats.get(f"{statname}matchplayed", 0)
            self.kill_assists = stats.get(f"{statname}killassists", 0)
            self.time_played = stats.get(f"{statname}timeplayed", 0)
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
            self.areas_secured = stats.get(f"{statname}servershacked", 0)
            self.areas_defended = stats.get(f"{statname}serverdefender", 0)
            self.areas_contested = stats.get(f"{statname}serveraggression", 0)
            self.hostages_rescued = stats.get(f"{statname}hostagerescue", 0)
            self.hostages_defended = stats.get(f"{statname}hostagedefense", 0)
            self.blind_kills = stats.get(f"{statname}blindkills", 0)

    def get_dict(self) -> dict[str: int]:
        return vars(self)
