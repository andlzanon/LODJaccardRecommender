import numpy as np
import pandas as pd
import lod_recommender
import baseline_colaborative_cosine as cos_baseline


def read_data_set(file_path: str, columns: list):
    """
    :param file_path: path of dataset file
    :param columns: list of names for the columns of the dataset
    :return:  dataset with named columns
    """

    set = pd.read_csv(file_path, header=None, sep="\t")
    set.columns = columns
    return set


def get_acuracy_results(lod_rec: lod_recommender.JacLodRecommendationEngine, baseline_rec: cos_baseline.CosineBaseline,
                        k_values: list):
    """
    Compute map accuracy results for proposed and recommended
    :param lod_rec: lod dbpedia recommender
    :param baseline_rec: baseline cosine recommender
    :param k_values: vector of k params to test
    :return: file with results
    """
    f = open("./results/results.txt", "w")
    for k in k_values:
        f.write("--- K = " + str(k) + " ---\n")

        lod_rec.set_k(k)
        baseline_rec.set_k(k)

        f.write("LOD Jaccard Algorithm MAP: " + str(lod_rec.generate_map()))
        f.write("LOD Jaccard Algorithm MAP: " + str(lod_rec.generate_map()))

    f.close()


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
    # baseline = cos_baseline.CosineBaseline(user_item, test_set, movies_set, 5, 5)
    recommender_engine = lod_recommender.JacLodRecommendationEngine(user_item, movies_set, test_set, 5, 5, 1, 0)
    # get_acuracy_results(recommender_engine, baseline, [3, 5, 15])

    recommender_engine.generate_recommendation(user_id=10)
    # print("--- MAP ---")
    # mean_ap = recommender_engine.generate_map()
    # print(mean_ap)
    print("--- END ---")


if __name__ == "__main__":
    main()
