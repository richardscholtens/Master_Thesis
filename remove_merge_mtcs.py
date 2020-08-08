#!/usr/bin/python3
# student: J.F.P. (Richard) Scholtens
# studentnr.: s2956586
# datum: 25/07/2020
# A program that removes and merges Main Topic Classifications that are
# considered too small to work. By removing Main Topic Classifications
# with a low frequency, one can create a more balanced dataset. By merging
# Main Topic Classifications one can increase the size of the dataset which
# helps improve robustness.


import json


def open_json(file_name):
    """Opens a json file and returns a dictionary."""
    with open(file_name + '.json') as file:
        return json.load(file)


def remove_and_merge_dictionaries(dic, remove_list, merge_list):
    """Removes and merges keys within a dictionary. It then returns
    the dictionary with updated keys."""
    for merge_tup in merge_list:
        dic[merge_tup[0] + '_&_' + merge_tup[1]] = {**dic[merge_tup[0]],
                                                    **dic[merge_tup[1]]}
        remove_list.append(merge_tup[0])
        remove_list.append(merge_tup[1])

    for remove in remove_list:
        dic.pop(remove, None)

    return dic


def main():
    keys = ['Category:Concepts',
            'Category:Mind',
            'Category:Objects',
            'Category:Organizations',
            'Category:People',
            'Category:Policy']
    merge = [('Category:History', 'Category:Events')]
    mtc = open_json('dataset_range2_strategy3_NL')

    dictionary = remove_and_merge_dictionaries(mtc, keys, merge)

    print('INCLUDED MAIN TOPIC CLASSIFICATIONS:\n')
    for label in dictionary.keys():
        print(label)
    print('\nTOTAL LABELS: {0}'.format(len(dictionary)))

    with open('dataset_range_strategy3_NL_merged.json', 'w') as file:
        json.dump(dic, file)


if __name__ == '__main__':
    main()
