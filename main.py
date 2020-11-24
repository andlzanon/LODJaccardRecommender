import numpy as np
import pandas as pd
import recommender


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
    """
    create DataFrames, call recommendation engine and show results
    """

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

    # call recomendation engine and get or generate similarity matrix based on dbpedia
    recommender_engine = recommender.JacLodRecommendationEngine(user_item, movies_set, test_set, 5, 5, 0, 0)
    recommender_engine.generate_recommendation(user_id=1)
    print("--- END ---")


if __name__ == "__main__":
    main()
