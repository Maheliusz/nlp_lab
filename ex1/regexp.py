import argparse
import os

import regex

parser = argparse.ArgumentParser()
parser.add_argument('--path', type=str, help='Path to text files with bills')
args = parser.parse_args()

pattern_1 = r'(?i)ustaw(?:a(?:|mi|ch|)|y|o(?:|m)|ą|ie)\b\s+z\s+dnia\s+(\d{1,2})\s+(' \
            r'stycznia|lutego|marca|kwietnia|maja|czerwca|lipca|sierpnia|września|października|listopada|grudnia)\s+(' \
            r'\d{4})\s+r\.(?:\s|\W)*(.*|\s*)(?=\s\()\s+\((?<=\()(?:Dz\.U\.\s+)((?:.|\s*)*)(?=\))\) '

pattern_1_inside_parentheses = r'(?i)(?:(?:z\s+(\d+)\s+r\.\s+)?Nr\s+(\d+)\,\s+poz\.\s+(\d+))'

pattern_2 = r'(?:art\.\s+(\d+)(?:.)*\s+)?ust\.\s+(\d+)'

pattern_3 = r'(?i)(ustaw(?:a(?:|mi|ch|)|y|o(?:|m)|ą|ie))\b'


def open_directory(path):
    return os.listdir(path)


def read_file(path, filename):
    with open(path + "/" + filename, 'r', encoding="utf-8") as file:
        return file.read()


def call_fun(path, fun, pattern):
    directory_contents = open_directory(path)
    for filename in directory_contents:
        file_contents = read_file(path, filename)
        for item in regex.findall(pattern, file_contents):
            pass


def ex1(path):
    title = ''
    pattern = regex.compile(pattern_1, flags=regex.MULTILINE | regex.IGNORECASE)
    additional_pattern = regex.compile(pattern_1_inside_parentheses, flags=regex.MULTILINE | regex.IGNORECASE)
    directory_contents = open_directory(path)
    count_dict = {}
    for filename in directory_contents:
        file_contents = read_file(path, filename)
        for item in regex.findall(pattern, file_contents):
            day, month, year, name, journal_info = item
            if len(name) > len(title):
                title = name
            prev_year = year
            for journal_data_captured in regex.findall(additional_pattern, journal_info):
                journal_year, number, position = journal_data_captured
                if journal_year is None or journal_year == '':
                    journal_year = prev_year
                else:
                    prev_year = journal_year
                if (journal_year, position) in count_dict:
                    count_dict[journal_year, position] = count_dict[journal_year, position] + 1
                else:
                    count_dict[journal_year, position] = 1
        print("{} parsed".format(filename))
    print(title)
    count_list = list(count_dict.items())
    count_list.sort(key=lambda item: item[1], reverse=True)
    with open("ex1.txt", 'w+', encoding='utf-8') as file:
        for item in count_list:
            file.write("Journal year:{}\tJournal number:{}\tCount:{}\n".format(item[0][0], item[0][1], item[1]))


def ex2(path):
    pattern = regex.compile(pattern_2, flags=regex.MULTILINE | regex.IGNORECASE)
    directory_contents = open_directory(path)
    count_list = []
    for filename in directory_contents:
        file_contents = read_file(path, filename)
        counter = 0
        for _ in regex.findall(pattern, file_contents):
            counter += 1
        count_list.append((filename, counter))
        print("{} parsed".format(filename))
    count_list.sort(key=lambda item: item[1], reverse=True)
    with open("ex2.txt", 'w+', encoding='utf-8') as file:
        for item in count_list:
            split_name = regex.split("\_|\.", item[0])
            file.write("Bill year:{}\tBill number:{}\tCount:{}\n".format(split_name[0], split_name[1], item[1]))


def ex3(path):
    pattern = regex.compile(pattern_3, flags=regex.MULTILINE | regex.IGNORECASE)
    directory_contents = open_directory(path)
    counter = 0
    for filename in directory_contents:
        file_contents = read_file(path, filename)
        for _ in regex.findall(pattern, file_contents):
            counter += 1
    print("Ustawa counter: {}".format(counter))


ex1(args.path)
ex2(args.path)
ex3(args.path)
