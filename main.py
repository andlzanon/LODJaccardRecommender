import numpy as np
import pandas as pd
import lod_recommender
import random
import baseline_colaborative_cosine as cos_baseline
import evaluation_utils


def read_data_set(file_path: str, columns: list):
    """
    :param file_path: path of dataset file
    :param columns: list of names for the columns of the dataset
    :return:  dataset with named columns
    """

    set = pd.read_csv(file_path, header=None, sep="\t")
    set.columns = columns
    return set


def main():
    cols = ['user_id', 'movie_id', 'interaction']
    # test and train sets are divided 0.2 and 0.8 respectively
    train_set = read_data_set("./facebook_movies/trainingset.tsv", cols)
    test_set = read_data_set("./facebook_movies/testset.tsv", cols)
    movies_set = read_data_set("./facebook_movies/mappingLinkedData.tsv", ['movie_id', 'dbpedia_uri'])

    # create user/item matrix
    user_item = pd.DataFrame(index=test_set["user_id"].unique(),
                             columns=[i for i in movies_set['movie_id'].sort_values().tolist()])

    # set 1 on user/item matrix if user interacted with movie
    for index, row in train_set.iterrows():
        user_id = row[0]
        movie_id = row[1]
        user_item.loc[user_id, movie_id] = 1

    # call recomendation engines
    recommender_engine = lod_recommender.JacLodRecommendationEngine(user_item, movies_set, test_set, 5, 5, 1, 0)

    n_rec = 20
    for i in range(0, n_rec):
        random_user = random.randint(train_set['user_id'].unique().min(), train_set['user_id'].unique().max())
        recommender_engine.generate_recommendation(user_id=random_user)

    # ---- accuracy results code ----
    # k_values = [5, 10, 20]
    # evaluation_utils.generate_accuracy_results(recommender_engine, k_values, "./results/lod_results.txt",
    #                                        "LOD Jaccard Recommender")
    # baseline = cos_baseline.CosineBaseline(user_item, test_set, movies_set, 5, 5)
    # evaluation_utils.generate_accuracy_results(baseline, k_values, "./results/baseline_results.txt",
    #                                            "Baseline Collaborative Item-KNN Recommender")

    print("--- END ---")


if __name__ == "__main__":
    main()
