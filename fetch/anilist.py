import requests
import traceback
import json
import os


def get_anime_detail(anl_id, cache=False, cache_dir='.'):
    """
    Get detail for an anime, from AniList.
    You can enable cache to make less requests.
    If anything failed, return None.

    @param anl_id: string or int, an id.
    @param cache: boolean, enable cache.
    @param cache_dir: string, path to cache directory.
    @return: a dict, containing detailed data.
    """

    try:
        api_url = 'https://graphql.anilist.co'
        cache_path = os.path.join(cache_dir, '{}.json'.format(anl_id))
        if cache and os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            query = '''
            query ($id: Int) {
                Media (id: $id, type: ANIME) {
                    id
                    title {
                        romaji
                        english
                        native
                    }
                    coverImage {
                        large
                    }
                    averageScore
                    stats {
                        scoreDistribution {
                            score
                            amount
                        }
                    }
                }
            }
            '''
            variables = {
                'id': anl_id
            }
            resp = requests.post(api_url, json={ 'query': query, 'variables': variables })
            data = resp.json()['data']
            data = data['Media']
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

    # print(get_anime_detail(5114))
