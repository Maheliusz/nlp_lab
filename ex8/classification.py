import argparse
import os
import random

import fasttext
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report
from sklearn.model_selection import GridSearchCV
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str, help='Path to text files with bills', required=True)
    parser.add_argument('--variant', type=str, help='Variant of program to run', required=True)
    args = parser.parse_args()

    normal_training_dir = os.listdir(args.path + 'normal/training/')
    normal_testing_dir = os.listdir(args.path + 'normal/testing/')
    normal_validation_dir = os.listdir(args.path + 'normal/validation/')

    zmiana_training_dir = os.listdir(args.path + 'zmiana/training/')
    zmiana_testing_dir = os.listdir(args.path + 'zmiana/testing/')
    zmiana_validation_dir = os.listdir(args.path + 'zmiana/validation/')


    def split(a, n):
        k, m = divmod(len(a), n)
        return [a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]


    feature_extraction = TfidfVectorizer()


    def process_lines(contents):
        result = []
        for file_contents in contents:
            if args.variant == 'full':
                result.append(' '.join(file_contents))
            elif args.variant == 'percent':
                result.append(' '.join(random.sample(file_contents, len(file_contents) // 10)))
            elif args.variant == 'ten':
                result.append(' '.join(random.sample(file_contents, min(len(file_contents), 10))))
            elif args.variant == 'one':
                result.append(' '.join(random.sample(file_contents, min(len(file_contents), 1))))
            else:
                exit()
        return result


    training_data = process_lines(
        [open(args.path + 'normal/training/' + filename, encoding='utf-8').readlines() for filename in
         normal_training_dir] +
        [open(args.path + 'zmiana/training/' + filename, encoding='utf-8').readlines() for filename in
         zmiana_training_dir])
    testing_data = process_lines(
        [open(args.path + 'normal/testing/' + filename, encoding='utf-8').readlines() for filename in
         normal_testing_dir] +
        [open(args.path + 'zmiana/testing/' + filename, encoding='utf-8').readlines() for filename in
         zmiana_testing_dir])
    validation_data = process_lines(
        [open(args.path + 'normal/validation/' + filename, encoding='utf-8').readlines() for filename in
         normal_validation_dir] +
        [open(args.path + 'zmiana/validation/' + filename, encoding='utf-8').readlines() for filename in
         zmiana_validation_dir])

    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer()),
        ('clf', OneVsRestClassifier(LinearSVC())),
    ])
    parameters = {
        'tfidf__max_df': (0.25, 0.5, 0.75),
        'tfidf__ngram_range': [(1, 1), (1, 2), (1, 3)],
        "clf__estimator__C": [0.01, 0.1, 1],
        "clf__estimator__class_weight": ['balanced', None],
    }

    with open('model.txt', 'w', encoding='utf-8') as file:
        counter = 0
        for file_contents in training_data:
            file.write('{} {}\n'.format('__label__normal' if counter < len(normal_training_dir) else '__label__changed',
                                        file_contents.replace('\n', ' ')))
            counter += 1

    grid_search_tune = GridSearchCV(
        pipeline, parameters, cv=2, n_jobs=2, verbose=3)
    grid_search_tune.fit(training_data, ['normal'] * len(normal_training_dir) + ['changed'] * len(zmiana_training_dir))

    print("Best parameters set:")
    print(grid_search_tune.best_estimator_.steps)

    # measuring performance on test set
    print("Applying best classifier on test data:")
    best_clf = grid_search_tune.best_estimator_
    predictions = best_clf.predict(testing_data)

    print(classification_report(['normal'] * len(normal_testing_dir) + ['changed'] * len(zmiana_testing_dir),
                                predictions))

    classifier = fasttext.supervised('model.txt', 'model', label_prefix="__label__")

    labels = list(zip(classifier.predict(testing_data),
                      ['normal'] * len(normal_testing_dir) + ['changed'] * len(zmiana_testing_dir)))
    true_positive = 0
    false_positive = 0
    false_negative = 0
    for label in labels:
        if label[1] == 'changed':
            if label[0][0] == 'changed':
                true_positive += 1
            else:
                false_negative += 1
        else:
            if label[0][0] == 'changed':
                false_positive += 1

    precision = true_positive / (true_positive + false_positive)
    recall = true_positive / (true_positive + false_negative)
    f1 = 2 * (precision * recall) / (precision + recall)
    print('{}\t\t{}\t\t{}'.format('Precision', 'Recall', 'F1'))
    print('{0:.5f}\t\t{0:.5f}\t\t{0:.5f}'.format(precision, recall, f1))
