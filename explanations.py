import numpy as np
import pandas as pd
import sparql_utils
import re
import math


class Explanations:

    def __init__(self, profile: pd.DataFrame, recommended: pd.DataFrame,
                 movie_props: pd.DataFrame, number_documents: int):
        """
        Constructor of class explanations
        :param profile: items that the user interacted
        :param recommended: recommended movies
        :param movie_props: movies properties
        :param number_documents: number of movies in data_set
        """
        self.profile = profile
        self.recommended = recommended
        self.movie_props = movie_props
        self.number_documents = number_documents

    def __get_profile_recommended_graph(self, rec_movie_id: int):
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

        graph = graph.set_index(cols[2])
        return graph

    def __generate_score(self, graph: pd.DataFrame):
        prop_scores = pd.DataFrame(index=graph.index.unique(), columns=['prop', 'score'])
        for obj in graph.index.unique():
            ncip = len(graph.loc[obj])
            count_d = self.movie_props['obj'].value_counts()[obj]
            idf = math.log(self.number_documents / count_d)
            score = (ncip / len(self.profile)) * idf
            try:
                rel = graph.loc[obj]['prop'].unique()[0]
            except AttributeError:
                rel = graph.loc[obj]['prop']

            prop_scores.loc[obj] = [rel, score]

        # return properties with max score
        return prop_scores.loc[prop_scores['score'] == prop_scores.max()[1]]

    def __get_value_of_uri(self, property: str):
        flag = False
        reg = r'\([\s\S]*\)'
        separated = property.split("/")
        most_important = separated[-1]
        if "franchise" not in most_important:
            most_important = re.sub(reg, '', most_important)
            flag = True

        most_important = most_important.replace("_", " ")

        prev_len = len(most_important)
        most_important = most_important.replace("Category:", "")
        curr_len = len(most_important)
        if prev_len != curr_len and flag:
            most_important = most_important[0].lower() + most_important[1:]

        if most_important[-1] == " ":
            most_important = most_important[:-1]

        return most_important

    def __generate_sentence(self, graph: pd.DataFrame, most_relevant_prop: pd.DataFrame, movie: int):
        explanations = ["Because you like "]

        for index, row in most_relevant_prop.iterrows():
            prop = row[0].split("/")[-1]
            if prop == "subject":
                sentence = self.__get_value_of_uri(str(index)) + " such as "
            elif prop == "cinematography" or prop == "editing":
                sentence = "the " + prop + " of " + self.__get_value_of_uri(str(index)) + " of "
            elif prop == "producer" or prop == "director" or prop == "distributor":
                sentence = "the " + prop + " " + self.__get_value_of_uri(str(index)) + " of "
            elif prop == "musicComposer":
                music_composer = re.sub("([a-z])([A-Z])", "\g<1> \g<2>", prop)
                separated = music_composer.split()
                music_composer = separated[0] + separated[-1][0].lower() + separated[-1][1:]
                sentence = "the " + music_composer + " " + self.__get_value_of_uri(str(index)) + " of "
            else:
                sentence = "films " + prop + " " + self.__get_value_of_uri(str(index)) + " like "

            movies_id = graph.loc[index]['movie_id']
            if type(movies_id) == pd.Series:
                count = 0
                for movie_id in movies_id.iteritems():
                    movie_name = sparql_utils.get_movie_name(self.movie_props, movie_id[1])
                    if count != len(movies_id) - 1:
                        sentence = sentence + "\"" + movie_name + "\", "
                    else:
                        sentence = sentence[:-2] + " and \"" + movie_name + "\""
                    count = count + 1
            else:
                movie_name = "\"" + sparql_utils.get_movie_name(self.movie_props, movies_id) + "\""
                sentence = sentence + movie_name

            explanations.append(sentence)

        explanation_sentence = explanations[0]
        if len(explanations) > 2:
            for i in range(1, len(explanations)):
                if i != len(explanations) - 1:
                    explanation_sentence = explanation_sentence + explanations[i] + "; "
                else:
                    explanation_sentence = explanation_sentence[:-2] + " and " + explanations[i]
        else:
            explanation_sentence = explanations[0] + explanations[1]

        explanation_sentence = explanation_sentence + " watch \"" + \
                               sparql_utils.get_movie_name(self.movie_props, movie) + "\" with these same characteristics"

        return explanation_sentence

    def generate_explanations(self):
        explanation = pd.DataFrame(index=self.recommended.index, columns=['sentence'])
        for movie in self.recommended.index:
            profile_recommended_graph = self.__get_profile_recommended_graph(movie)
            most_relevant_prop = self.__generate_score(profile_recommended_graph)
            explanation.loc[movie] = self.__generate_sentence(profile_recommended_graph, most_relevant_prop, movie)

        for movie in self.recommended.index:
            print(explanation.loc[movie]['sentence'])
