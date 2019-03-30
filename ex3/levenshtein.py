import argparse
from pprint import pprint

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
        if key.isalpha() and len(key) >= 2:
            frequencies[key] = value['term_freq'] if key not in frequencies else frequencies[key] + value['term_freq']
pprint(frequencies)
