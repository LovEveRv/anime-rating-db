# Anime Rating DB
An anime database mainly collecting and analyzing ratings from several famous websites.

Home page: https://imagasaikou.cn/animeratingdb

Wiki page: https://imagasaikou.cn/animeratingdb/wiki

This website is still under development. For more details, you can check the wiki page.

## Usage

### Updater
If you want to build your own database:

```
pip3 install -r requirements.txt
python3 updater.py
```

You can use some console arguments to fit your own need:

```
usage: updater.py [-h] [--jikan JIKAN] [--jikan_use_api_pool]
                  [--jikan_api_pool JIKAN_API_POOL] [--delay DELAY]
                  [--interval INTERVAL] [--checkpoint CHECKPOINT]

optional arguments:
  -h, --help            show this help message and exit
  --jikan JIKAN         The URL of Jikan api
  --jikan_use_api_pool  Enable Jikan api pool
  --jikan_api_pool JIKAN_API_POOL
                        Jikan api url pool, use space to divide urls
  --delay DELAY         Delay seconds for requests
  --interval INTERVAL   Update interval (seconds)
  --checkpoint CHECKPOINT
                        File path to checkpoint (all.tmp.json).
```

Also, you can customize your own updater using the codes under `./fetch/` and `./analyze/`.

### ID-Mapping
If you want to use the ID-mapping:

```py
# a python example
import requests

url = 'https://raw.githubusercontent.com/LovEveRv/anime-rating-db/master/id.mapping.json'
response = requests.get(url)
mapping = response.json()
```

#### Data format

##### Root
`Dict<Int, Anime>`

##### Anime

| Field   | Type  | Nullable | Description                                              |
| :-:     | :-:   | :-:      | :-:                                                      |
| mal     | `Int` | No       | ID of [MyAnimeList](https://myanimelist.net)             |
| anidb   | `Int` | Yes      | ID of [AniDB](https://anidb.net)                         |
| anilist | `Int` | Yes      | ID of [AniList](https://anilist.co)                      |
| ann     | `Int` | Yes      | ID of [AnimeNewsNetwork](https://animenewsnetwork.com)   |
| bgm     | `Int` | Yes      | ID of [Bangumi](https://bgm.tv) (**May be wrong**)       |

## Thanks
+ [soruly/burstlink](https://github.com/soruly/burstlink)
+ [jikan-me/jikan-rest](https://github.com/jikan-me/jikan-rest)
+ [bangumi/api](https://github.com/bangumi/api)
