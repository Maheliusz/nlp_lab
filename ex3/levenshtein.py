import argparse
from pprint import pprint

import matplotlib.pyplot as plt
import Levenshtein as lev

from utils.utils import initialize_elastic, open_directory

parser = argparse.ArgumentParser()
parser.add_argument('--path', type=str, help='Path to text files with bills', required=True)
parser.add_argument('--dict_path', type=str, help='Path to text file with dictionary', required=True)
parser.add_argument('--address', type=str, help='Address to send requests to', required=True)
parser.add_argument('--reset', help='Should the indexes be reset', required=False, action="store_true")
args = parser.parse_args()

INDEX_NAME = 'legislatives'
TYPE = 'text'

es = initialize_elastic(address=args.address, path=args.path, settings={
    "settings": {
        "analysis": {
            "analyzer": "morfologik",
            "filter": ["lowercase"]
        }
    },
    "mappings": {
        "text": {
            "properties": {
                "text": {
                    "term_vector": "yes",
                    "type": "text",
                    "analyzer": "morfologik"
                }
            }
        }
    }
}, reset=args.reset, index_name=INDEX_NAME, doc_type=TYPE, index_counter=True)

directory_contents = open_directory(args.path)
tmp_dict = {}
prev = 0
for x in range(500, len(directory_contents), 500):
    ids = list(map(lambda x: str(x), range(prev, x)))
    tmp_dict.update(es.mtermvectors(index=INDEX_NAME, doc_type=TYPE, term_statistics=True, ids=ids))
    prev = x
frequencies = {}
for entry in tmp_dict['docs']:
    term_vectors = entry['term_vectors']['text']['terms']
    for key, value in term_vectors.items():
        if key.isalpha():
            frequencies[key] = value['term_freq'] if key not in frequencies else frequencies[key] + value['term_freq']
frequencies = {k: v for k, v in frequencies.items() if k.isalpha() and len(k) > 1}
frequency_list = sorted(frequencies.values(), reverse=True)
plt.loglog(list(range(len(frequency_list))), frequency_list)
plt.grid(True)
plt.xlabel("rank of a term")
plt.ylabel("number of occurrences")
plt.show()

non_appearing = {}
with open(file=args.dict_path, mode="r", encoding="UTF-8") as dict_file:
    dictionary = set([line.split(";")[0] for line in dict_file.readlines()])
    for k, v in frequencies.items():
        if k not in dictionary:
            non_appearing[k] = v

print("30 words with the highest ranks that do not belong to the dictionary")
high_ranks = list(sorted(non_appearing.items(), key=lambda kv: kv[1], reverse=True))[:30]
pprint(high_ranks)
print()

print("30 words with 3 occurrences that do not belong to the dictionary")
three_occurences = [entry for entry in non_appearing.items() if entry[1] == 3][:30]
pprint(three_occurences)
print()

print("Closest corrections")
corrections = {}
for entry in three_occurences:
    distance = {k: lev.distance(k, entry[0]) for k in dictionary}
    corrections[entry[0]] = min(distance.items(), key=lambda x: x[1])
pprint(corrections)
