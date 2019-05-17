import argparse
import os
import random
import sys
import time

import requests

parser = argparse.ArgumentParser()
parser.add_argument('--path', type=str, help='Path to text files with bills', required=True)
parser.add_argument('--count', type=int, help='How much files process', required=False, default=20)

args = parser.parse_args()

url = 'http://ws.clarin-pl.eu/nlprest2'

parsed = {}
id2file = {}

already_parsed = os.listdir(args.path + 'ner/')
count = min(args.count, 100 - len(already_parsed))
directory_contents = random.sample(list(filter(lambda entry: os.path.isfile(args.path + entry)
                                                             and entry not in already_parsed,
                                               os.listdir(args.path))),
                                   k=count)
for filename in directory_contents:
    with open(args.path + filename, encoding='utf-8') as file:
        response = requests.post(url=url + '/base/startTask',
                                 json={'text': file.read(), 'lpmn': 'any2txt|wcrft2|liner2({"model":"n82"})',
                                       'user': ''})
        response_string = str(response.content).replace("b\'", "").replace("\'", "")
        id2file[response_string] = filename
        parsed[response_string] = {"value": None, "status": None}
    print("{} read and sent".format(filename))

id_list = list(parsed.keys())
print("Finished reading files")

counter = 0
while len(id_list) > 0:
    for id in id_list:
        parsed[id] = requests.get(url=url + '/base/getStatus/' + str(id)).json()
        if parsed[id]['status'] == 'DONE':
            counter += 1
            with open(args.path + 'ner/' + id2file[id], 'wb') as file:
                for element in parsed[id]['value']:
                    # print(requests.get(url=url + '/base/download' + element['fileID']).content)
                    # file.write(str(requests.get(url=url + '/base/download' + element['fileID']).content)[2:-1])
                    file.write(requests.get(url=url + '/base/download' + element['fileID']).content)
            id_list.remove(id)
            print("{} finished".format(counter))
        elif parsed[id]['status'] == 'ERROR':
            print(parsed[id]['value'], file=sys.stderr)
            exit(-1)
    time.sleep(2)
    print('{} docs left'.format(len(id_list)))
