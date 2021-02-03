import json
import time
import os
import shutil
import argparse

from tqdm import tqdm
from fetch import anime_news_network, myanimelist, bangumi, anilist
from analyze import adjust, bayesian


MAL_DIR = 'fetch/mal'
BGM_DIR = 'fetch/bgm'
ANN_DIR = 'fetch/ann'
ANL_DIR = 'fetch/anilist'


def clear_cache():
    """
    Clear local cache files.
    """

    if os.path.exists(MAL_DIR):
        shutil.rmtree(MAL_DIR)
    if os.path.exists(BGM_DIR):
        shutil.rmtree(BGM_DIR)
    if os.path.exists(ANN_DIR):
        shutil.rmtree(ANN_DIR)
    if os.path.exists(ANL_DIR):
        shutil.rmtree(ANL_DIR)
    os.mkdir(MAL_DIR)
    os.mkdir(BGM_DIR)
    os.mkdir(ANN_DIR)
    os.mkdir(ANL_DIR)


def update_once(args, save_method, pre_data={}):
    """
    Update the data once.

    @param args: some args to be passed, as defined in arg_parser.
    @param save_method: a function, used for saving data to file/sql/oss.
    @param pre_data: a dict, loaded from tmp file.
    """

    with open('id.mapping.json', 'r', encoding='utf-8') as f:
        mapping = json.load(f)

    allow_types = set(('TV', 'Movie', 'OVA'))
    
    # fetch data
    all_data = pre_data
    for uid, item in tqdm(mapping.items()):
        if uid in all_data:
            continue
        
        assert item['mal'] is not None
        mal_res = myanimelist.get_anime_detail(item['mal'], True, MAL_DIR)
        if mal_res is None or mal_res['type'] not in allow_types:
            time.sleep(args.delay)
            continue
        
        if item['ann'] is not None:
            ann_res = anime_news_network.get_anime_detail(item['ann'], True, ANN_DIR)
        else:
            ann_res = None
        if item['bgm'] is not None:
            bgm_res = bangumi.get_anime_detail(item['bgm'], True, BGM_DIR)
        else:
            bgm_res = None
        if item['anilist'] is not None:
            anl_res = anilist.get_anime_detail(item['anilist'], True, ANL_DIR)
        else:
            anl_res = None
        
        all_data[uid] = {
            'MAL': mal_res,
            'ANN': ann_res,
            'BGM': bgm_res,
            'AniList': anl_res,
        }
        # save to tmp file
        with open('all.tmp.json', 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)
        # request delay
        time.sleep(args.delay)
    
    # re-calculate the scores
    ids, ratings = [], []
    for uid, item in all_data.items():
        bgm = item['BGM']
        if bgm is not None and bgm['rating_detail'] is not None:
            ids.append(uid)
            rating_detail = list(bgm['rating_detail'].values())
            rating_detail.reverse()
            ratings.append(rating_detail)
    scores = bayesian.calc_bayesian_score(ratings, 10)
    for uid, score in zip(ids, scores):
        all_data[uid]['BGM']['bayesian_score'] = score
    
    # TODO: consider scores from AniList

    # normalize and average
    all_data = adjust.adjust_scores(all_data)
    min_count = 3
    all_list = []
    for uid, item in all_data.items():
        count = 0
        score_sum = 0
        for site in item:
            site_data = item[site]
            if site_data is not None and 'adjusted_score' in site_data:
                count += 1
                score_sum += site_data['adjusted_score']
        if count >= min_count:
            item['score'] = score_sum / count
            all_list.append(item)

    # save
    save_method(all_list)


def always_update(args, save_method):
    """
    Keep udating the data.

    @param args: some args to be passed, as defined in arg_parser.
    @param save_method: a function, used for saving data to file/sql/oss.
    """

    myanimelist.jikan_api = args.jikan
    myanimelist.req_delay = args.delay
    myanimelist.use_api_pool = args.jikan_use_api_pool
    if args.jikan_use_api_pool:
        if args.jikan_api_pool == '':
            raise RuntimeError('You should provide the api pool if you enable Jikan api pool.')
        myanimelist.jikan_api_pool = [url for url in args.jikan_api_pool.split(' ') if url != '']
        myanimelist.jikan_api = myanimelist.jikan_api_pool[0]
        myanimelist.jikan_api_idx = 0

    if args.checkpoint != '':
        with open(args.checkpoint, 'r', encoding='utf-8') as f:
            pre_data = json.load(f)
    else:
        pre_data = {}
    
    while True:
        start_time = time.time()
        clear_cache()
        update_once(args, save_method, pre_data)
        end_time = time.time()
        time_spent = int(end_time - start_time)
        time_to_sleep = max(args.interval - time_spent, 0)
        print('\n\n\nSleeping for {} seconds\n\n\n'.format(time_to_sleep))
        time.sleep(time_to_sleep)
        del pre_data
        pre_data = {}


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--jikan', default='https://api.jikan.moe/v3',
        help='The URL of Jikan api')
    arg_parser.add_argument('--jikan_use_api_pool', action='store_true', default=False,
        help='Enable Jikan api pool')
    arg_parser.add_argument('--jikan_api_pool', default='',
        help='Jikan api url pool, use space to divide urls')
    arg_parser.add_argument('--delay', type=float, default=4,
        help='Delay seconds for requests')
    arg_parser.add_argument('--interval', type=int, default=86400,
        help='Update interval (seconds)')
    arg_parser.add_argument('--checkpoint', default='',
        help='File path to checkpoint (all.tmp.json).')
    args = arg_parser.parse_args()

    def save_json(data):
        with open('all.save.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    always_update(args, save_json)
