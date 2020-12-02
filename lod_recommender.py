import numpy as np
import pandas as pd
import sparql_utils
import evaluation_utils
import explanations


# A class that generates recomendations and explanations based on dbpedia
class JacLodRecommendationEngine:

    def __init__(self, user_item: pd.DataFrame, movies_set: pd.DataFrame, test_set: pd.DataFrame,
                 k: int, n: int, explanation_flag: int, sim_matrix_flag: int,
                 sim_matrix_path="./generated_files/sim_matrix.csv",
                 all_props_path="./generated_files/all_movie_props.csv"):
        """
        Constructor of the class
        :param user_item: user item matrix
        :param movies_set: movies data frame with two columns for movie id and movie dbpedia uri
        :param test_set: test data frame with interactions to predict
        :param k: number of neighbours
        :param n: number of recommendation items to return
        :param explanation_flag: 1 to generate explanations and 0 otherwise
        :param sim_matrix_flag: 1 to generate the similarity matrix from scratch, 0 to read from file path
        :param sim_matrix_path: path to file of the similarity matrix
        :param all_props_path: path to file with all properties
        """

        self.user_item = user_item
        self.test_set = test_set
        self.movies_set = movies_set.set_index(movies_set['movie_id'].values)
        self.k = k
        self.n = n
        self.explanation_flag = explanation_flag
        self.sim_matrix_flag = sim_matrix_flag
        self.sim_matrix_path = sim_matrix_path
        self.all_props_path = all_props_path

    def set_k(self, new_k: int):
        """
        setter of neighbours of class
        :param new_k: new value of k
        :return:k of class changed
        """
        self.k = new_k

    def set_n(self, new_n: int):
        """
        setter of top n of class
        :param new_n: new value of n
        :return: n of class changed
        """
        self.n = new_n

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

    def __generate_similarity_matrix(self, movies_id: list):
        """
        Function that generates the similarity matrix
        :param movies_id: list of all movie id on data set
        :return: movie per movie similarity matrix where 1 means more proximity and 0 otherwise
        """

        movies_props = sparql_utils.get_all_movie_props(self.movies_set, self.sim_matrix_flag, self.all_props_path)
        sim_movies = pd.DataFrame(0, index=movies_id, columns=movies_id)

        for i in range(0, len(movies_id)):
            movie1 = movies_id[i]
            movie1_props = sparql_utils.movie_props_tolist(movie1, movies_props)
            for j in range(i, len(movies_id)):
                movie2 = movies_id[j]
                movie2_props = sparql_utils.movie_props_tolist(movie2, movies_props)
                jac_sim = self.__calculate_jaccard(movie1, movie1_props, movie2, movie2_props)
                sim_movies.loc[movie1, movie2] = jac_sim
                sim_movies.loc[movie2, movie1] = jac_sim
                print("sim: " + str(movie1) + " / " + str(movie2) + " = " + str(sim_movies.loc[movie1, movie2]))

        return sim_movies

    def __get_similarity_matrix(self):
        """
        Function that gets or generates the similarity matrix
        :return: the similarity matrix with index and column
        """
        movies_id = self.movies_set['movie_id'].to_list()
        movies_id.sort()

        if self.sim_matrix_flag == 1:
            sim_matrix = self.__generate_similarity_matrix(movies_id)
            sim_matrix.to_csv(self.sim_matrix_path, mode='w', header=False, index=False)
        else:
            sim_matrix = pd.read_csv(self.sim_matrix_path, header=None)
            sim_matrix.columns = movies_id
            sim_matrix.index = movies_id

        return sim_matrix

    def generate_recommendation(self, user_id: int):
        """
        Function that generates a top n recommendation to a user
        :param user_id: user to generate recommendation
        :return: recommendations with or without the explanation to the user
        """
        sim_matrix = self.__get_similarity_matrix()
        user_interactions = self.user_item.loc[user_id].sort_values()

        profile = user_interactions[user_interactions == 1]
        prediction = user_interactions[user_interactions.isnull()]

        for movie in prediction.index:
            prediction.loc[movie] = evaluation_utils.calculate_prediction(movie, profile, sim_matrix, self.k)

        prediction = prediction.sort_values(ascending=False)
        recommended_movies = prediction[:self.n]
        print("----- MOVIES WATCHED BY THE USER " + str(user_id) + " -----")
        for movie in profile.index:
            print(sparql_utils.get_movie_name(sparql_utils.get_all_movie_props(self.movies_set, 0, self.all_props_path),
                                             movie))

        print("----- MOVIES RECOMMENDED TO THE USER " + str(user_id) + " -----")
        for movie in recommended_movies.index:
            print(sparql_utils.get_movie_name(sparql_utils.get_all_movie_props(self.movies_set, 0, self.all_props_path),
                                              movie))

        print("----- EXPLANATIONS TO THE USER " + str(user_id) + " -----")
        if self.explanation_flag == 1:
            all_movies_props = sparql_utils.get_all_movie_props(self.movies_set,
                                                                self.sim_matrix_flag,
                                                                self.all_props_path)
            movies_explanations = explanations.Explanations(profile, recommended_movies,
                                                            all_movies_props, len(sim_matrix.index.unique()))

            movies_explanations.generate_explanations()

    def generate_map(self):
        """
        Function that returns the MAP accuracy metric of the recommendation algorithm
        :return: MAP accuracy of the algorithm
        """
        sim_matrix = self.__get_similarity_matrix()
        return evaluation_utils.generate_map(sim_matrix, self.test_set, self.user_item, self.n, self.k)
