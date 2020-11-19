from SPARQLWrapper import SPARQLWrapper, JSON

# utils sparql functions lib


def get_props_from_dbpedia(movie_uri: str, exclusions: list):
    """
    Function that obtains the tuples (properties, resources) of a movie form its' uri
    :param movie_uri: path to the movie resource from dbpedia
    :param exclusions: list of properties to ignore
    :return: list with properties of movies
    """

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

    list_results = __filter_results(results, exclusions)
    return list_results


def __filter_results(props_movie: dict, exclusions: list):
    """
    Function that filter the results from sparql call
    :param props_movie: dictionary with all connections of the movies
    :param exclusions: list with properties to be excluded
    :return: filtered list with properties of movies
    """

    filter_props = []
    for p in props_movie["results"]["bindings"]:
        if p["prop"]["value"] not in exclusions:
            filter_props.append((p["prop"]["value"], p["obj"]["value"]))

    return filter_props
