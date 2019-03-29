import os

from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient

INDEX_NAME = 'legislatives'
TYPE = 'text'


def open_directory(path):
    return os.listdir(path) if os.path.isdir(path) else [os.path.basename(path)]


def read_file(path, filename):
    with open(path + "/" + filename, 'r', encoding="utf-8") as file:
        return file.read()


def initialize_elastic(address, path, settings, reset=True, index_name=INDEX_NAME, doc_type=TYPE):
    es = Elasticsearch([address])
    if reset:
        ic = IndicesClient(es)
        if ic.exists(index=index_name):
            ic.delete(index_name)
        ic.create(index=index_name, body=settings)
        directory_contents = open_directory(path)
        for filename in directory_contents:
            file_contents = read_file(path, filename)
            es.index(index=index_name, doc_type=doc_type, id=filename, body={
                "text": file_contents,
            })
            print(filename + " loaded")
    return es
