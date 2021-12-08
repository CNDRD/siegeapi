<div align="center">
    <h1>siegeapi</h1>
    <img src="https://img.shields.io/github/license/CNDRD/siegeapi" />
    <img src="https://img.shields.io/github/v/release/CNDRD/siegeapi?label=latest%20release" />
    <img src="https://img.shields.io/pypi/pyversions/siegeapi" />
    <br/>
    <img src="https://img.shields.io/github/last-commit/CNDRD/siegeapi" />
    <img src="https://img.shields.io/github/commit-activity/m/CNDRD/siegeapi" />
</div>

## How to install  
```commandline
pip install siegeapi
```

## Quick example  
```python
from siegeapi import Auth, Platforms
import asyncio

async def sample():
    auth = Auth("UBI_EMAIL", "UBI_PASSWORD")
    player = await auth.get_player(uid="7e0f63df-a39b-44c5-8de0-d39a05926e77", platform=Platforms.UPLAY)
    
    print(f"Name: {player.name}")
    print(f"Profile pic URL: {player.profile_pic_url}")
    
    await player.load_level()
    print(f"Level: {player.level}")
    print(f"Alpha pack %: {player.lootbox_probability}")
    
    await auth.close()

asyncio.get_event_loop().run_until_complete(sample())
```
### Output  
```text
Name: CNDRD
Profile pic URL: https://ubisoft-avatars.akamaized.net/7e0f63df-a39b-44c5-8de0-d39a05926e77/default_256_256.png
Level: 252
Alpha pack %: 2050
```

> **_NOTE:_** `player.lootbox_probability` is 3 or 4-digits long E.g.:  `player.lootbox_probability = 500` 👉 5.00%  

---  

# Docs  

# `Auth`  
|       Parameter       |  Type  |                       Info                       |
|:---------------------:|:------:|:------------------------------------------------:|
|         email         | string |          Ubisoft account email address           |
|       password        | string |             Ubisoft account password             |
 
### `.close()`  
Closes the [`Auth`](#auth) session  

### `.get_player(name=None, platform=None, uid=None) -> Player`  
Either `name` or `uid` must be given, but not both  
Returns one instance of [`Player`](#player) that matches either `name` or `uid`   

### `.get_player_batch(self, platform, names=None, uids=None) -> PlayerBatch:`  
Returns a [`PlayerBatch`](#playerbatch) of players' data according to the given lists of `names` and/or `uids`  

# `Player`  

### `.load_playtime() -> dict[str: int]`  
Loads the `Player.pvp_time_played`, `Player.pve_time_played` and `Player.time_played`  
_(Also returns these values)_  

### `.load_general() -> None`  
Loads these values into the [`Player`](#player) object:  

|            Stat            |          Stat          |
|:--------------------------:|:----------------------:|
|         `.deaths`          |        `.kills`        |
|      `.kill_assists`       |  `.penetration_kills`  |
|       `.matches_won`       |     `.bullets_hit`     |
|       `.melee_kills`       |   `.matches_played`    |
|         `.revives`         |      `.headshots`      |
|      `.matches_lost`       |    `.dbno_assists`     |
|        `.suicides`         | `.barricades_deployed` |
| `.reinforcements_deployed` |      `.total_xp`       |
|     `.rappel_breaches`     | `.distance_travelled`  |
|     `.revives_denied`      |        `.dbnos`        |
|    `.gadgets_destroyed`    |     `.blind_kills`     |

> **_NOTE:_** `.distance_travelled` Could be overflown, so if you see a funny number send a thank you letter to Ubi  

### `.load_gamemodes() -> None`  
Loads [`Gamemode`](#gamemode) objects into the current [`Player`](#player)  

| `Gamemode` | `Player.` |
|:----------:|:---------:|
|   Ranked   | `.ranked` |
|   Casual   | `.casual` |
|   T Hunt   | `.thunt`  |

### `.load_weapon_types() -> None`  
Loads [`Weapon`](#weapon) type stats into `Player.weapons`  

|      Weapon       |     types      |
|:-----------------:|:--------------:|
|   Assault Rifle   | Submachine Gun |
| Light Machine Gun | Marksman Rifle |
|      Handgun      |    Shotgun     |
|  Machine Pistol   |       -        |

Loads these values:  

|     attr     |         ?         |
|:------------:|:-----------------:|
|   `.kills`   |                   |
| `.headshots` |                   |
|   `.shots`   |   bullets fired   |
|   `.hits`    | bullets connected |

### `.load_all_operators() -> dict[str: Operator]`  
Loads all the available operators' statistics inside the [`Operator`](#operator) class and also returns them  
Dict keys are lowercase operator names  

### `.load_everything()`  
As the name suggests, loads everything in one call  

# Operator  
Holds general operator statistics for a given operator as well as a list of their unique ability stats

|      Stat      |      Stat       |
|:--------------:|:---------------:|
|    `.wins`     |    `.losses`    |
|    `.kills`    |    `.deaths`    |
|  `.headshots`  |    `.melees`    |
|    `.dbnos`    |      `.xp`      |
| `.time_played` |    `.atkdef`    |
|    `.icon`     | `.unique_stats` |

> **_NOTE:_** `.atkdef` & `.icon` are strings; `.unique_stats` is a dict  

# Rank  
Holds stats for the given gamemode (ranked / casual) for the given `Rank.season` and `Rank.region`  

| Stat               | Type  |     | Stat           |  Type  |
|:-------------------|:-----:|-----|:---------------|:------:|
| `.kills`           |  int  |     | `.abandons`    |  int   |
| `.deaths`          |  int  |     | `.rank_id`     |  int   |
| `.last_mmr_change` | float |     | `.rank`        | string |
| `.prev_rank_mmr`   | float |     | `.max_rank_id` |  int   |
| `.next_rank_mmr`   | float |     | `.max_rank`    | string |
| `.mmr`             |  int  |     | `.season`      |  int   |
| `.max_mmr`         |  int  |     | `.region`      | string |
| `.wins`            |  int  |     | `.skill_mean`  | float  |
| `.losses`          |  int  |     | `.skill_stdev` | float  |

# Gamemode  
Holds the following statistics for the given gamemode  
- `.won`  
- `.lost`  
- `.time_played`  
- `.played`  
- `.kills`  
- `.deaths`  

# Weapon  
Holds weapon type statistics  

|     attr     |         ?         |
|:------------:|:-----------------:|
|   `.kills`   |                   |
| `.headshots` |                   |
|   `.shots`   |   bullets fired   |
|   `.hits`    | bullets connected |

# Platforms  
Used while getting players in [`Auth`](#auth)  

`Platforms.UPLAY` is for Ubisoft Connect  
`Platforms.XBOX` is for XBOX  
`Platforms.PLAYSTATION` is for Playstation  

---  

### Type hints  
Everything is type hinted to the best of my abilities  
If there's something missing or wrong, let me know or submit a PR  
