import argparse
import os
import shutil
from pprint import pprint

parser = argparse.ArgumentParser()
parser.add_argument('--path', type=str, help='Path to text files with bills', required=True)
args = parser.parse_args()

directory_contents = filter(lambda entry: os.path.isfile(args.path + entry), os.listdir(args.path))
for filename in directory_contents:
    with open(args.path + filename, 'r+', encoding='utf-8') as file:
        first_lines = list(filter(lambda line: len(line.strip()) > 0, file.readlines()))[:10]
        if any('o zmianie' in line for line in first_lines):
            shutil.copy2(args.path + filename, args.path + 'zmiana')
            print('{} copied to "zmiana"'.format(filename))
            # print("JEST")
            # print(first_lines)
        else:
            shutil.copy2(args.path + filename, args.path + 'normal')
            print('{} copied to "normal"'.format(filename))
            # print("NIE MA")
            # print(first_lines)
