import pathlib
import shutil
import hashlib
import sys
import json
import time
from typing import Union
from art import tprint
from my_stack import MyStack


# import click
# from tqdm import tqdm
# from time import sleep

class CopyFiles:
    def __init__(self, source, destination):
        self.source = pathlib.Path(source).absolute()
        self.destination = pathlib.Path(destination).absolute()
        self.data_json_file = self.destination.joinpath('db.json')
        self.data_json = {}

    @classmethod
    def hash_file(cls, filename):
        """Возвращает хэш сумму файла"""
        h = hashlib.sha256()
        with open(filename, 'rb') as file:
            chunk = 0
            while chunk != b'':
                chunk = file.read(1024)
                h.update(chunk)
        return h.hexdigest()

    def update_data_file(self, directory: Union[str, pathlib.Path] = None):
        if directory is None:
            directory = self.destination
        else:
            directory = pathlib.Path(directory)
        if directory.exists():
            stack = MyStack()
            self.data_json = {}
            stack.push(directory)
            while not stack.empty():
                d = stack.pop()
                for x in d.iterdir():
                    if x.is_dir():
                        stack.push(x)
                    else:
                        self.data_json[str(x)] = {}
                        self.data_json[str(x)]['sha256'] = self.hash_file(x)
                        file_stats = x.stat()
                        self.data_json[str(x)]["size, Kb"] = file_stats.st_size / 1024
                        self.data_json[str(x)]["size, Mb"] = file_stats.st_size / (1024 * 1024)
                        self.data_json[str(x)]["Created"] = time.ctime(file_stats.st_ctime)
                        self.data_json[str(x)]["Last modified"] = time.ctime(file_stats.st_mtime)
                        self.data_json[str(x)]["Last accessed"] = time.ctime(file_stats.st_atime)
            self.data_json_file = directory.joinpath('db.json')
            self.dump_json()

    def copy_files(self, source=None, destination=None, json_use=True):
        if destination is None:
            destination = self.destination
        if source is None:
            source = self.source
        src = pathlib.Path(source).resolve()
        dest = pathlib.Path(destination).resolve()
        if not src.exists():
            print(f"Расположение {src} не найдено, пожалуйста проверьте путь")
            return
        if not dest.exists():
            print(f"Расположение {dest} не найдено")
            while True:
                answer = input("Создать новую директорию? Д/Н ").upper()
                if answer == 'Д' or answer == 'Y':
                    dest.mkdir(parents=True)
                    print(f"Директория {dest} создана!")
                    break
                elif answer == 'Н' or answer == 'N':
                    return
                else:
                    print('Hеверный ответ!')
        stack = MyStack()
        stack.push(src)
        black_list = ["db.json"]
        if json_use:
            json_src_file = src.joinpath('db.json')
            if not json_src_file.exists():
                self.update_data_file(src)
            json_src_data = self.load_json(json_src_file)
            json_dest_file = dest.joinpath('db.json')
            if json_dest_file.exists():
                json_dest_data = self.load_json(json_dest_file)
            else:
                json_dest_data = {}
            while not stack.empty():
                d = stack.pop()
                for x in d.iterdir():
                    if x.name in black_list:
                        continue
                    child_path = x.relative_to(src)
                    y = dest.joinpath(child_path)
                    if x.is_dir():
                        stack.push(x.resolve())
                        if not y.exists():
                            y.mkdir()
                            print(f"Создана папка {y}")
                    else:
                        hash_x = json_src_data[str(x)].get('sha256')
                        hash_y = None
                        if str(y) in json_dest_data:
                            if json_dest_data[str(y)].get('sha256') is not None:
                                hash_y = json_dest_data[str(y)].get('sha256')
                                if hash_x == hash_y:
                                    print(f"Файлы {str(x)} и {str(y)} совпадают.")
                                else:
                                    shutil.copyfile(x, y)
                                    hash_y = hash_x
                                    print(f"Файл {str(y)} обновлён")
                            elif y.exists():
                                hash_y = self.hash_file(y)
                                if hash_x == hash_y:
                                    print(f"Файлы {str(x)} и {str(y)} совпадают.")
                                else:
                                    shutil.copyfile(x, y)
                                    hash_y = hash_x
                                    print(f"Файл {str(y)} обновлён")
                            else:
                                shutil.copyfile(x, y)
                                hash_y = hash_x
                                print(f"Файл {str(x)} скопирован в {str(y.parent)}.")
                        else:
                            json_dest_data[str(y)] = {}
                            if y.exists():
                                hash_y = self.hash_file(y)
                                if hash_x == hash_y:
                                    print(f"Файлы {str(x)} и {str(y)} совпадают.")
                                else:
                                    shutil.copyfile(x, y)
                                    hash_y = hash_x
                                    print(f"Файл {str(y)} обновлён")
                            else:
                                shutil.copyfile(x, y)
                                hash_y = hash_x
                                print(f"Файл {str(x)} скопирован в {str(y.parent)}.")
                        json_dest_data[str(y)]['sha256'] = hash_y
                        file_stats = y.stat()
                        json_dest_data[str(y)]["size, Kb"] = file_stats.st_size / 1024
                        json_dest_data[str(y)]["size, Mb"] = file_stats.st_size / (1024 * 1024)
                        json_dest_data[str(y)]["Created"] = time.ctime(file_stats.st_ctime)
                        json_dest_data[str(y)]["Last modified"] = time.ctime(file_stats.st_mtime)
                        json_dest_data[str(y)]["Last accessed"] = time.ctime(file_stats.st_atime)
                        self.data_json = json_dest_data
                        self.data_json_file = json_dest_file
                        self.dump_json()

        else:
            while not stack.empty():
                d = stack.pop()
                for x in d.iterdir():
                    if x.name in black_list:
                        continue
                    child_path = x.relative_to(src)
                    y = dest.joinpath(child_path)
                    if x.is_dir():
                        stack.push(x.resolve())
                        if not y.exists():
                            y.mkdir()
                            print(f"Создана папка {y}")
                    elif y.exists():
                        if self.hash_file(x) == self.hash_file(y):
                            print(f"Файлы {x} и {y} совпадают.")
                        else:
                            shutil.copyfile(x, y)
                            print(f"Файл {y} обновлён.")
                    else:
                        shutil.copyfile(x, y)
                        print(f"Файл {x} скопирован в {y.parent}")

    def dump_json(self):
        with open(self.data_json_file, "w", encoding="utf-8") as fp:
            json.dump(self.data_json, fp, indent=4, sort_keys=True)

    def load_json(self, file):
        with open(file, "r", encoding="utf-8") as fp:
            self.data_json = json.load(fp)
            return self.data_json


def main():
    tprint("Copy files", font="bulbhead")
    if len(sys.argv) == 3:
        source = sys.argv[1]
        destination = sys.argv[2]
    else:
        source = input("Папка источник: ")
        destination = input("Папка назначения: ")
    cp = CopyFiles(source, destination)
    # cp.update_data_file(str(source))
    # cp.update_data_file(str(destination))
    cp.copy_files()


if __name__ == "__main__":
    main()
