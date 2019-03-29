import argparse

from utils.utils import initialize_elastic

parser = argparse.ArgumentParser()
parser.add_argument('--path', type=str, help='Path to text files with bills', required=True)
parser.add_argument('--address', type=str, help='Address to send requests to', required=True)
parser.add_argument('--reset', help='Should the indexes be reset', required=False, action="store_true")
args = parser.parse_args()

INDEX_NAME = 'legislatives'
TYPE = 'text'

es = initialize_elastic(address=args.address, path=args.path, reset=args.reset, settings={
    "settings": {
        "analysis": {
            "filter": {
                "synonyms": {
                    "type": "synonym",
                    "synonyms": [
                        "kpk => kodeks postępowania karnego",
                        "kpc => kodeks postępowania cywilnego",
                        "kk => kodeks karny",
                        "kc => kodeks cywilny",
                    ]
                }
            },
            "analyzer": {
                "custom_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "morfologik_stem",
                        "lowercase",
                        "synonyms",
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
}, index_name=INDEX_NAME, doc_type=TYPE)

print("Number of legislative acts containing the word ustawa (in any form):\t{}".format(
    es.search(index=INDEX_NAME, doc_type=TYPE, body={
        "query": {
            "match": {
                "text": {
                    "query": "ustawa",
                }
            }
        }
    })['hits']['total']))

print("Number of legislative acts containing the words kodeks postępowania cywilnego in the specified order, "
      "but in an any inflection form:\t{}".format(
    es.search(index=INDEX_NAME, doc_type=TYPE, body={
        "query": {
            "match_phrase": {
                "text": {
                    "query": "kodeks postępowania cywilnego",
                }
            }
        }
    })['hits']['total']))

print("Number of legislative acts containing the words wchodzi w życie (in any form) allowing for up to 2 additional "
      "words in the searched phrase:\t{}".format(
    es.search(index=INDEX_NAME, doc_type=TYPE, body={
        "query": {
            "match_phrase": {
                "text": {
                    "query": "wchodzi w życie",
                    "slop": 2
                }
            }
        }
    })['hits']['total']))

konstytucjas = sorted(es.search(index=INDEX_NAME, doc_type=TYPE, body={
    "query": {
        "match": {
            "text": {
                "query": "konstytucja",
            }
        }
    },
    "highlight": {
        "fields": {
            "text": {}
        },
        "number_of_fragments": 3
    }
})['hits']['hits'], key=lambda x: -x["_score"])[:10]
print("Most relevant konstytucjas")
for x in konstytucjas:
    print("{}:\t{}\t{}".format(x['_id'], x["_score"], x['highlight']['text']))
