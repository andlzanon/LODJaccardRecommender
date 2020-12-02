import numpy as np
import pandas as pd
from scipy.spatial.distance import cosine
import evaluation_utils


class CosineBaseline:
    def __init__(self, user_item: pd.DataFrame, test_set: pd.DataFrame, movies_set: pd.DataFrame, k: int, n: int,
                 sim_matrix_flag=0, sim_matrix_path="./generated_files/item_knn_sim.csv"):
        """
        Constructor of the class
        :param user_item: user item matrix data frame
        :param test_set: test set
        :param movies_set: movies set
        :param k: number of neighbours
        :param n: number of recommendation items to return
        :param sim_matrix_flag: 1 to generate the similarity matrix from scratch, 0 to read from file path
        :param sim_matrix_path: path to file of the similarity matrix
        """
        self.user_item = user_item
        self.test_set = test_set
        self.movies_set = movies_set
        self.sim_matrix_flag = sim_matrix_flag
        self.sim_matrix_path = sim_matrix_path
        self.k = k
        self.n = n

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

    def __get_similarity_matrix(self):
        """
        Function that gets or generates the similarity matrix
        :return: the similarity matrix with index and column
        """
        movies_id = self.movies_set['movie_id'].to_list()
        movies_id.sort()

        if self.sim_matrix_flag == 1:
            np.seterr(all='raise')
            item_sim = pd.DataFrame(0, index=movies_id, columns=movies_id)
            for i in range(0, len(movies_id)):
                column1 = movies_id[i]
                for j in range(i, len(movies_id)):
                    column2 = movies_id[j]
                    try:
                        sim = 1 - cosine(self.user_item[column1].fillna(0), self.user_item[column2].fillna(0))
                    except FloatingPointError:
                        sim = 0

                    item_sim.loc[column1, column2] = sim
                    item_sim.loc[column2, column1] = sim
                    print("sim: " + str(column1) + " / " + str(column2) + " = " + str(item_sim.loc[column1, column2]))

            item_sim.to_csv(self.sim_matrix_path, mode='w', header=False, index=False)

        else:
            item_sim = pd.read_csv(self.sim_matrix_path, header=None)
            item_sim.columns = movies_id
            item_sim.index = movies_id

        return item_sim

    def generate_map(self):
        """
        Function that returns the MAP accuracy metric of the recommendation algorithm
        :return: MAP accuracy of the algorithm
        """
        sim_matrix = self.__get_similarity_matrix()
        return evaluation_utils.generate_map(sim_matrix, self.test_set, self.user_item, self.n, self.k)
