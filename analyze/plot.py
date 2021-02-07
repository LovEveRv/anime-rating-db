import json

from matplotlib import pyplot as plt


"""
Plot the distribution of ratings.
"""


with open('../all.save.json', 'r', encoding='utf-8') as f:
    all_data = json.load(f)

x = [i * 0.1 for i in range(101)]
ann_stats = [0 for _ in range(101)]
mal_stats = [0 for _ in range(101)]
bgm_stats = [0 for _ in range(101)]
anl_stats = [0 for _ in range(101)]
akr_stats = [0 for _ in range(101)]

min_votes = 100

for v in all_data:
    ann = v['ANN']
    if ann is not None:
        ann_score = ann['bayesian_score']
        ann_votes = ann['votes']
        if ann_score is not None and ann_votes >= min_votes:
            idx = int(round(ann_score, 1) * 10)
            ann_stats[idx] += 1

    mal = v['MAL']
    if mal is not None:
        mal_score = mal['score']
        mal_votes = mal['votes']
        if mal_score is not None and mal_votes >= min_votes:
            idx = int(round(mal_score, 1) * 10)
            mal_stats[idx] += 1
    
    bgm = v['BGM']
    if bgm is not None:
        try:
            bgm_score = bgm['bayesian_score']
        except:
            bgm_score = bgm['score']
        bgm_votes = bgm['votes']
        if bgm_score is not None and bgm_votes >= min_votes:
            idx = int(round(bgm_score, 1) * 10)
            bgm_stats[idx] += 1
    
    anl = v['AniList']
    if anl is not None:
        try:
            anl_score = anl['bayesian_score']
        except:
            anl_score = anl['averageScore'] / 10
        anl_votes = anl['votes']
        if anl_score is not None and anl_votes >= min_votes:
            idx = int(round(anl_score, 1) * 10)
            anl_stats[idx] += 1

    akr = v['Anikore']
    if akr is not None:
        akr_score = akr['score'] * 2
        akr_votes = akr['votes']
        if akr_score is not None and akr_votes >= min_votes:
            idx = int(round(akr_score, 1) * 10)
            akr_stats[idx] += 1

plt.bar(x, ann_stats, width=0.08)
plt.title('Anime News Network')
plt.xlabel('Rating')
plt.ylabel('Counts')
plt.savefig('ann.png', dpi=300)

plt.clf()
plt.bar(x, mal_stats, width=0.08)
plt.title('MyAnimeList')
plt.xlabel('Rating')
plt.ylabel('Counts')
plt.savefig('mal.png', dpi=300)

plt.clf()
plt.bar(x, bgm_stats, width=0.08)
plt.title('Bangumi')
plt.xlabel('Rating')
plt.ylabel('Counts')
plt.savefig('bgm.png', dpi=300)

plt.clf()
plt.bar(x, anl_stats, width=0.08)
plt.title('AniList')
plt.xlabel('Rating')
plt.ylabel('Counts')
plt.savefig('anilist.png', dpi=300)

plt.clf()
plt.bar(x, akr_stats, width=0.08)
plt.title('Anikore')
plt.xlabel('Rating')
plt.ylabel('Counts')
plt.savefig('anikore.png', dpi=300)
