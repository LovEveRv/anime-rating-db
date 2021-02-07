import numpy as np


def calc_bayesian_score(ratings, min_votes=100):
    """
    Calculate score using Bayesian Estimation.

    @param ratings: list/np.array, shaped N x C, where N is number of samples, C is number of classes.
           For an example, if ratings can be 1-5, then [[10, 20, 30, 40, 50]] means for sample 0,
           10 people rated 1, 20 people rated 2, ..., 50 people rated 5.
    @param min_votes: int, means the min number of votes one sample must reach to get a bayesian score.
    @return: list, shaped N, each item is a bayesian score of that sample. if votes < min_votes,
             bayesian score will be None.
    """

    ratings = np.array(ratings)
    N, C = ratings.shape
    score = np.arange(1, C + 1)
    v_sum = np.sum(ratings)
    s_sum = np.sum(ratings * score)
    overall_avg = s_sum / v_sum
    
    v_sum = np.sum(ratings, 1)
    s_sum = np.sum(ratings * score, 1)
    bayesian = []
    for v, s in zip(v_sum, s_sum):
        if v < min_votes:
            bayesian.append(None)
        else:
            bayesian.append((s + min_votes * overall_avg) / (v + min_votes))
    return bayesian


def calc_bayesian_score_by_average(ratings, min_votes=100):
    """
    Calculate score using Bayesian Estimation.

    @param ratings: list/np.array, shaped 2 x N, where N is number of samples.
                    ratings[0] are average scores, ratings[1] are corresponding votes.
    @param min_votes: int, means the min number of votes one sample must reach to get a bayesian score.
    @return: list, shaped N, each item is a bayesian score of that sample. if votes < min_votes,
             bayesian score will be None.
    """

    score = np.array(ratings[0])
    votes = np.array(ratings[1])
    v_sum = np.sum(votes)
    s_sum = np.sum(score * votes)
    overall_avg = s_sum / v_sum

    bayesian = []
    for v, s in zip(votes, score):
        if v < min_votes:
            bayesian.append(None)
        else:
            bayesian.append((s * v + min_votes * overall_avg) / (v + min_votes))
    return bayesian


if __name__ == '__main__':
    """
    Just for testing.
    """

    # import json
    # with open('../all.json') as f:
    #     all_data = json.load(f)
    # ids, ratings = [], []
    # for uid, item in all_data.items():
    #     bgm = item['BGM']
    #     if bgm is not None and bgm['rating_detail'] is not None:
    #         ids.append(uid)
    #         rating_detail = list(bgm['rating_detail'].values())
    #         rating_detail.reverse()
    #         ratings.append(rating_detail)
    # scores = calc_bayesian_score(ratings, 10)
    # for uid, score in zip(ids, scores):
    #     all_data[uid]['BGM']['bayesian_score'] = score
    # with open('../all.json', 'w', encoding='utf-8') as f:
    #     json.dump(all_data, f, indent=2, ensure_ascii=False)
