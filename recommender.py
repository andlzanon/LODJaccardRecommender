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

    def __calculate_jaccard(self,  movie1_id: int, props_m1: list, movie2_id: int, props_m2: list):
        """
        Function that calculates the jaccard similarity of two movies, if they are the same return 1
        :param movie1_id: movie_id of movie 1
        :param props_m1: list of tuples with the properties of movie 1
        :param movie2_id: list of tuples of movie 2
        :param props_m2: data frame with the properties of movie 2
        :return: jaccard similarity between the two lists
        """

        if movie1_id == movie2_id:
            return 1

        intersection = pd.Series(list(set(props_m1).intersection(set(props_m2))), dtype=str)
        union = pd.Series(list(set(props_m1).union(set(props_m2))), dtype=str)

        intersection_n = len(intersection)
        union_n = len(union)

        try:
            jaccard = intersection_n / union_n
        except ZeroDivisionError:
            jaccard = 0

        return jaccard

    def __get_movie_props(self, all_movies_props: pd.DataFrame, movie_id: int):
        """
        Get the movies properties from the data frame all_movie_props
        :param all_movies_props: data frame to extract movie properties from
        :param movie_id: id of the movie to extract the properties
        :return: a list of tuples with all of the movie properties
        """

        try:
            movie_props = all_movies_props.loc[movie_id]

            # when movie_props size is two, it means that there is only one line of return
            # and the command on line 63 wont work
            if len(movie_props) > 2:
                movie_tuples = [tuple(x) for x in movie_props.to_numpy()]
            else:
                movie_tuples = [(movie_props[0], movie_props[1])]

        except KeyError:
            movie_tuples = []

        return movie_tuples

    def __generate_similarity_matrix(self, movies_id: list):
        """
        Function that generates the similarity matrix
        :param movies_id: list of all movie id on data set
        :return: movie per movie similarity matrix where 1 means more proximity and 0 otherwise
        """

        movies_props = sparql_utils.get_all_movie_props(self.movies_set, flag=1)
        sim_movies = pd.DataFrame(0, index=movies_id, columns=movies_id)

        for i in range(0, len(movies_id)):
            movie1 = movies_id[i]
            movie1_props = self.__get_movie_props(movies_props, movie1)
            for j in range(i, len(movies_id)):
                movie2 = movies_id[j]
                movie2_props = self.__get_movie_props(movies_props, movie2)
                jac_sim = self.__calculate_jaccard(movie1, movie1_props, movie2, movie2_props)
                sim_movies.loc[movie1, movie2] = jac_sim
                sim_movies.loc[movie2, movie1] = jac_sim
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
        movies_id = self.movies_set['movie_id'].to_list()
        movies_id.sort()

        if flag == 0:
            sim_matrix = self.__generate_similarity_matrix(movies_id)
            sim_matrix.to_csv(file_path, mode='w', header=False, index=False)
        else:
            sim_matrix = pd.read_csv(file_path, header=None)
            sim_matrix.columns = movies_id
            sim_matrix.set_index(movies_id)

        return sim_matrix
