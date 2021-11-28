import os
import json
import datetime, time


def load_packages(files, bot):

    for file in files:
        if file.endswith(".py"):
            file = file.replace("/", ".")
            bot.load_extension(file[2:-3])


def unload_packages(files, bot):

    for file in files:
        if file.endswith(".py"):
            file = file.replace("/", ".")
            bot.unload_extension(file[2:-3])


def init_files(path_root, files):

    current_files = os.listdir(path_root)

    for file_path_name in current_files:

        if os.path.isdir(f"{path_root}/{file_path_name}") and file_path_name not in ["__pycache__", "package"]:
            init_files(f"{path_root}/{file_path_name}", files)
        elif file_path_name.endswith('.py'):
            files.append(f"{path_root}/{file_path_name}")


def get_json_file(path):

    with open(path) as file:
        json_f = json.load(file)
        file.close()

    return json_f


def get_time():
    return round(time.time())