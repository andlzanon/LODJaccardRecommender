import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON

# utils sparql functions lib


def __get_props_of_movie_from_dbpedia(movie_id: int, movie_uri: str):
    """
    Function that obtains the tuples (properties, resources) of a movie form its' uri
    :param movie_id: id of the movie on the data set
    :param movie_uri: path to the movie resource from dbpedia
    :return: dict with properties of movies, along with its' movie id
    """

    print(movie_uri)

    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery("""
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX dc: <http://purl.org/dc/elements/1.1/>
    PREFIX : <http://dbpedia.org/resource/>
    PREFIX dbpedia2: <http://dbpedia.org/property/>
    PREFIX dbpedia: <http://dbpedia.org/>       
    PREFIX dct:	<http://purl.org/dc/terms/> 
    PREFIX ns:<http://www.w3.org/ns/prov#>    
    SELECT DISTINCT *
    WHERE { 
        <""" + movie_uri + """> ?prop ?obj.
        FILTER( 
            ?prop = dbo:cinematography || ?prop = dbo:director || ?prop = dbo:distributor || 
            ?prop = dbo:editing || ?prop = dbo:musicComposer || ?prop = dbo:producer || 
            ?prop = dbo:starring || ?prop = dct:subject || ?prop = foaf:name
        )   
    }
    """)

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    list_results = __results_to_dict(movie_id, results)
    return list_results


def __obtain_all_movie_props(movies_set: pd.DataFrame, cols: list):
    """
    Function that obtains the properties of all movies from the dbpedia
    :param movies_set: data set of movies with columns movie id and movie dbpedia uri
    :param cols: columns of data frame with all movie properties
    :return: a data frame with all movie properties
    """
    movies_id = movies_set['movie_id'].to_list()
    movies_id.sort()
    all_movie_props = pd.DataFrame(columns=cols)
    for movie in movies_id:
        movie_uri = movies_set.loc[movie]['dbpedia_uri']
        props_list_dic = __get_props_of_movie_from_dbpedia(movie, movie_uri)
        all_movie_props = all_movie_props.append(props_list_dic, ignore_index=True)
        print("Obtained data of movie: " + str(movie))

    return all_movie_props


def get_all_movie_props(movies_set: pd.DataFrame, flag: int, file_path="./generated_files/all_movie_props.csv"):
    """
    Function that returns the data frame of all movie properties from dbpedia
    :param movies_set: data set of movies with columns movie id and movie dbpedia uri
    :param flag: 0 to generate the data frame from scratch and 1 to read from file
    :param file_path: file path to read if flag is not 0
    :return: the data frame of all movie properties from dbpedia
    """
    cols = ['movie_id', 'prop', 'obj']
    if flag == 0:
        all_movie_props = __obtain_all_movie_props(movies_set, cols)
        all_movie_props.to_csv(file_path, mode='w', header=False, index=False)
    else:
        all_movie_props = pd.read_csv(file_path, header=None)
        all_movie_props.columns = cols

    all_movie_props = all_movie_props.set_index(cols[0])

    return all_movie_props


def __results_to_dict(moive_id: int, props_movie: dict):
    """
    Function that returns vector of dictionaries with the results from the dbpedia to insert into data frame of all
    movie properties
    :param moive_id: movie id of the movie
    :param props_movie: peoperties returned from dbpedia
    :return: vector of dictionaries with the results from the dbpedia
    """
    filter_props = []
    for p in props_movie["results"]["bindings"]:
        dict_props = {'movie_id': moive_id, "prop": p["prop"]["value"], "obj": p["obj"]["value"]}
        filter_props.append(dict_props)

    return filter_props
