import argparse
from collections import Counter
from pprint import pprint

from res import llr  # https://github.com/tdunning/python-llr
from utils.utils import open_directory

noun_tags = ('subst',)  # , 'depr', 'num', 'numcol')
adj_tags = ('adj',)  # , 'adja', 'adjp', 'adjc')

parser = argparse.ArgumentParser()
parser.add_argument('--path', type=str, help='Path to text files with processed (!) bills', required=True)
parser.add_argument('--save_to_file', help='Should the scores of n-grams be saved to file "scores.txt"', required=False,
                    action="store_true")
args = parser.parse_args()

unigrams = {}
bigrams = {}
directory_contents = open_directory(args.path)

for filename in directory_contents:
    with open(args.path + '/' + filename, 'r', encoding='utf-8') as file:
        lines = [line.strip().split()[0] + ":" + line.strip().split()[1].split(":")[0]
                 for line in file.readlines()
                 if len(line.strip()) > 0
                 and line.strip().split()[-1] == 'disamb'
                 and line.strip().split()[1] != 'interp']
        for k, v in Counter(lines).items():
            unigrams[k] = v + unigrams[k] if k in unigrams.keys() else v
        for k, v in Counter([lines[i] + ' ' + lines[i + 1] for i in range(0, len(lines) - 1)]).items():
            bigrams[k] = v + bigrams[k] if k in bigrams.keys() else v
        # unigrams.update(Counter(lines))
        # bigrams.update(Counter([lines[i] + ' ' + lines[i + 1] for i in range(0, len(lines) - 1)]))
    print("{} parsed".format(filename))

# for k,v in sorted(bigrams.items(), key=lambda kv: kv[1], reverse=True)[:30]:
#     print(k, v)

llr_diff = llr.llr_compare(Counter(bigrams), Counter(unigrams))
llr_diff_list = list(sorted(llr_diff.items(), key=lambda kv: kv[1], reverse=True))
llr_filtered = [el for el in llr_diff_list
                if len(el[0].split()) > 1
                and el[0].split()[0].split(":")[1] in noun_tags
                and el[0].split()[1].split(":")[1] in noun_tags + adj_tags]

if args.save_to_file:
    with open("scores.txt", 'w', encoding='utf-8') as file:
        file.write('\n'.join(str(line) for line in llr_filtered))
    with open("top50.txt", 'w', encoding='utf-8') as file:
        file.write('\n'.join(str(line) for line in llr_filtered[:50]))
else:
    print('LLR filtered')
    pprint(llr_filtered)
