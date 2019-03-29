import argparse
from pprint import pprint

from utils.utils import initialize_elastic

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
                    "type": "text",
                    "analyzer": "morfologik"
                }
            }
        }
    }
}, reset=args.reset, index_name=INDEX_NAME, doc_type=TYPE)

frequency_list = es.termvectors(index=INDEX_NAME, doc_type=TYPE, term_statistics=True)
pprint(frequency_list)
