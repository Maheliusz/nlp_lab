import itertools

import matplotlib.pyplot as plt
import networkx as nx
import requests

api_address = "http://api.slowosiec.clarin-pl.eu:80/plwordnet-api/"
# """
# 3
result_file = open('result.txt', 'w', encoding='utf-8')
in_word = "szkoda"
print(in_word)
result_file.write(in_word + '\n')
response = requests.get(url=api_address + "senses/search", params={"lemma": in_word, "partOfSpeech": "noun"})
for sense in response.json()["content"]:
    print('\t' + sense['domain']['description'])
    result_file.write('\t' + sense['domain']['description'] + '\n')
    synset_id = requests.get(url=api_address + 'senses/{}/synset'.format(sense['id']))
    synset = requests.get(url=api_address + 'synsets/{}/senses'.format(synset_id.json()['id']))
    for synonym in synset.json():
        print('\t\t' + synonym['lemma']['word'])
        result_file.write('\t\t' + synonym['lemma']['word'] + '\n')

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
plt.savefig('4.png')

# 5, 6
in_word = "wypadek"
print(in_word)
result_file.write(in_word + '\n')
response = requests.get(url=api_address + "senses/search", params={"lemma": in_word})
for sense in filter(lambda data: data['senseNumber'] == 1, response.json()["content"]):
    synset_id = requests.get(url=api_address + 'senses/{}/synset'.format(sense['id']))
    relations = requests.get(url=api_address + 'synsets/{}/relations'.format(synset_id.json()['id']))
    for hip in filter(lambda data: data['relation']['name'] == 'hiponimia', relations.json()):
        _to = set(list(map(lambda item: (item['id'], item['lemma']['word'].strip()),
                           requests.get(url=api_address + 'synsets/{}/senses'.format(hip['synsetTo']['id'])).json())))
        for item in _to:
            print("\t" + item[1])
            result_file.write("\t" + item[1] + '\n')
            subsynset_id = requests.get(url=api_address + 'senses/{}/synset'.format(item[0]))
            subrelations = requests.get(url=api_address + 'synsets/{}/relations'.format(subsynset_id.json()['id']))
            for subhip in filter(lambda data: data['relation']['name'] == 'hiponimia', subrelations.json()):
                subto = set(list(map(lambda x: x['lemma']['word'].strip(),
                                     requests.get(
                                         url=api_address + 'synsets/{}/senses'.format(
                                             subhip['synsetTo']['id'])).json())))
                for subitem in subto:
                    print("\t\t" + subitem)
                    result_file.write("\t\t" + subitem + '\n')


# """
# 7
def group(intake, meaning_nr):
    result = {}
    for word in intake:
        response = requests.get(url=api_address + "senses/search", params={"lemma": word}).json()
        for sense in filter(lambda data: data['senseNumber'] == meaning_nr, response["content"]):
            result.update({requests.get(url=api_address + 'senses/{}/synset'.format(sense['id'])).json()['id']: word})
    return result


def create_graph(in_group, G: nx.Graph):
    relations = []
    for synset_id in in_group.keys():
        relations.extend(requests.get(url=api_address + 'synsets/{}/relations'.format(synset_id)).json())
    edge_labels = {}
    for relation in relations:
        if relation['synsetFrom']['id'] in in_group.keys() and relation['synsetTo']['id'] in in_group.keys():
            G.add_edge(in_group[relation['synsetFrom']['id']], in_group[relation['synsetTo']['id']])
            edge_labels[in_group[relation['synsetFrom']['id']], in_group[relation['synsetTo']['id']]] = \
                relation['relation']['shortDisplayText']
    return edge_labels


group_1_1 = ('strata', 'uszczerbek', 'szkoda majątkowa', 'uszczerbek na zdrowiu', 'krzywda', ' niesprawiedliwość')
group_1_2 = ('szkoda', 'nieszczęście')
group_2_1 = ('wypadek', 'wypadek komunikacyjny', 'kolizja drogowa', 'katastrofa budowlana', 'wypadek drogowy')
group_2_2 = ('kolizja', 'zderzenie', 'bezkolizyjny')


def ex7(ingroup_1, ingroup_2):
    G = nx.DiGraph()
    G.add_nodes_from(ingroup_1 + ingroup_2)
    print(ingroup_1 + ingroup_2)
    result_file.write(str(ingroup_1 + ingroup_2) + '\n')
    grouped = group(ingroup_1, 1)
    grouped.update(group(ingroup_2, 2))
    edge_labels = create_graph(grouped, G)
    pos = nx.circular_layout(G)
    nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=edge_labels, arrowstyle='->')
    nx.draw_networkx(G, pos=pos, with_labels=True)


ex7(group_1_1, group_1_2)
plt.savefig('7_1.png')
plt.close()
ex7(group_2_1, group_2_2)
plt.savefig('7_2.png')


# 8
# print(wn.synsets('szkoda', lang='pol'))
def get_sense(in_word, sense_nr):
    filtered = list(filter(lambda data: data['senseNumber'] == sense_nr,
                           requests.get(url=api_address + "senses/search",
                                        params={"lemma": in_word}).json()["content"]))
    return requests.get(url=api_address + 'senses/{}/synset'.format(filtered[0]['id'])).json()['id'] \
        if len(filtered) > 0 else None


szkoda = get_sense('szkoda', 2)
wypadek = get_sense('wypadek', 1)
kolizja = get_sense('kolizja', 2)
szkoda_m = get_sense('szkoda majątkowa', 1)
nieszczescie = get_sense('nieszczęście', 2)
katastrofa = get_sense('katastrofa budowlana', 1)
