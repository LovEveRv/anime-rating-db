import numpy as np


def norm(scores, mean=0, std=1):
    """
    Normalize the scores, let mean and std are as given.

    @param scores: list/np.array, all scores.
    @return: np.array, normalized scores.
    """

    _mean = np.mean(scores)
    _std = np.std(scores)
    # print(_mean, _std)
    _scores = (scores - _mean) / _std * std + mean
    return _scores


def adjust_scores(all_data):
    """
    Adjust scores from different sites.

    @param all_data: dict, as defined in ../pre_process.py.
    @return: dict, with "adjusted_score" in each item.
    """

    min_votes = 100

    mapping = {
        'ANN': 'bayesian_score',
        'MAL': 'score',
        'BGM': 'bayesian_score',
        'AniList': 'bayesian_score',
        'Anikore': 'bayesian_score',
    }

    all_scores = {
        'ANN': ([], []),
        'MAL': ([], []),
        'BGM': ([], []),
        'AniList': ([], []),
        'Anikore': ([], []),
    }
    
    for uid, item in all_data.items():
        for site, attr in mapping.items():
            if site in item and item[site] is not None:
                if attr in item[site] and item[site][attr] is not None:
                    score = item[site][attr]
                    if item[site]['votes'] >= min_votes:
                        all_scores[site][0].append(score)
                        all_scores[site][1].append(uid)

    overall_scores = []
    for site, data in all_scores.items():
        scores, uids = data
        overall_scores.extend(scores)

    overall_mean = np.mean(overall_scores)
    overall_std = np.std(overall_scores)
    # print(overall_mean, overall_std)

    for site, data in all_scores.items():
        scores, uids = data
        if len(scores) > 0:
            adj_scores = norm(scores, overall_mean, overall_std)
            for adj_score, uid in zip(adj_scores, uids):
                all_data[uid][site]['adjusted_score'] = adj_score

    return all_data


if __name__ == '__main__':
    """
    Just for testing.
    """

    # import json
    # with open('../all.json', 'r', encoding='utf-8') as f:
    #     all_data = json.load(f)
    # all_data = adjust_scores(all_data)
    # with open('../all.adjusted.json', 'w', encoding='utf-8') as f:
    #     json.dump(all_data, f, indent=2, ensure_ascii=False)
