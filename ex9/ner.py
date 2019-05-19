import argparse
import os
import xml.etree.ElementTree as ET
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
    print('{} unique fine tags found'.format(len(fine)))
fig, axs = plt.subplots(2, 1)
axs[0].hist(list(fine.values()), label=list(fine.keys()))
axs[1].hist(list(coarse.values()), label=list(coarse.keys()))
for tag in fine.keys():
    print('{}\t\t{}'.format(tag, len(fine[tag])))
for tag in coarse.keys():
    print('{}\t\t{}'.format(tag, len(coarse[tag])))
# fig.savefig('res.png')
plt.show()
