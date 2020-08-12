# Master_Thesis
Multi-label classification of unclassifiednamed entities usingWikipedia’s main topic classifications.

This research set out to see if it is possible to create an efficient and accurate
fine-grained named entity multi-label classification system using Wikipedia’s Main
Topic Classifications as labels. Creating such a system will help other academics to
improve existing data sets by adding new generalized labels for unknown named
entities. By using four different data collections strategies information about 7991
entities spread out over 34 Main Topic Classifications for the Dutch language is
gathered. Every one of these classifications has subcategories that hold information
about a specific topic within the Main Topic Classification. Two annotators created
a gold standard using MISC entities out of the SoNaR1-corpus, resulting in Kappascore 
of 0.8182. Using fine-tuned bidirectional LSTM models in combination with
GloVe and BERTje embeddings, one can perform multi-label classification based
upon chunks of texts as input. The best text classification was an LSTM model using
BERTje embeddings and resulted in an accuracy of 44,01%, a macro F1-score of 86,31
and a micro F1-score of 97,91%. Another LSTM model used GloVe embeddings resulting in 
an accuracy of 37,74%, a macro F1-score of 89,87%, and a micro F1-score 97,60%. 
All models performed the same multi-label named entity classification task
and were evaluated on the gold standard resulting in an accuracy score of 70%,
macro F1-score of 9,26%, and a micro F1-score of 12,45% for the LSTM using GloVe
embeddings and accuracy of 91%, macro F1-score of 8,72% and a micro F1-score
of 12,45% for the LSTM using BERTje embeddings. One must conclude that the
Dutch Main Topic Classification articles are suitable to create a dataset for training a
fine-grained multi-label named entity classification model if one takes the proper removing,
merging and pruning steps. Therefore the performed methods succeeded
in developing fine-grained entity multi-label classifications system but could not be
considered robust enough. Therefor more information retrieval methods and optimization steps
should be considered in future research. 

## Scraping DBpedia using SPARQL-queries - retrieve_information.py

This program retrieves information about Wikipedia's Main Topic
Classification articles by using four different collection strategies.
Information is retrieved using SPARQL-queries to extract Dutch abstract data
per article from DBpedia. All information retrieved is then converted to a
JSON file. One has to note that DBpedia is a dynamic database, and thus the
frequencies of articles per MTC written in the thesis may vary over time. 

## Removing and merging Main Topic Classification articles - remove_merge_mtcs.py

A program that removes and merges Main Topic Classifications that are
considered too small to work. By removing Main Topic Classifications
with a low frequency, one can create a more balanced dataset. By merging
Main Topic Classifications one can increase the size of the dataset which
helps improve robustness.

## Pre-processing and calculating baseline scores - pre-processing_and_baseline.py

Pre-processes the abstracts to Flair input. It creates files for multi-class
and multi-label. The Flair library has a class named ClassificationCorpus
that takes in the following format: __label__LABELNAME TAB TEXT. All text is
stripped of punctuation using regex. The program also calculates the baseline
scores using a DummyClassifier developed by SciKit Learn.

## Calculating the Kappa-score and creating a gold standard - gold_standard.py

This programs reads two annotation files and processes them to calculate the
Kappa-score. It also creates a gold standard by unifying the annotation
labels of both annotation files. An annotation
text file should have the following format:

SENTENCE: TAB PDF -bestand over de rivier
ENTITY 1: TAB PDF
ANSWER 1: TAB Category:Technology TAB Category:Science

## Training and evaluating the Flair LSTM models - training_evaluation.ipynb

This programs converts the Flair input texts (flair_train.txt, flair_dev.txt and flair_test.txt) into
classification corpus. This is than converted to document embeddings for the LSTM models. By doing so
the training process can take place. After creating the models the program can evaluate a system by 
making predictions on the gold standard.
