import argparse
import math
from pprint import pprint

import regex as re

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
                        "morfologik_stem",
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


pointwise_mutual_information = {k: pmi(unigrams[k.split()[0]], unigrams[k.split()[1]], v) for k, v in
                                bigrams.items()}
pprint(list(sorted(pointwise_mutual_information.items(), key=lambda kv: kv[1], reverse=True))[:30])
