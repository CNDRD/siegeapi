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

## How to use  
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

> **_NOTE:_** To get user XP use `player.load_level()`, then `player.total_xp`  

---  

## Some weird stuff

### `player.load_rank(region='EU', season-1)`  
Loads the players' ranked info for the latest season in the EU region  
However, the API just flat out errors out when you try to input season number that's lower than `18` (or `-7`)  
This can be seen also at their own stats website, where the last season with sensible data is Shadow Legacy  
> **_NOTE:_** I am planning on limiting the season numbers or using some other endpoint to get the missing seasons but for now be careful  

### `player.load_general()`  
`player.bullets_fired` - Hasn't been updated for a long time  
`player.distance_travelled` - Could be overflown, so if you see a funny number send a thank you letter to Ubi  

> **_NOTE:_** I want to remove all the unsupported data that Ubi sends out but for that I need to figure out which data is affected  

---  

### Type hints  
Everything is type hinted to the best of my abilities  
If there's something missing or wrong, let me know or submit a PR  
