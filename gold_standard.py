#!/usr/bin/python3
# student: J.F.P. (Richard) Scholtens
# studentnr.: s2956586
# datum: 17/05/2020
# This programs reads two annotation files and processes them to calculate the
# Kappa-score. It also creates a gold standard by unifying the annotation
# labels of both annotation files. An annotation
# text file should have the following format:

# SENTENCE: TAB PDF -bestand over de rivier
# ENTITY 1: TAB PDF
# ANSWER 1: TAB Category:Technology TAB Category:Science


from collections import defaultdict
from flair.data import Sentence


def retrieve_annotations(file_path):
    """This function reads an annotation file and creates two types of
    dictionaries. The first one uses entities as keys and uses a list of
    annotation labels as value. The second one uses sentences as key and a
    a tuple containing a list with entities and a list of annotation labels as
    value."""
    dic = defaultdict(list)
    sentence_dic = defaultdict(tuple)

    sentence = False

    entities = []
    answers = []

    entity_lst = []
    answer_lst = []
    with open(file_path, 'r') as file:

        for line in file.readlines():
            line = line.strip()
            lst = line.split('\t')
            if len(lst) > 0:
                if lst[0] == 'SENTENCE:':
                    if sentence:
                        sentence_dic[sentence] = (entities, answers)
                        entities = []
                        answers = []

                    sentence = lst[1]

                elif lst[0][:6] == 'ENTITY':
                    entity = lst[1]
                    entities.append(lst[1])
                    entity_lst.append(lst[1])

                elif lst[0][:6] == 'ANSWER':
                    answer = lst[1:]

                    answers.append(lst[1:])
                    answer_lst.append(lst[1:])
        sentence_dic[sentence] = (entities, answers)
        entities = []
        answers = []

    for entity, answer in zip(entity_lst, answer_lst):

        dic[entity] = answer
    return dic, sentence_dic


def calculate_kappa(dic1, dic2):
    """Calculates the kappa score. This function takes in two dictionaries as
    with entity as key and label(s) as values. If there is agreement about at
    least one label it will be seen as a correct annotation."""
    lst1 = []
    lst2 = []
    for entity in dic1.keys():
        lst1.append((entity, dic1[entity]))
        lst2.append((entity, dic2[entity]))

    agree = e = 0
    d1, d2 = defaultdict(int), defaultdict(int)
    for el1, el2 in zip(lst1, lst2):

        intersect = list(set(el1[1]) & set(el2[1]))
        agree += 1 if len(intersect) > 0 else 0
        d1[el1[0]] += 1
        d2[el2[0]] += 1
    a = agree / sum(d1.values())
    for k, v in d1.items():
        e += (v / sum(d1.values())) * (d2[k] / sum(d1.values()))
    print('AGREE FREQUENCY: ', agree)
    print(round((a - e) / (1 - e) * 100, 2), "%")


def create_gold_standard(dic1, dic2):
    """This function takes in two dictionaries with annotations.
    A dictionary key is equivalent to a sentence and the value
    to a list with annotation labels."""
    gold_standard = defaultdict(tuple)
    lst1 = []
    lst2 = []
    c = 0
    with open('MISC_sentences_100_gold_standard_union.txt', 'w+') as file:
        for sentence in dic1.keys():
            tup1 = dic1[sentence]
            tup2 = dic2[sentence]
            file.write('SENTENCE:\t{0}\n'.format(sentence))
            entities = tup1[0]
            for entity, i in zip(entities, range(len(entities))):
                file.write(('ENTITY:\t{0}\n'.format(entity)))

                file.write('ANSWER:\t')

                # Use this code if you want unified gold standard.
                union = list(set(tup1[1][i]).union(set(tup2[1][i])))
                for ii in range(len(union)):
                    print(union[ii])
                    file.write('{0}\t'.format(union[ii]))
                file.write('\n')

                # Use this code if you want intersected gold standard.
                # intersect = list(set(tup1[1][i]) & set(tup2[1][i]))
                # for ii in range(len(intersect)):
                #     #file.write('{0}\t'.format(intersect[ii]))
                # file.write('\n')


def main():
    dictionary_amber, sentence_amber = retrieve_annotations('MISC_sentences_100_Amber.txt')
    dictionary_rolf, sentence_rolf = retrieve_annotations('MISC_sentences_100_Rolf.txt')

    calculate_kappa(dictionary_amber, dictionary_rolf)
    create_gold_standard(sentence_amber, sentence_rolf)


if __name__ == '__main__':
    main()
