import argparse
from collections import Counter
from pprint import pprint

from res import llr  # https://github.com/tdunning/python-llr
from utils.utils import open_directory

parser = argparse.ArgumentParser()
parser.add_argument('--path', type=str, help='Path to text files with processed (!) bills', required=True)
parser.add_argument('--save_to_file', help='Should the scores of n-grams be saved to file "scores.txt"', required=False,
                    action="store_true")
args = parser.parse_args()

unigrams = {}
bigrams = {}
directory_contents = open_directory(args.path)
for filename in directory_contents:
    previous_unigram = ''
    with open(args.path + '/' + filename, 'r', encoding='utf-8') as file:
        lines = [line.strip().split()[0] + ":" + line.strip().split()[1].split(":")[0]
                 for line in file.readlines()
                 if len(line.strip()) > 0
                 and line.strip().split()[-1] == 'disamb'
                 and line.strip().split()[1] != 'interp']
        unigrams.update(Counter(lines))
        for i in range(0, len(lines) - 1):
            key = lines[i] + ' ' + lines[i + 1]
            if key not in bigrams.keys():
                bigrams[key] = 1
            else:
                bigrams[key] += 1
    print("{} parsed".format(filename))

llr_diff = llr.llr_compare(Counter(bigrams), Counter(unigrams))
llr_diff_list = list(sorted(llr_diff.items(), key=lambda kv: kv[1], reverse=True))
print('Log likelihood ratio')
pprint(llr_diff_list[:30])

if args.save_to_file:
    with open("scores.txt", 'w', encoding='utf-8') as file:
        file.write('\n'.join(str(line) for line in llr_diff_list))
