import argparse
import random
from pprint import pprint

from gensim.models import KeyedVectors
from gensim.test.utils import datapath
import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE

parser = argparse.ArgumentParser()
parser.add_argument('--path', type=str, help='Path to file with polish word embeddings for word2vec', required=True)
args = parser.parse_args()

wv = KeyedVectors.load_word2vec_format(datapath(args.path), binary=False)

with open(args.path) as opened:
    for _ in range(0, 20):
        print(opened.readline())

result_file = open("results.txt", mode="w", encoding="utf-8")

ex3_input = (
    "sąd::noun wysoki::adj",
    "trybunał::noun konstytucyjny::adj",
    "kodeks::noun cywilny::adj",
    "kpk::noun",
    "sąd::noun rejonowy::adj",
    "szkoda::noun",
    "wypadek::noun",
    "kolizja::noun",
    "szkoda::noun majątkowy::adj",
    "nieszczęście::noun",
    "rozwód::noun",
)

print("# 3")
result_file.write("# 3\n")
for word in ex3_input:
    closest = "{}:\t\t{}".format(word, wv.most_similar(positive=word.split(), topn=1))
    print(closest)
    result_file.write(closest + "\n")

print("# 4")
result_file.write("# 4\n")
print("sąd wysoki - kpc + konstytucja")
result_file.write("sąd wysoki - kpc + konstytucja\n")
vector = np.sum((wv.get_vector("sąd::noun"), wv.get_vector("wysoki::adj"), wv.get_vector("konstytucja::noun"),
                 np.negative(wv.get_vector("kpc::noun"))), axis=0)
computed_result = wv.similar_by_vector(vector=vector, topn=5)
print(computed_result)
result_file.write(str(computed_result))
result_file.write("\n")

print("pasażer - mężczyzna + kobieta")
result_file.write("pasażer - mężczyzna + kobieta\n")
vector = np.sum((wv.get_vector("pasażer::noun"), wv.get_vector("kobieta::noun"),
                 np.negative(wv.get_vector("mężczyzna::noun"))), axis=0)
computed_result = wv.similar_by_vector(vector=vector, topn=5)
print(computed_result)
result_file.write(str(computed_result))
result_file.write("\n")

print("samochód - droga + rzeka")
result_file.write("samochód - droga + rzeka\n")
vector = np.sum((wv.get_vector("samochód::noun"), wv.get_vector("rzeka::noun"),
                 np.negative(wv.get_vector("droga::noun"))), axis=0)
computed_result = wv.similar_by_vector(vector=vector, topn=5)
print(computed_result)
result_file.write(str(computed_result))
result_file.write("\n")

print("# 5")
result_file.write("# 5\n")
wordlist = (
    'szkoda::noun',
    'strata::noun',
    'uszczerbek::noun',
    'szkoda::noun majątkowy::adj',
    'uszczerbek::noun na::prep zdrowie::noun',
    'krzywda::noun',
    'niesprawiedliwość::noun',
    'nieszczęście::noun',
)

highlights = []
for phrase in wordlist:
    try:
        vector = np.sum([wv.get_vector(part) for part in phrase.split()], axis=0)
        highlights.append(vector)
    except KeyError:
        print('{} not in model'.format(phrase))
print('{} highlights found'.format(len(highlights)))
random_vectors = list(map(lambda x: wv.get_vector(x), random.sample(list(wv.vocab.keys()), 1000 - len(highlights))))
processed = TSNE(n_components=2).fit_transform(highlights + random_vectors)

plt.figure(figsize=(10, 10))
plt.scatter(processed[:len(highlights), 0], processed[:len(highlights), 1])
plt.scatter(processed[len(highlights):, 0], processed[len(highlights):, 1])
plt.savefig('tsne.png')
