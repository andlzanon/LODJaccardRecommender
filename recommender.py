import numpy as np
import pandas as pd
import sparql_utils
import explanations


# A class that generates recomendations and explanations based on dbpedia
class JacLodRecommendationEngine:

    def __init__(self, user_item: pd.DataFrame, movies_set: pd.DataFrame, test_set: pd.DataFrame, k: int):
        """
        Constructor of the class
        :param user_item: user item matrix
        :param movies_set: movies data frame with two columns for movie id and movie dbpedia uri
        :param test_set: test data frame with interactions to predict
        :param k: number of neighbours
        """

        self.user_item = user_item
        self.test_set = test_set
        self.movies_set = movies_set.set_index(movies_set['movie_id'].values)
        self.k = k

    def __calculate_jaccard(self, props_m1: pd.DataFrame, props_m2: pd.DataFrame):
        """
        Function that calculates the jaccard similarity of two movies
        :param props_m1: data frame with the properties of movie 1
        :param props_m2: data frame with the properties of movie 2
        :return: jaccard similarity between the two lists
        """
        m1_tuples = [tuple(x) for x in props_m1.to_numpy()]
        m2_tuples = [tuple(x) for x in props_m2.to_numpy()]

        intersection = pd.Series(list(set(m1_tuples).intersection(set(m2_tuples))), dtype=str)
        union = pd.Series(list(set(m1_tuples).union(set(m2_tuples))), dtype=str)

        intersection_n = len(intersection)
        union_n = len(union)

        jaccard = intersection_n / union_n
        return jaccard

    def __generate_similarity_matrix(self):
        """
        Function that generates the similarity matrix
        :return: movie per movie similarity matrix where 1 means more proximity and 0 otherwise
        """

        movies_id = self.movies_set['movie_id'].to_list()
        movies_id.sort()
        movies_props = sparql_utils.get_all_movie_props(self.movies_set, flag=0)
        sim_movies = pd.DataFrame(0, index=movies_id, columns=movies_id)

        for i in range(0, len(movies_id)):
            movie1 = movies_id[i]
            movie1_props = movies_props.loc[movie1]
            for j in range(i, len(movies_id)):
                movie2 = movies_id[j]
                movie2_props = movies_props.loc[movie2]
                jac_sim = self.__calculate_jaccard(movie1_props, movie2_props)
                sim_movies.loc[movie1, movie2] = jac_sim
                print("sim: " + str(movie1) + " / " + str(movie2) + " = " + str(sim_movies.loc[movie1, movie2]))

        return sim_movies

    def get_similarity_matrix(self, flag: int, file_path="./generated_files/sim_matrix.csv"):
        """
        Function that gets or generates the similarity matrix based on the flag
        :param flag: if 0 the function will generate the sim matrix and save it on path
            "./generated_files/sim_matrix.csv" (it will take much longer time to finish). Otherwise,
             the matrix will be read from file path
        :param file_path: path where the matrix will be saved/read from
        :return: the similarity matrix with index and column
        """

        if flag == 0:
            sim_matrix = self.__generate_similarity_matrix()
            sim_matrix.to_csv(file_path, mode='w', header=False, index=False)
        else:
            sim_matrix = pd.read_csv(file_path, header=None)

        sim_matrix.index = self.user_item.columns
        sim_matrix.columns = self.user_item.columns

        return sim_matrix
