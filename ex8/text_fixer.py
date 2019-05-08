import argparse
import os
from pprint import pprint

import regex

parser = argparse.ArgumentParser()
parser.add_argument('--path', type=str, help='Path to text files with bills', required=True)
args = parser.parse_args()

directory_contents = filter(lambda entry: os.path.isfile(args.path + entry), os.listdir(args.path))
for filename in directory_contents:
    line_counter = 0
    lines = []
    with open(args.path + filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        # pprint(lines)
        for line in lines:
            if not regex.compile(r'\b[Aa]rt\.').search(line):
                line_counter += 1
            else:
                break
    with open(args.path + filename, 'w', encoding='utf-8') as file:
        for item in lines[line_counter:]:
            file.write("{}\n".format(item))
    print("{} processed".format(filename))
