import os


def open_directory(path):
    return os.listdir(path) if os.path.isdir(path) else [os.path.basename(path)]


def read_file(path, filename):
    with open(path + "/" + filename, 'r', encoding="utf-8") as file:
        return file.read()
