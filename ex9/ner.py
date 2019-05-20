import argparse
import os
import xml.etree.ElementTree as ET
from collections import Counter

import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument('--path', type=str, help='Path to text files with bills', required=True)

args = parser.parse_args()

fine = {}
coarse = {}

already_parsed = os.listdir(args.path)
for filename in already_parsed:
    tree = ET.parse(args.path + filename)
    root = tree.getroot()
    for sentence in root.findall('chunk/sentence'):
        words = {}
        for tok in sentence.findall('tok'):
            for ann in tok.findall('ann'):
                chan = ann.attrib['chan']
                num = ann.text
                word = tok.find('lex').find('base').text
                if chan not in words:
                    words[chan] = {}
                if num not in words[chan]:
                    words[chan][num] = word
                else:
                    words[chan][num] = ' '.join([words[chan][num], word])
        for tag in words.keys():
            subdict = words[tag]
            general_tag = '_'.join(tag.split('_')[:2])
            if tag not in fine.keys():
                fine[tag] = list(subdict.values())
            else:
                fine[tag].extend(list(subdict.values()))
            if general_tag not in coarse.keys():
                coarse[general_tag] = list(subdict.values())
            else:
                coarse[general_tag].extend(list(subdict.values()))

    print('{} processed'.format(filename))
fig, axs = plt.subplots(2, 1, figsize=(10, 30))
axs[0].bar(list(fine.keys()), list(map(lambda x: len(x), fine.values())))
axs[1].bar(list(coarse.keys()), list(map(lambda x: len(x), coarse.values())))
for tag in fine.keys():
    print('{}\t\t{}'.format(tag, len(fine[tag])))
for tag in coarse.keys():
    print('{}\t\t{}'.format(tag, len(coarse[tag])))
axs[0].tick_params(labelrotation=90)
fig.savefig('histograms.png')
fine_counter = []
coarse_counter = []
for tag in fine.keys():
    fine_counter.extend([(y, x, tag) for (x, y) in Counter(fine[tag]).items()])
fine_counter = sorted(fine_counter, key=lambda elem: elem[0], reverse=True)
for tag in coarse.keys():
    coarse_counter.extend([(y, x, tag) for (x, y) in Counter(coarse[tag]).items()])
coarse_counter = sorted(coarse_counter, key=lambda elem: elem[0], reverse=True)
with open('top50.txt', 'w', encoding='utf-8') as file:
    file.write('\n'.join(map(lambda x: str(x), fine_counter[:50])))
with open('top10.txt', 'w', encoding='utf-8') as file:
    file.write('\n'.join(map(lambda x: str(x), coarse_counter[:10])))
