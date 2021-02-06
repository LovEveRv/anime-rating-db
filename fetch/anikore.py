import requests
import traceback
import time
import json
import os
import re

from tqdm import tqdm
from bs4 import BeautifulSoup


def get_all_anime_list():
    """
    Get id list of all anime, from Anime News Network.
    If anything failed, return None.

    @return: a list of strings, each string is an id.

    P.S. Anikore provides all anime list in a way called 50-on (50音). We'll parse all
         related pages to extract id list. We'll delay 10 seconds for each request.
    """

    try:
        delay = 10
        base_url = 'https://www.anikore.jp/50on'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) \
            AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15'
        }
        id_list = []
        for i in range(1, 4):
            for j in tqdm(range(1, 47)):
                url = base_url + '-' + str(i) + '-' + str(j) + '/'
                resp = requests.get(url, headers=headers)
                html = resp.text
                soup = BeautifulSoup(html, 'html.parser')
                div_list = soup.select('div.rec_list_title')[0]
                if not div_list:
                    continue
                items = div_list.select('div.rlta')
                for item in items:
                    ani_id = int(item.div.a.attrs['href'].split('/')[-1])
                    id_list.append(ani_id)
                time.sleep(delay)
        return id_list
    except Exception:
        traceback.print_exc()
        return None


def get_anime_detail(ani_id, cache=False, cache_dir='.'):
    """
    Get detail for an anime, from Anikore.
    You can enable cache to make less requests.
    If anything failed, return None.

    @param ani_id: string or int, an id.
    @param cache: boolean, enable cache.
    @param cache_dir: string, path to cache directory.
    @return: a dict, containing detailed data.

    P.S. We have to crawl and parse raw HTML to fetch date since Anikore does
         not provide API. Do not request too fast!
    """

    try:
        url = 'https://www.anikore.jp/anime/' + str(ani_id)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) \
            AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15'
        }
        cache_path = os.path.join(cache_dir, '{}.json'.format(ani_id))
        if cache and os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            resp = requests.get(url, headers=headers)
            # response in json format
            html = resp.text
            data = {'id': ani_id}
            soup = BeautifulSoup(html, 'html.parser')
            title = soup.select('section.l-animeDetailHeader')[0].select('h1')[0].text
            title = title.strip().replace('\r\n', '')
            data['title'] = title
            match_obj = re.match(r'「(.*)（(TVアニメ動画|アニメ映画|OVA)）」', title)
            if match_obj:
                data['jp_name'] = match_obj.group(1)
                data['type'] = match_obj.group(2)
            rating = soup.select('div.l-animeDetailHeader_pointAndButtonBlock_starBlock')[0]
            data['score'] = float(rating.select('strong')[0].text)
            data['votes'] = int(rating.select('a')[0].text)
            air = soup.select('ul.l-breadcrumb_flexRoot')[0].select('li')[2]
            data['year'] = int(air.a.attrs['href'].split('/')[-2])
            if cache:
                # add to cache
                with open(cache_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
        return data
    except Exception:
        traceback.print_exc()
        return None


if __name__ == '__main__':
    """
    Just for testing.
    """

    id_list = get_all_anime_list()
    with open('anikore.json', 'w', encoding='utf-8') as f:
        json.dump(id_list, f, indent=2)
    # detail = get_anime_detail(5160)
    # print(detail)
