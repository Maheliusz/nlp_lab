import argparse
import math
from collections import Counter
from pprint import pprint

from res import llr  # https://github.com/tdunning/python-llr

from utils.utils import initialize_elastic, open_directory

parser = argparse.ArgumentParser()
parser.add_argument('--path', type=str, help='Path to text files with bills', required=True)
parser.add_argument('--address', type=str, help='Address to send requests to', required=True)
parser.add_argument('--reset', help='Should the indexes be reset', required=False, action="store_true")
args = parser.parse_args()

INDEX_NAME = 'legislatives'
TYPE = 'text'

es = initialize_elastic(address=args.address, path=args.path, settings={
    "settings": {
        "analysis": {
            "filter": {
                "my_shingle_filter": {
                    "type": "shingle",
                    "min_shingle_size": 2,
                    "max_shingle_size": 2
                }
            },
            "analyzer": {
                "custom_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "my_shingle_filter",
                        # "morfologik_stem",
                    ]
                }
            }
        }
    },
    "mappings": {
        "text": {
            "properties": {
                "text": {
                    "term_vector": "yes",
                    "type": "text",
                    "analyzer": "custom_analyzer"
                }
            }
        }
    }
}, reset=args.reset, index_name=INDEX_NAME, doc_type=TYPE, index_counter=True, remove_non_alphanumeric=True)

directory_contents = open_directory(args.path)
tmp_dict = {}
prev = 0
for x in range(100, len(directory_contents), 100):
    ids = list(map(lambda x: str(x), range(prev, x)))
    tmp_dict.update(es.mtermvectors(index=INDEX_NAME, doc_type=TYPE, term_statistics=True, ids=ids))
    prev = x
frequencies = {}
for entry in tmp_dict['docs']:
    term_vectors = entry['term_vectors']['text']['terms']
    for key, value in term_vectors.items():
        frequencies[key] = value['term_freq'] if key not in frequencies else frequencies[key] + value['term_freq']
unigrams = {k: v for k, v in frequencies.items() if len(k.split()) == 1}
bigrams = {k: v for k, v in frequencies.items() if len(k.split()) == 2}


def pmi(x, y, xy):
    return math.log(xy / (x * y))


unigrams_sum = sum(unigrams.values())
bigrams_sum = sum(bigrams.values())
pointwise_mutual_information = {
    k: pmi(unigrams[k.split()[0]] / unigrams_sum, unigrams[k.split()[1]] / unigrams_sum, v / bigrams_sum)
    for k, v in bigrams.items()}
print('Pointwise mutual information')
pprint(list(sorted(pointwise_mutual_information.items(), key=lambda kv: kv[1], reverse=True))[:30])

diff = llr.llr_compare(Counter(bigrams), Counter(unigrams))
print('Log likelihood ratio')
pprint(list(sorted(diff.items(), key=lambda kv: kv[1], reverse=True))[:30])

print("Which measure works better for the problem?")
print("LLR > PMI")

print('What would be needed, besides good measure, to build a dictionary of multiword expressions?')
print()

print('Can you identify a certain threshold which clearly divides the good expressions from the bad?)')
print()
