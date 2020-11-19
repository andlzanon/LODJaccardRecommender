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

        self.movies_set = movies_set
        self.movies_set.set_index(movies_set['movie_id'].values)

        self.k = k

    def __calculate_jaccard(self, props_m1: list, props_m2: list):
        """
        Function that calculates the jaccard similarity of two movies
        :param props_m1: list of tuples (properties, resources) of movie 1
        :param props_m2:  list of tuples (properties, resources) of movie 2
        :return: jaccard similarity between the two lists
        """
        intersection = pd.Series(list(set(props_m1).intersection(set(props_m2))), dtype=str)
        union = pd.Series(list(set(props_m1).union(set(props_m2))), dtype=str)

        intersection_n = len(intersection)
        union_n = len(union)

        jaccard = intersection_n / union_n
        return jaccard

    def __generate_similarity_matrix(self):
        """
        Function that generates the similarity matrix
        :return: movie per movie similarity matrix where 1 means more proximity and 0 otherwise
        """
        exclusions = ["http://xmlns.com/foaf/0.1/name"]
        movies_id = self.movies_set['movie_id'].values
        movies_id.sort()
        sim_movies = pd.DataFrame(0, index=movies_id, columns=movies_id)

        for i in range(0, len(movies_id)):
            movie1 = movies_id[i]
            movie1_uri = self.movies_set.loc[movie1]['dbpedia_uri']
            movie1_props = sparql_utils.get_props_from_dbpedia(movie1_uri, exclusions)
            for j in range(i, len(movies_id)):
                movie2 = movies_id[j]
                movie2_uri = self.movies_set.loc[movie2]['dbpedia_uri']
                movie2_props = sparql_utils.get_props_from_dbpedia(movie2_uri, exclusions)
                jac_sim = self.__calculate_jaccard(movie1_props, movie2_props)
                sim_movies.at[movie1, movie2] = jac_sim
                print("sim bettween " + str(movie1) + " " + str(movie2) + "= " + str(sim_movies.loc[movie1, movie2]))

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
