import itertools

import matplotlib.pyplot as plt
import networkx as nx
import requests

api_address = "http://api.slowosiec.clarin-pl.eu:80/plwordnet-api/"

# 3
in_word = "szkoda"
print(in_word)
response = requests.get(url=api_address + "senses/search", params={"lemma": in_word, "partOfSpeech": "noun"})
for sense in response.json()["content"]:
    print('\t' + sense['domain']['description'])
    synset_id = requests.get(url=api_address + 'senses/{}/synset'.format(sense['id']))
    synset = requests.get(url=api_address + 'synsets/{}/senses'.format(synset_id.json()['id']))
    for synonym in synset.json():
        print('\t\t' + synonym['lemma']['word'])

# 4
in_word = "wypadek drogowy"
G = nx.DiGraph()
response = requests.get(url=api_address + "senses/search", params={"lemma": in_word})
for sense in filter(lambda data: data['senseNumber'] == 1, response.json()["content"]):
    synset_id = requests.get(url=api_address + 'senses/{}/synset'.format(sense['id']))
    relations = requests.get(url=api_address + 'synsets/{}/relations'.format(synset_id.json()['id']))
    for hyp in filter(lambda data: data['relation']['name'] == 'hiperonimia', relations.json()):
        _from = list(map(lambda item: item['lemma']['word'],
                         requests.get(url=api_address + 'synsets/{}/senses'.format(hyp['synsetFrom']['id'])).json()))
        _to = list(map(lambda item: item['lemma']['word'],
                       requests.get(url=api_address + 'synsets/{}/senses'.format(hyp['synsetTo']['id'])).json()))
        G.add_nodes_from(_from)
        G.add_nodes_from(_to)
        G.add_edges_from(itertools.product(_from, _to))
    nx.draw(G, with_labels=True)
    plt.show()

# 5
in_word = "wypadek"
print(in_word)
response = requests.get(url=api_address + "senses/search", params={"lemma": in_word})
for sense in filter(lambda data: data['senseNumber'] == 1, response.json()["content"]):
    synset_id = requests.get(url=api_address + 'senses/{}/synset'.format(sense['id']))
    relations = requests.get(url=api_address + 'synsets/{}/relations'.format(synset_id.json()['id']))
    for hip in filter(lambda data: data['relation']['name'] == 'hiponimia', relations.json()):
        _to = set(map(lambda item: (item['id'], item['lemma']['word'].strip()),
                      requests.get(url=api_address + 'synsets/{}/senses'.format(hip['synsetTo']['id'])).json()))
        for item in _to:
            if item[1] != in_word:
                print("\t" + item[1])

# 6
