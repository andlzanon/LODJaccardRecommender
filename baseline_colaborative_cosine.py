import numpy as np
import pandas as pd
from scipy.spatial.distance import cosine
import evaluation_utils


class CosineBaseline:
    def __init__(self, user_item: pd.DataFrame, test_set: pd.DataFrame, movies_set: pd.DataFrame, k: int, n: int,
                 sim_matrix_flag=0, sim_matrix_path="./generated_files/item_knn_sim.csv"):
        self.user_item = user_item
        self.test_set = test_set
        self.movies_set = movies_set
        self.sim_matrix_flag = sim_matrix_flag
        self.sim_matrix_path = sim_matrix_path
        self.k = k
        self.n = n

    def set_k(self, new_k: int):
        self.k = new_k

    def set_n(self, new_n: int):
        self.n = new_n

    def __get_similarity_matrix(self):

        movies_id = self.movies_set['movie_id'].to_list()
        movies_id.sort()

        if self.sim_matrix_flag == 1:
            item_sim = pd.DataFrame(0, index=movies_id, columns=movies_id)
            for i in range(0, len(movies_id)):
                column1 = movies_id[i]
                for j in range(i, len(movies_id)):
                    column2 = movies_id[j]
                    sim = 1 - cosine(self.user_item[column1].fillna(0), self.user_item[column2].fillna(0))
                    item_sim.loc[column1, column2] = sim
                    item_sim.loc[column2, column1] = sim

            item_sim.to_csv(self.sim_matrix_path, mode='w', header=False, index=False)

        else:
            item_sim = pd.read_csv(self.sim_matrix_path, header=None)
            item_sim.columns = movies_id
            item_sim.index = movies_id

        return item_sim

    def generate_map(self):
        sim_matrix = self.__get_similarity_matrix()
        return 1
