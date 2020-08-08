#!/usr/bin/python3
# student: J.F.P. (Richard) Scholtens
# studentnr.: s2956586
# datum: 17/05/2020
# Pre-processes the abstracts to Flair input. It creates files for multi-class
# and multi-label. The Flair library has a class named ClassificationCorpus
# that takes in the following format: __label__LABELNAME TAB TEXT. All text is
# stripped of punctuation using regex. The program also calculates the baseline
# scores using a DummyClassifier developed by SciKit Learn.

import re
import json
import numpy as np
import sklearn.metrics as metrics
from nltk.corpus import stopwords
from collections import defaultdict
from sklearn.pipeline import Pipeline
from sklearn.dummy import DummyClassifier
from sklearn.naive_bayes import MultinomialNB
from retrieve_information import get_categories
from sklearn.metrics import classification_report
from sklearn.multiclass import OneVsRestClassifier
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer


stop_words = set(stopwords.words('english'))


def open_json(file_name):
    """Opens a json file and returns a dictionary."""
    with open(file_name + '.json') as file:
        return json.load(file)


def write_file(file, label, line, chuncks=False, multi_label=False):
    """Removes punctuation of a line and writes that line to a file.
    Checks if must be chopped into chuncks of 200 characters."""

    line = line.strip()
    line = re.sub(r"[^\.a-zA-Z0-9]+", ' ', line)

    if chuncks:
        abstract_chuncks = get_split(line)
        for chunck in abstract_chuncks:
            if multi_label:
                write_line = label[:-1] + '\t' + line + '\n'
            else:
                write_line = label + '\t' + chunck + '\n'
            file.write(write_line)
    else:
        if multi_label:
            write_line = label[:-1] + '\t' + line + '\n'
        else:
            write_line = label + '\t' + line + '\n'
        file.write(write_line)


def write_flair_input_multi_class(dictionary, file_name, chunks=False):
    """Expects a dictionary as input that
    has the following architecture:

    dictionary[topic][category][entity] = abstract

    It writes the in data to a flair input namely:

    __label__LABELNAME TAB TEXT
    """
    with open(file_name, 'w+') as file:
        for topic, category in dictionary.items():
            label = '__label__' + topic
            for entity, abstract in category.items():
                for key, val in abstract.items():
                    write_file(file, label, val, chunks)


def write_flair_input_multi_label(dictionary, file_name, chunks=False):
    """Expects a dictionary as input that
    has the following architecture:

    dictionary[abstract] = [labels]

    It writes the in data to a flair input namely:

    __label__LABELNAME TAB TEXT

    If multiple labels detected it becomes similar to:

    __label__LABELNAME __label__LABELNAME TAB TEXT

    """
    with open(file_name, 'w+') as file:

        for abstract, labels in dictionary.items():
            write_line = ''
            for label in labels:
                label += label + ' '
            write_file(file, label, abstract, chunks, True)


def get_split(text):
    """Splits text in chunks of 200 characters and returns
    a list with these chunks as elements."""
    total = []
    l_parcial = []
    if len(text.split()) // 150 > 0:
        n = len(text.split())//150
    else:
        n = 1
    for w in range(n):
        if w == 0:
            l_parcial = text.split()[:200]
            total.append(" ".join(l_parcial))
        else:
            l_parcial = text.split()[w*150:w*150 + 200]
            total.append(" ".join(l_parcial))
    return total


def create_train_dev_test(file_name):
    """Takes in a textfile as input and randomizes the text.
    It returns a training, development and test text file.
    """
    X = []
    Y = []
    with open(file_name, "r") as d:
        for line in d:
            line = line.split("\t", 1)
            X.append(line[1])
            Y.append(line[0])

    X_train, X_test, Y_train, Y_test = train_test_split(X,
                                                        Y,
                                                        test_size=0.2,
                                                        random_state=1)
    # 0.25 x 0.8 = 0.2
    X_train, X_val, Y_train, Y_val = train_test_split(X_train,
                                                      Y_train,
                                                      test_size=0.25,
                                                      random_state=1)

    with open("flair_train.txt", "w") as training:
        for sentence, label in zip(X_train, Y_train):
            training.write(label + "\t" + sentence)
    print('done with train')

    with open("flair_dev.txt", "w") as developing:
        for sentence, label in zip(X_val, Y_val):
            developing.write(label + "\t" + sentence)
    print('done with dev')

    with open("flair_test.txt", "w") as testing:
        for sentence, label in zip(X_test, Y_test):
            testing.write(label + "\t" + sentence)
    print('done with test')

    return X_train, Y_train, X_val, Y_val, X_test, Y_test


