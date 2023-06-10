<div align="center">
    <img width="250" src="https://raw.githubusercontent.com/CNDRD/siegeapi/master/assets/siegeapi-banner.png" />
    <h1>siegeapi</h1>
    <a href="https://github.com/CNDRD/siegeapi/releases">
        <img src="https://img.shields.io/github/v/release/CNDRD/siegeapi?label=latest%20release&style=for-the-badge&logo=github&logoColor=white" />
    </a>
    <a href="https://pypi.org/project/siegeapi/#history">
        <img src="https://img.shields.io/pypi/v/siegeapi?style=for-the-badge&logo=pypi&logoColor=white" />
    </a>
    <br />
    <a href="https://www.python.org/downloads/">
        <img src="https://img.shields.io/pypi/pyversions/siegeapi?style=for-the-badge&logo=python&logoColor=white&color=yellow" />
    </a>
    <a href="https://pypi.org/project/siegeapi">
        <img src="https://img.shields.io/pypi/dm/siegeapi?style=for-the-badge&logo=pypi&logoColor=white&color=yellow" />
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
    print(f"Total Time Played: {player.total_time_played:,} seconds")
    print(f"Level: {player.level}")

    await player.load_ranked_v2()
    print(f"Ranked Points: {player.ranked_profile.rank_points}")
    print(f"Rank: {player.ranked_profile.rank}")
    print(f"Max Rank Points: {player.ranked_profile.max_rank_points}")
    print(f"Max Rank: {player.ranked_profile.max_rank}")

    await player.load_progress()
    print(f"XP: {player.xp:,}")
    print(f"Total XP: {player.total_xp:,}")
    print(f"XP to level up: {player.xp_to_level_up:,}")
    
    await auth.close()

asyncio.get_event_loop().run_until_complete(sample())
# Or `asyncio.run(sample())`  
```
### Output  
```text
Name: CNDRD
Profile pic URL: https://ubisoft-avatars.akamaized.net/7e0f63df-a39b-44c5-8de0-d39a05926e77/default_256_256.png
Total Time Played: 7,910,265 seconds
Level: 285
Ranked Points: 1000
Rank: Unranked
Max Rank Points: 1000
Max Rank: Unranked
XP: 56,362
Total XP: 17,973,862
XP to level up: 77,138
```

---  

## Siege Inventory  
If you want to see every skin, headgear, uniform and more, head over to **[skins.cndrd.xyz](https://skins.cndrd.xyz/)**  

## Docs  
For docs go to [cndrd.github.io/siegeapi](https://cndrd.github.io/siegeapi/)  

## Credits  
Operator Icons from [r6operators][r6operators_] by [marcopixel][marcopixel_]  
Built (and re-built) on top of what [billy-yoyo][r6s_python_api] started  

## Problems  
If you experience any problems, reach out to me, or submit a PR  
You can reach out here on GitHub or on Discord (_cndrd_)  


![forthebadge](https://forthebadge.com/images/badges/works-on-my-machine.svg)  
![forthebadge](https://forthebadge.com/images/badges/powered-by-energy-drinks.svg)  

[r6operators_]: https://github.com/marcopixel/r6operators  
[marcopixel_]: https://github.com/marcopixel  
[r6s_python_api]: https://github.com/billy-yoyo/RainbowSixSiege-Python-API  
