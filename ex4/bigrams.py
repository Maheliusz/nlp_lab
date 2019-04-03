import argparse

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
                    "max_shingle_size": 2,
                    "output_unigrams": False
                }
            },
            "analyzer": {
                "custom_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "morfologik_stem",
                        "lowercase",
                        "my_shingle_filter"
                    ]
                }
            }
        }
    },
    "mappings": {
        "text": {
            "properties": {
                "text": {
                    "type": "text",
                    "analyzer": "custom_analyzer"
                }
            }
        }
    }
}, reset=args.reset, index_name=INDEX_NAME, doc_type=TYPE, index_counter=True)

directory_contents = open_directory(args.path)
