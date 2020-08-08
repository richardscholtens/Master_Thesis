#!/usr/bin/python3
# student: J.F.P. (Richard) Scholtens
# studentnr.: s2956586
# datum: 08/08/2020
# This program retrieves information about Wikipedia's Main Topic
# Classification articles by using four different collection strategies.
# Information is retrieved using SPARQL-queries to extract Dutch abstract data
# per article from DBpedia. All information retrieved is then converted to a
# JSON file.


from SPARQLWrapper import SPARQLWrapper, JSON
import json
from collections import defaultdict


def get_categories():
    """Includes all 41 Main Topic Classifications (MTC) that has subcategories
    and returns a list of categories."""
    categories = ["Category:Academic_disciplines",
                  "Category:Business",
                  "Category:Concepts",
                  "Category:Crime",
                  "Category:Culture",
                  "Category:Economy",
                  "Category:Education",
                  "Category:Energy",
                  "Category:Engineering",
                  "Category:Entertainment",
                  "Category:Events",
                  "Category:Food_and_drink",
                  "Category:Geography",
                  "Category:Government",
                  "Category:Health",
                  "Category:History",
                  "Category:Human_behavior",
                  "Category:Humanities",
                  "Category:Industry",
                  "Category:Knowledge",
                  "Category:Language",
                  "Category:Law",
                  "Category:Life",
                  "Category:Mass_media",
                  "Category:Mathematics",
                  "Category:Military",
                  "Category:Mind",
                  "Category:Music",
                  "Category:Nature",
                  "Category:Objects",
                  "Category:Organizations",
                  "Category:People",
                  "Category:Philosophy",
                  "Category:Policy",
                  "Category:Politics",
                  "Category:Religion",
                  "Category:Science",
                  "Category:Society",
                  "Category:Sports",
                  "Category:Technology",
                  # "Category:Universe", THIS ONE DOES NOT HOLD ANY CATEGORIES
                  "Category:World"]
    return categories


def get_statistics(sample):
    """Prints the frequency, sum, mean, standard deviation,
    variance and margin of error. It then returns these values,
    including two range points for the margin of error."""
    frequency = len(sample)
    total_sum = sum(sample)
    mean = round(np.mean(sample))
    sd = round(statistics.stdev(sample))
    var = round(statistics.variance(sample))
    range_1 = mean - sd
    range_2 = mean + sd

    print('FREQUENCY SAMPLES: {0}'.format(frequency))
    print('SUM OF ALL SAMPLES: {0}'.format(total_sum))
    print('MEAN: {0}'.format(mean))
    print('STANDARD DEVIATION: {0}'.format(sd))
    print('VARIANCE: {0}'.format(var))

    return frequency, total_sum, mean, sd, var, range_1, range_2


def retrieve_info(ent, query, abstract=False):
    """This function returns a set of values according to the given query.
    If the value is a hyperlink, it slices the last part as
    and stores it as the value."""
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    values = set()
    for result in results["results"]["bindings"]:
        value = result["value"]["value"]
        if not abstract:
            value = value.rsplit('/', 1)[-1]
        values.add(value)
    return values


def collect_is_skos_broader_of(entity):
    """Creates a SPARQL-query using the following DBpedia property:

        is skos:broader of

        It then returns a list with the information.
    """

    query = """SELECT * WHERE { <http://dbpedia.org/resource/%s>
                     ^skos:broader
                    ?value .}""" % entity
    info = retrieve_info(entity, query)
    return info


def collect_is_subject_of(entity):
    """Creates a SPARQL-query using the following DBpedia property:

        is dct:subject of

        It then returns a list with the information.
    """

    query = """SELECT * WHERE { <http://dbpedia.org/resource/%s>
            ^<http://purl.org/dc/terms/subject>
            ?value .}""" % entity
    info = retrieve_info(entity, query)
    return info


def collect_dbo_abstract(entity):
    """Creates a SPARQL-query using the following DBpedia property:

        dbo:abstract

        It then returns a list with the information.
    """
    query = """SELECT * WHERE { <http://dbpedia.org/resource/%s>
        <http://dbpedia.org/ontology/abstract> ?value .
        FILTER langMatches(lang(?value),'nl')}""" % entity
    info = retrieve_info(entity, query, True)
    return info


def collect_dct_subject(entity):
    """Creates a SPARQL-query using the following DBpedia property:

        dct:subject

        It then returns a list with the information.
    """
    query = """SELECT * WHERE { <http://dbpedia.org/resource/%s>
      <http://purl.org/dc/terms/subject>
      ?value .}""" % entity
    info = retrieve_info(entity, query)
    return info


