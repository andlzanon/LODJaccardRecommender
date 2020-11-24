import numpy as np
import pandas as pd
import sparql_utils


class Explanations:

    def __init__(self, profile: pd.DataFrame, recommended: pd.DataFrame, movie_props: pd.DataFrame):
        """
        Constructor of class explanations
        :param profile: items that the user interacted
        :param recommended: recommended movies
        :param movie_props: movies properties
        """
        self.profile = profile
        self.recommended = recommended
        self.movie_props = movie_props

    def __explanation_for_movie(self, rec_movie_id: int, cols: list):
        dict = {cols[0]: rec_movie_id, cols[1]: "", cols[2]: 0}
        cols = ['movie_id', 'prop', 'obj']
        graph = pd.DataFrame(columns=cols)
        rec_movie_props = self.movie_props.loc[rec_movie_id]
        rec_movie_props_l = sparql_utils.movie_props_tolist(rec_movie_id, rec_movie_props)

        for i in range(0, len(self.profile.index)):
            pro_movie = self.profile.index[i]
            pro_movie_props = self.movie_props.loc[pro_movie]
            pro_movie_props_l = sparql_utils.movie_props_tolist(pro_movie, pro_movie_props)

            intersection = pd.Series(list(set(rec_movie_props_l).intersection(set(pro_movie_props_l))), dtype=str)

            for tuples in intersection.values:
                graph = graph.append({cols[0]: pro_movie, cols[1]: tuples[0], cols[2]: tuples[1]}, ignore_index=True)

        return dict

    def generate_explanations(self):
        cols = ['movie_id', 'explanation', 'score']
        explanation = pd.DataFrame(columns=cols)
        for movie in self.recommended.index:
            explanation = explanation.append(self.__explanation_for_movie(movie, cols), ignore_index=True)
