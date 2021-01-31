import json

from matplotlib import pyplot as plt


"""
Plot the distribution of ratings.
"""


with open('../all.json', 'r', encoding='utf-8') as f:
    all_data = json.load(f)

x = [i * 0.1 for i in range(101)]
ann_stats = [0 for _ in range(101)]
mal_stats = [0 for _ in range(101)]
bgm_stats = [0 for _ in range(101)]

min_votes = 100

for k, v in all_data.items():
    ann = v['ANN']
    ann_score = ann['bayesian_score']
    ann_votes = ann['votes']
    if ann_score is not None and ann_votes >= min_votes:
        idx = int(round(ann_score, 1) * 10)
        ann_stats[idx] += 1

    mal = v['MAL']
    if mal is not None:
        mal_score = mal['score']
        mal_votes = ann['votes']
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