def check_range(counter, maximum_range):
    """Checks if the counter is equal to the maximum range.
    The function then returns a boolean accordingly with True or False."""
    if counter == maximum_range:
        print("ENOUGH INFORMATION HAS BEEN GATHERED.\n")
        return True
    else:
        return False


def check_size(dictionary, minimum_range=0):
    """Shows how the data is distributed and checks it meets the minimum
    range."""
    print('CHECKING ENTITY FREQUENCY PER TOPIC.')
    print('MUST BE HIGHER THAN MINIMUM RANGE OF: {0}\n'.format(minimum_range))
    counter = 0
    print("{0:30}{1:30}{2:30}\n".format('TOPIC:', 'FREQUENCY:', 'RESULT:'))
    for topic, cat in dictionary.items():
        for category, entities in cat.items():
            for entity, abstract in entities.items():
                counter += 1
        if counter >= minimum_range:
            result = 'SUCCESS'
        else:
            result = 'FAILURE'
        print("{0:30}{1:<30}{2:<30}".format(topic, counter, result))
        counter = 0


def collection_strategy1(topic, dic, counter, max_range=99999999):
    """Retrieves abstracts of all entities of a specific
    category of the main topic classification and returns a dictionary
    with the following architecture:

    dictionary[topic][category][entity] = abstract

    Returns a dictionary and a boolean to see if enough entities were
    collected.

    MTC topic -> is skos:broader of -> category -> is dct:subject of -> entity
    -> dbo:abstract -> abstract

    """
    print("START COLLECTION STRATEGY 1.")
    print("TOPIC:\t{0}".format(topic))

    info = collect_is_skos_broader_of(topic)

    for category in list(info):

        print("SUBCATEGORY:\t{0}\n".format(category))

        entities = collect_is_subject_of(category)

        for entity in entities:

            if check_range(counter, max_range):
                return dic, True, counter

            abstracts = collect_dbo_abstract(entity)
            for abstract in abstracts:
                print("ENTITY: {0}\n".format(entity))
                print("ABSTRACT: {0}\n\n".format(abstract))
                dic[topic][category][entity] = abstract
                counter += 1

    print("MORE INFORMATION MUST BE RETRIEVED FOR THIS TOPIC.")
    return dic, False, counter


def collection_strategy2(topic, dic, counter, max_range=99999999):
    """Retrieves abstracts of all entities of a specific
    category of the main topic classification and returns a dictionary
    with the following architecture:

    dictionary[topic][category][entity] = abstract

    Returns a dictionary and a boolean to see if enough entities were
    collected.

    MTC topic -> is skos:broader -> category -> is dct:subject of -> entity
    -> is skos:broader of -> category -> is dct:subject of -> entity
    -> dbo:abstract -> abstract
    """

    print("START COLLECTION STRATEGY 2.")
    print("TOPIC:\t{0}".format(topic))

    info = collect_is_skos_broader_of(topic)

    for higher_category in list(info):
        print("SUBCATEGORY:\t{0}\n".format(higher_category))
        higher_entities = collect_is_subject_of(higher_category)
        for high_entity in higher_entities:
            print("HIGHER ENTITY: {0}\n".format(high_entity))
            try:
                info = collect_is_skos_broader_of(high_entity)
                for lower_category in list(info):
                    if lower_category not in higher_category.keys():
                        print("SUBCATEGORY:\t{0}\n".format(lower_category))
                        lower_entities = collect_is_subject_of(lower_category)

                        for low_entity in lower_entities:

                            if check_range(counter, max_range):
                                return dic, True, counter

                            abstracts = collect_dbo_abstract(low_entity)
                            for abstract in abstracts:
                                print("LOWER ENTITY: {0}\n".format(low_entity))
                                print("ABSTRACT: {0}\n\n".format(abstract))
                                dic[topic][lower_category][entity2] = abstract
                                counter += 1
            except:
               pass

    print("MORE INFORMATION MUST BE RETRIEVED FOR THIS TOPIC.")
    return dic, False, counter


