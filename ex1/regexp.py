import argparse
import os

import regex

parser = argparse.ArgumentParser()
parser.add_argument('--path', type=str, help='Path to text files with bills')
args = parser.parse_args()

pattern_1 = r'''(?i)ustaw(?:a(?:|mi|ch|)|y|o(?:|m)|ą|ie)\b\s+z\s+dnia\s+(\d{1,2})\s+ # np. ustawa z dnia 23
                (stycznia|lutego|marca|kwietnia|maja|czerwca|
                lipca|sierpnia|września|października|listopada|grudnia)\s+ # np. grudnia
                (\d{4})\s+r\.(?:\s|\W)*(.*|\s*) # np. 1998 r. o nazwie takiej a innej
                (?=\s\()\s+\((?<=\()(?:Dz\.U\.\s+)((?:.|\s*)*)(?=\))\) # np. (Dz.U [...]) '''

pattern_1_inside_parentheses = r'''(?i)(?:(?:z\s+(\d+)\s+r\.\s+)? # np. z 1996 r. 
                                    Nr\s+(\d+)\,\s+ # np. Nr 23,
                                    poz\.\s+(\d+)) # np. poz. 34'''

pattern_2 = r'''(?:art\.\s+(\d+)(?:.)*\s+)? # np. art. 24 (...)
                ust\.\s+(\d+) # np. ust. 123'''

pattern_3 = r'''(?i)(ustaw(?:a(?:|mi|ch|)|y|o(?:|m)|ą|ie))\b'''


def open_directory(path):
    return os.listdir(path) if os.path.isdir(path) else [path]


def read_file(path, filename):
    with open(path + "/" + filename, 'r', encoding="utf-8") as file:
        return file.read()


def ex1(path):
    directory_contents = open_directory(path)
    count_dict = {}
    for filename in directory_contents:
        file_contents = read_file(path, filename)
        for item in regex.findall(pattern_1, file_contents, flags=regex.IGNORECASE | regex.MULTILINE | regex.VERBOSE):
            day, month, year, name, journal_info = item
            prev_year = year
            for journal_data_captured in regex.findall(pattern_1_inside_parentheses, journal_info,
                                                       flags=regex.IGNORECASE | regex.MULTILINE | regex.VERBOSE):
                journal_year, number, position = journal_data_captured
                if journal_year is None or journal_year == '':
                    journal_year = prev_year
                else:
                    prev_year = journal_year
                if (journal_year, position) in count_dict.keys():
                    count_dict[journal_year, position] = count_dict[journal_year, position] + 1
                else:
                    count_dict[journal_year, position] = 1
        print("{} parsed".format(filename))
    count_list = list(count_dict.items())
    count_list.sort(key=lambda item: item[1], reverse=True)
    with open("ex1.txt", 'w+', encoding='utf-8') as file:
        for item in count_list:
            file.write("Journal year:{}\t\tJournal position:{}\t\tCount:{}\n".format(item[0][0], item[0][1], item[1]))


def ex2(path):
    directory_contents = open_directory(path)
    count_list = []
    for filename in directory_contents:
        file_contents = read_file(path, filename)
        counter = len(regex.findall(pattern_2, file_contents, flags=regex.MULTILINE | regex.VERBOSE))
        count_list.append((filename, counter))
        print("{} parsed".format(filename))
    count_list.sort(key=lambda item: item[1], reverse=True)
    with open("ex2.txt", 'w+', encoding='utf-8') as file:
        for item in count_list:
            split_name = regex.split("\_|\.", item[0])
            file.write("Bill year:{}\t\tBill number:{}\t\tCount:{}\n".format(split_name[0], split_name[1], item[1]))


def ex3(path):
    directory_contents = open_directory(path)
    counter = 0
    for filename in directory_contents:
        file_contents = read_file(path, filename)
        counter += len(regex.findall(pattern_3, file_contents, flags=regex.IGNORECASE | regex.MULTILINE | regex.VERBOSE))
    print("'Ustawa' counter: {}".format(counter))


ex1(args.path)
ex2(args.path)
ex3(args.path)
