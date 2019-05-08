import argparse
import os
import random
import shutil


def split(a, n):
    k, m = divmod(len(a), n)
    return [a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]


parser = argparse.ArgumentParser()
parser.add_argument('--path', type=str, help='Path to text files with bills', required=True)
args = parser.parse_args()

directory_contents = list(filter(lambda entry: os.path.isfile(args.path + entry), os.listdir(args.path)))
cut = split(directory_contents, 5)
random.shuffle(cut)
validation = cut.pop(0)
testing = cut.pop(0)
training = []
for sublist in cut:
    training.extend(sublist)
for filename in validation:
    shutil.copy2(args.path + filename, args.path + 'validation')
    print('{} copied to "validation"'.format(filename))
for filename in testing:
    shutil.copy2(args.path + filename, args.path + 'testing')
    print('{} copied to "testing"'.format(filename))
for filename in training:
    shutil.copy2(args.path + filename, args.path + 'training')
    print('{} copied to "training"'.format(filename))
