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
parser.add_argument('--save_to_file', help='Should the scores of n-grams be saved to file "scores.txt"', required=False,
                    action="store_true")
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


result_file = open('result.txt', 'w', encoding='utf-8')

unigrams_sum = sum(unigrams.values())
bigrams_sum = sum(bigrams.values())
pointwise_mutual_information = {
    k: pmi(unigrams[k.split()[0]] / unigrams_sum, unigrams[k.split()[1]] / unigrams_sum, v / bigrams_sum)
    for k, v in bigrams.items()}
pmi_list = list(sorted(pointwise_mutual_information.items(), key=lambda kv: kv[1], reverse=True))
print('Pointwise mutual information')
result_file.write('Pointwise mutual information\n')
pprint(pmi_list[:30])
pprint(str(pmi_list[:30]), stream=result_file)
result_file.write('\n')

if args.save_to_file:
    with open("scores.txt", 'w', encoding='utf-8') as file:
        file.write('\n'.join(str(line) for line in pmi_list))
        file.write('\n')
        for _ in range(0, 10):
            file.write(''.join('-' for _ in range(0, 30)))
            file.write('\n')

llr_diff = llr.llr_compare(Counter(bigrams), Counter(unigrams))
llr_diff_list = list(sorted(llr_diff.items(), key=lambda kv: kv[1], reverse=True))
print('Log likelihood ratio')
pprint(llr_diff_list[:30])
result_file.write('Log likelihood ratio\n')
pprint(llr_diff_list[:30])
pprint(str(llr_diff_list[:30]), stream=result_file)
result_file.write('\n')

if args.save_to_file:
    with open("scores.txt", 'a', encoding='utf-8') as file:
        file.write('\n'.join(str(line) for line in llr_diff_list))

print('Which measure works better for the problem?')
print('\tLLR > PMI')
result_file.write('Which measure works better for the problem?\n')
result_file.write('\tLLR > PMI\n')

print('What would be needed, besides good measure, to build a dictionary of multiword expressions?')
print('\tLarge amount (or simply enough) of data')
result_file.write('What would be needed, besides good measure, to build a dictionary of multiword expressions?\n')
result_file.write('\tLarge amount (or simply enough) of data\n')

print('Can you identify a certain threshold which clearly divides the good expressions from the bad?')
print('\tNot really, it all depends on data provided')
result_file.write('Can you identify a certain threshold which clearly divides the good expressions from the bad?\n')
result_file.write('\tNot really, it all depends on data provided\n')