def collection_strategy3(topic, dic, counter, max_range):
    """Retrieves abstracts of all entities of a specific
    category of the main topic classification and returns a dictionary
    with the following architecture:

    dictionary[topic][category][entity] = abstract

    Returns a dictionary and a boolean to see if enough entities were
    collected.

    MTC topic -> is dct:subject of -> relational entity -> dbo:abstract
    -> abstract
    """
    print("START COLLECTION STRATEGY 3.")
    print("TOPIC:\t{0}".format(topic))

    info = collect_is_subject_of(topic)
    categories = get_categories()

    category_dic = dic[topic]
    entities = category_dic.values()

    for entity in list(info):
        if check_range(counter, max_range):
            return dic, True, counter

        if entity not in entities:

            abstracts = collect_dbo_abstract(entity)

            for abstract in abstracts:
                print("RELATIONAL ENTITY: {0}\n".format(entity))
                print("ABSTRACT: {0}\n\n".format(abstract))
                replace_category = entity + '_' + str(counter)
                dic[topic][replace_category][entity] = abstract
                counter += 1

    print("MORE INFORMATION MUST BE RETRIEVED FOR THIS TOPIC.")
    return dic, False, counter


def collection_strategy4(topic, dic, counter, max_range):
    """Retrieves abstracts of all entities of a specific
    category of the main topic classification and returns a dictionary
    with the following architecture:

    dictionary[topic][category][entity] = abstract

    Returns a dictionary and a boolean to see if enough entities were
    collected.

    MTC topic -> is dct:subject of -> relational entity -> dct:subject
    -> supercategory -> is dct:subject of -> entity -> dbo:abstract -> abstract
    """
    print("START COLLECTION STRATEGY 4.")
    print("TOPIC:\t{0}".format(topic))

    info = collect_is_subject_of(topic)
    categories = get_categories()

    category_dic = dic[topic]
    old_entities = category_dic.values()

    for relational_entity in list(info):
        print("RELATIONAL ENTITY: {0}\n".format(relational_entity))
        relational_entities = collect_dct_subject(relational_entity)

        for subject in relational_entities:
            print("SUPERCATEGORY: {0}\n".format(subject))

            if subject not in old_entities and subject not in categories:

                entities = collect_is_subject_of(subject)

                for entity in entities:

                    if check_range(counter, max_range):
                        return dic, True, counter
                    try:
                        abstracts = collect_dbo_abstract(entity)
                        for abstract in abstracts:
                            print("ENTITY: {0}\n".format(entity))
                            print("ABSTRACT: {0}\n\n".format(abstract))
                            dic[topic][subject][entity] = abstract
                            counter += 1
                    except:
                        pass

    print("MORE INFORMATION MUST BE RETRIEVED FOR THIS TOPIC.")
    return dic, False, counter


def main():
    # The sample frequencies below were retrieved without using
    # a margin error range going through the classifications in the for loop.
    # sample = sorted([235,
                        # 511,
                        # 61,
                        # 238,
                        # 365,
                        # 119,
                        # 326,
                        # 184,
                        # 130,
                        # 346,
                        # 77,
                        # 229,
                        # 225,
                        # 447,
                        # 361,
                        # 239,
                        # 595,
                        # 489,
                        # 360,
                        # 295,
                        # 247,
                        # 124,
                        # 98,
                        # 105,
                        # 192,
                        # 95,
                        # 70,
                        # 175,
                        # 130,
                        # 41,
                        # 64,
                        # 50,
                        # 107,
                        # 31,
                        # 311,
                        # 337,
                        # 258,
                        # 177,
                        # 174,
                        # 220,
                        # 99])

    # freq, sum, mean, sd, var, min_range, max_range = get_statistics(sample)
    # Range has been set by using the commented code above.
    min_range = 79
    max_range = 357

    classifications = get_categories()
    dic = defaultdict(lambda: defaultdict(lambda: defaultdict(str)))

    print("MARGIN OF ERROR RANGE: {0} - {1}\n".format(min_range, max_range))

    for classification in classifications:
        classification = classification.strip()

        dic, check, counter = collection_strategy1(classification,
                                                   dic,
                                                   0,
                                                   max_range)
        if not check:
            dic, check, counter = collection_strategy2(classification,
                                                       dic,
                                                       counter,
                                                       max_range)
            if not check:
                dic, check, counter = collection_strategy3(classification,
                                                           dic,
                                                           counter,
                                                           max_range)

                if not check:
                    dic, check, counter = collection_strategy4(classification,
                                                               dic,
                                                               counter,
                                                               max_range)

    check_size(dic, min_range)

    with open('dataset_max_range_357_all_strategies_NL.json', 'w') as fp:
        json.dump(dic, fp)


if __name__ == '__main__':
    main()