def print_scores(y_true, y_pred, average='macro'):
    """Calculates accuracy, precison, recall, F1-scores and.
    then prints te results."""
    print('Printing {} scores...\n'.format(average))
    print('PRECISION: {0}'.format(metrics.precision_score(y_true=y_true,
                                                          y_pred=y_pred,
                                                          average=average,
                                                          zero_division=1)))
    print('RECALL: {0}'.format(metrics.recall_score(y_true=y_true,
                                                    y_pred=y_pred,
                                                    average=average,
                                                    zero_division=1)))
    print('F1-scores: {0}'.format(metrics.f1_score(y_true=y_true,
                                                   y_pred=y_pred,
                                                   average=average,
                                                   zero_division=1)))
    print('ACCURACY: {0}\n'.format(metrics.accuracy_score(y_true, y_pred)))
    print('Printing classification report')
    print(classification_report(y_true, y_pred, digits=4, zero_division=1))


def get_baseline(X_train, Y_train, X_val, Y_val, X_test, Y_test):
    """Calculates accuracy, precison, recall, F1-scores."""

    dummy_clf = DummyClassifier(strategy="most_frequent")
    dummy_clf.fit(X_train, Y_train)
    prediction_development = dummy_clf.predict(X_val)
    prediction_test = dummy_clf.predict(X_test)

    print('CALCULATING DEVELOPMENT SCORES DUMMYCLASSIFIER.\n')
    print_scores(Y_val, prediction_development)
    print_scores(Y_val, prediction_development, 'micro')

    print('CALCULATING TEST SCORES DUMMYCLASSIFIER.\n')
    print_scores(Y_test, prediction_test)
    print_scores(Y_test, prediction_test, 'micro')

    # Optional baseline:
    # Define a pipeline combining a text feature extractor with multi lable
    # classifier.
    NB_pipeline = Pipeline([
                    ('tfidf', TfidfVectorizer(stop_words=stop_words)),
                    ('clf', OneVsRestClassifier(MultinomialNB(
                        fit_prior=True, class_prior=None))),
                ])

    NB_pipeline.fit(X_train, Y_train)
    prediction_development = NB_pipeline.predict(X_val)
    prediction_test = NB_pipeline.predict(X_test)

    print('CALCULATING DEVELOPMENT SCORES NB_PIPLINE.\n')
    print_scores(Y_val, prediction_development)
    print_scores(Y_val, prediction_development, 'micro')

    print('CALCULATING TEST SCORES NB_PIPLINE.\n')
    print_scores(Y_test, prediction_test)
    print_scores(Y_test, prediction_test, 'micro')


def change_to_multi_label(dictionary):
    """Makes a new dictionary that holds the abstracts as key and a list of
    labels as value."""
    dic = defaultdict(list)
    for topic, category in dictionary.items():
        for entity, abstract in category.items():
            for key, value in abstract.items():
                label = '__label__' + topic
                dic[value].append(label)
    return dic


def main():
    mtc = open_json('dataset_range_strategy3_NL_merged')

    # Only needed when choosing multi-class.
    write_flair_input_multi_class(mtc, 'flair_input_dataset_range_strategy3_NL_multiclass.txt')
    write_flair_input_multi_class(mtc, 'flair_input_dataset_range_strategy3_NL_multiclass_BERT.txt', True)
    X_train, Y_train, X_val, Y_val, X_test, Y_test = create_train_dev_test('flair_input_dataset_range_strategy3_NL_multiclass_BERT.txt')
    get_baseline(X_train, Y_train, X_val, Y_val, X_test, Y_test)

    # Only needed when choosing multi-label.
    multi_label = change_to_multi_label(mtc)
    write_flair_input_multi_label(multi_label, 'flair_input_dataset_range_strategy3_NL.txt')
    write_flair_input_multi_label(multi_label, 'flair_input_dataset_range_strategy3_NL_BERT.txt', True)
    X_train, Y_train, X_val, Y_val, X_test, Y_test = create_train_dev_test('flair_input_dataset_range_strategy3_NL_BERT.txt')
    get_baseline(X_train, Y_train, X_val, Y_val, X_test, Y_test)


if __name__ == '__main__':
    main()
