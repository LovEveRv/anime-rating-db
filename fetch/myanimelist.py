import requests
import traceback
import time
import json
import os
import dateutil.parser

from tqdm import tqdm
from bs4 import BeautifulSoup
# from . import utils


"""
Since MyAnimeList (https://myanimelist.net) does not provide easy-to-use api,
this script is based on a third-party, unofficial api: Jikan (https://jikan.moe).

The Web API of Jikan is rate-limited strictly. But you can build your own Jikan
REST API since it's free and open-source.
"""

# by changing the following variables, you can choose the API you want to use.
# for an example, see ../pre_process.py

jikan_api_pool = []
jikan_api_idx = 0
use_api_pool = False
jikan_api = 'https://api.jikan.moe/v3'
req_delay = 4


def change_api_url():
    if use_api_pool:
        global jikan_api_idx
        jikan_api_idx = (jikan_api_idx + 1) % len(jikan_api_pool)
        jikan_api = jikan_api_pool[jikan_api_idx]
        print('Now using Jikan api: ' + jikan_api)
    print('Sleeping for 30s')
    time.sleep(30)


def parse_data(data):
    """
    Parse the data (response) to extract information.
    If anything failed, return None.

    @param data: JSON object.
    @return: dict, containing extracted information.
    """

    try:
        detail = {}
        detail['id'] = data['mal_id']
        detail['type'] = data['type']
        detail['score'] = data['score'] if 'score' in data else None
        detail['votes'] = data['scored_by'] if 'scored_by' in data else None
        detail['rank'] = data['rank'] if 'rank' in data else None
        detail['image'] = data['image_url']
        detail['air_from'] = data['aired']['from']
        detail['air_to'] = data['aired']['to']
        detail['air_status'] = data['status']
        detail['title'] = data['title']
        detail['en_name'] = data['title_english']
        if detail['en_name'] is None:
            detail['en_name'] = detail['title']
        detail['jp_name'] = data['title_japanese']
        return detail
    except Exception:
        traceback.print_exc()
        return None


def get_top_1000_id_list():
    """
    Get a list of top-1000 anime, from MyAnimeList.
    If anything failed, return None.

    @return: a list of strings (1000 items), each string is an id.

    P.S. Regretfully, I failed to find an api which provides the whole list of anime
         on MyAnimeList. But fortunately, MyAnimeList provides a list ranked by rating.
         Since this project is called "anime-rating-db", I believe it's enough to pick
         up only top-1000 anime.
    """

    try:
        api_url = jikan_api + '/top/anime/'
        # items per page: 50
        anime_list = []
        for page in tqdm(range(1, 21)):
            whole_url = api_url + str(page)
            resp = requests.get(whole_url)
            # response in json format
            data = resp.json()['top']
            anime_list.extend([item['mal_id'] for item in data])
            # api request rate-limit
            time.sleep(req_delay)
        return anime_list
    except Exception:
        traceback.print_exc()
        return None


def cache_anime_detail(mal_id, dir_path='.'):
    """
    Cache detail for an anime, from MyAnimeList.

    @param id_list: a list of strings, each string is an id.
    @param dir_path: string, path to the cache directory.
    """

    try:
        api_url = jikan_api + '/anime/' + str(mal_id)
        resp = requests.get(api_url)
        # response in json format
        data = resp.json()
        if 'error' in data and data['status'] == 403:
            # may get 403 for requesting too fast
            change_api_url()
            cache_anime_detail(mal_id)
        fpath = os.path.join(dir_path, '{}.json'.format(mal_id))
        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        traceback.print_exc()


def get_anime_detail(mal_id, cache=False, cache_dir='.'):
    """
    Get detail for an anime, from MyAnimeList.
    You can enable cache to make less requests.
    If anything failed, return None.

    @param mal_id: string or int, an id.
    @param cache: boolean, enable cache.
    @param cache_dir: string, path to cache directory.
    @return: a dict, containing detailed data.
    """

    try:
        api_url = jikan_api + '/anime/' + str(mal_id)
        cache_path = os.path.join(cache_dir, '{}.json'.format(mal_id))
        if cache and os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            resp = requests.get(api_url)
            # response in json format
            data = resp.json()
            if 'error' in data:
                if data['status'] == 403:
                    # may get 403 for requesting too fast
                    change_api_url()
                    return get_anime_detail(mal_id, cache, cache_dir)
            elif cache:
                # add to cache
                with open(cache_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
        return parse_data(data)
    except Exception:
        print('mal_id: {}'.format(mal_id))
        traceback.print_exc()
        return None


def get_external_links(mal_id, cookie):
    """
    Get external links for an anime, from MyAnimeList.
    If anything failed, return None.

    @param mal_id: string or int, an id.
    @param cookie: string, your cookie.
    @return: a list of tuple, containing links.

    P.S. External links are not provided by Jikan API, so we have to parse it from raw HTML.
         However, you must login to see external links, so cookie is needed.
    """

    try:
        url = 'https://myanimelist.net/anime/' + str(mal_id)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) \
            AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15',
            'Cookie': cookie
        }
        resp = requests.get(url, headers=headers)
        if resp.status_code == 403:
            # may get 403 for requesting too fast
            time.sleep(60)
            # retry in 1 min
            return get_external_links(mal_id)
        html = resp.text
        # parse HTML-format text
        soup = BeautifulSoup(html, 'html.parser')
        div = soup.select('div.pb16')[0]
        items = div.select('a')
        result = []
        for item in items:
            result.append((item.text ,item.attrs['href']))
        return result
    except Exception:
        traceback.print_exc()
        return None


if __name__ == '__main__':
    """
    Just for testing.
    """

    # id_list = get_top_1000_id_list()
    # detail_list = []
    # for mal_id in tqdm(id_list):
    #     detail = get_anime_detail(mal_id)
    #     detail_list.append(detail)
    #     time.sleep(4)
    # import json
    # with open('mal.json', 'w', encoding='utf-8') as f:
    #     json.dump(detail_list, f, indent=2, ensure_ascii=False)
    
    # res = search_for_anime('爆れつハンター', 'Spell Wars: Sorcerer Hunters Revenge', '1995-10-03')
    # print(res)
