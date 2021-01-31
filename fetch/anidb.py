import requests
import traceback
import json
import gzip
import xml.dom.minidom


"""
Notice that using AniDB API requires a registered client.
You can set variables here, or pass by console arguments. (see ../pre_process.py)
"""

client = ''  # change this to your own client here
clientver = 1  # change this to your own client version
protover = 1  # change this to your own protocol version


def download_all_anime_list(fpath='anime-titles.xml'):
    """
    Download a list of all anime, from AniDB.

    @param fpath: a string, the path to save the dumped file.
    @return: True for success and False for failure.

    P.S. AniDB provides a daily dumped file for this kind of request.
         But remember not to request the file "MORE THAN ONCE PER DAY".
         (https://wiki.anidb.net/API#Anime_Titles)
    """

    try:
        dumped_file_url = 'http://anidb.net/api/anime-titles.xml.gz'
        gzpath = fpath + '.gz'
        # downloading
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) \
            AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15'
        }
        resp = requests.get(dumped_file_url, headers=headers)
        with open(gzpath, 'wb') as f:
            f.write(resp.content)
        # unzipping
        gfile = gzip.GzipFile(gzpath)
        with open(fpath, 'wb') as f:
            f.write(gfile.read())
        gfile.close()
        return True
    except Exception:
        traceback.print_exc()
        return False


def get_all_anime_id_list(fpath='anime-titles.xml'):
    """
    Get a id (also called "aid") list of all anime, from local-dumped file.
    If anything failed, return None. (A typical error: file not exist)

    @param fpath: a string, the path of the local-dump file.
    @return: a list of strings, each string is an id.

    P.S. Make sure the file exists. This function won't check it for you,
         it will simply return None.
    """

    try:
        dom = xml.dom.minidom.parse(fpath)
        root = dom.documentElement
        items = root.getElementsByTagName('anime')
        id_list = [item.getAttribute('aid') for item in items]
        return id_list
    except Exception:
        traceback.print_exc()
        return None


def get_anime_detail(aid):
    """
    Get detail for an anime, from AniDB.
    If anything failed, return None.

    @param aid: string or int, an id.
    @return: a dict, containing detailed data.

    P.S. It's a very good news that AniDB provides "resource" attribute for
         an anime, which links to Anime News Network. We can only keep very
         few info and we have no need for searching!
    """

    try:
        api_url = 'http://api.anidb.net:9001/httpapi?request=anime&client=' + client \
            + '&clientver=' + str(clientver) + '&protover=' + str(protover) + '&aid=' + str(aid)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) \
            AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15'
        }
        resp = requests.get(api_url, headers=headers)
        # response in XML format, parsing needed
        dom = xml.dom.minidom.parseString(resp.text)
        root = dom.documentElement
        detail = {}
        detail['id'] = aid
        rating = root.getElementsByTagName('ratings')[0]
        rating = rating.getElementsByTagName('permanent')[0]
        detail['score'] = float(rating.childNodes[0].data)
        detail['votes'] = int(rating.getAttribute('count'))
        air = root.getElementsByTagName('startdate')[0]
        detail['air'] = air.childNodes[0].data
        resources = root.getElementsByTagName('resources')[0]
        resources = resources.getElementsByTagName('resource')
        detail['ann_id'] = []
        detail['mal_id'] = []
        for resource in resources:
            if resource.getAttribute('type') == '1':
                externalentity = resource.getElementsByTagName('externalentity')[0]
                identifier = externalentity.getElementsByTagName('identifier')[0]
                detail['ann_id'].append(identifier.childNodes[0].data)
            if resource.getAttribute('type') == '2':
                externalentity = resource.getElementsByTagName('externalentity')[0]
                identifier = externalentity.getElementsByTagName('identifier')[0]
                detail['mal_id'].append(identifier.childNodes[0].data)
        return detail
    except Exception:
        traceback.print_exc()
        return None


if __name__ == '__main__':
    """
    Just for testing.
    """

    # download_all_anime_list()
    # id_list = get_all_anime_id_list()
    # print(len(id_list))
    # detail = get_anime_detail(5101)
    # print(detail)
