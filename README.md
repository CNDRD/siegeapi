<div align="center">
    <img width="250" src="https://raw.githubusercontent.com/CNDRD/siegeapi/master/assets/siegeapi-banner.png" />
    <h1>siegeapi</h1>
    <a href="https://github.com/CNDRD/siegeapi/blob/master/LICENSE">
        <img src="https://img.shields.io/github/license/CNDRD/siegeapi" />
    </a>
    <a href="https://github.com/CNDRD/siegeapi/releases">
        <img src="https://img.shields.io/github/v/release/CNDRD/siegeapi?label=latest%20release" />
    </a>
    <a href="https://pypi.org/project/siegeapi/#history">
        <img src="https://img.shields.io/pypi/v/siegeapi" />
    </a>
    <a href="https://www.python.org/downloads/">
        <img src="https://img.shields.io/pypi/pyversions/siegeapi" />
    </a>
    <a href="https://github.com/CNDRD/siegeapi">
        <img src="https://img.shields.io/github/repo-size/CNDRD/siegeapi" />
    </a>
    <br/>
    <a href="https://github.com/CNDRD/siegeapi/commits/master">
        <img src="https://img.shields.io/github/last-commit/CNDRD/siegeapi" />
    </a>
    <a href="https://github.com/CNDRD/siegeapi/commits/master">
        <img src="https://img.shields.io/github/commit-activity/m/CNDRD/siegeapi" />
    </a>
    <a href="https://pypi.org/project/siegeapi">
        <img src="https://img.shields.io/pypi/dm/siegeapi" />
    </a>
</div>

## How to install  
```commandline
pip install siegeapi
```

## Quick example  
```python
from siegeapi import Auth
import asyncio

async def sample():
    auth = Auth("UBI_EMAIL", "UBI_PASSWORD")
    player = await auth.get_player(uid="7e0f63df-a39b-44c5-8de0-d39a05926e77")

    print(f"Name: {player.name}")
    print(f"Profile pic URL: {player.profile_pic_url}")

    await player.load_playtime()
    print(f"Total Time Played: {player.total_time_played}")
    
    await player.load_progress()
    print(f"Level: {player.level}")
    print(f"Alpha pack %: {player.alpha_pack}")
    print(f"XP: {player.xp}")
    print(f"Total XP: {player.total_xp}")
    print(f"XP to level up: {player.xp_to_level_up}")

    await auth.close()

asyncio.get_event_loop().run_until_complete(sample())
# Or `asyncio.run(sample())`  
```
### Output  
```text
Name: CNDRD
Profile pic URL: https://ubisoft-avatars.akamaized.net/7e0f63df-a39b-44c5-8de0-d39a05926e77/default_256_256.png
Total Time Played: 6723492
Level: 261
Alpha pack %: 30.5
XP: 12318
Total XP: 14875818
XP to level up: 109182
```

---

## Docs
For docs visit [WIKI](https://github.com/CNDRD/siegeapi/wiki/)

### Operator Icons  
From [r6operators](https://github.com/marcopixel/r6operators) by [marcopixel](https://github.com/marcopixel)

### Type hints  
Everything is type hinted to the best of my abilities  
If there's something missing or wrong, let me know or submit a PR  
