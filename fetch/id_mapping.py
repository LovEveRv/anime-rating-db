import requests
import traceback
import json


def download_burstlink_mapping(fpath='burstlink.json'):
    """
    Download the mapping from github.

    @param fpath: a string, the path to save the json file.
    @return: True for success and False for failure.

    Source: https://github.com/soruly/burstlink
    Thank you for the great work!
    """

    try:
        url = 'https://raw.githubusercontent.com/soruly/burstlink/master/burstlink.json'
        # downloading
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) \
            AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15'
        }
        resp = requests.get(url, headers=headers)
        mapping = resp.json()
        for i in range(len(mapping)):
            item = mapping[i]
            item['mal'] = None if 'mal' not in item else item['mal']
            item['anidb'] = None if 'anidb' not in item else item['anidb']
            item['anilist'] = None if 'anilist' not in item else item['anilist']
            mapping[i] = item
        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        traceback.print_exc()
        return False


if __name__ == '__main__':
    """
    Just for testing.
    """

    # download_burstlink_mapping()
    