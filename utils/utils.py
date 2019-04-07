import os
import regex as re

from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient

INDEX_NAME = 'legislatives'
TYPE = 'text'


def open_directory(path):
    return os.listdir(path) if os.path.isdir(path) else [os.path.basename(path)]


def read_file(path, filename):
    with open(path + "/" + filename, 'r', encoding="utf-8") as file:
        return file.read()


def initialize_elastic(address, path, settings, index_name=INDEX_NAME, doc_type=TYPE, **kwargs):
    es = Elasticsearch([address])
    if kwargs['reset']:
        ic = IndicesClient(es)
        if ic.exists(index=index_name):
            ic.delete(index_name)
        ic.create(index=index_name, body=settings)
        directory_contents = open_directory(path)
        counter = 0
        for filename in directory_contents:
            file_contents = re.sub(r'(?:[^\w\s])+', ' ', read_file(path, filename).lower().strip()) if kwargs[
                'remove_non_alphanumeric'] else read_file(path, filename)
            index = counter if kwargs['index_counter'] else filename
            es.index(index=index_name, doc_type=doc_type, id=index, body={
                "text": file_contents,
            })
            print(filename + " loaded")
            counter += 1
    return es
