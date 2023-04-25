#!/usr/bin/env python3
import argparse
import json
import os
import shutil
import subprocess
import sys

APPEND: dict[str, list[str]] = {}
BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
COMMANDS: dict[str, list[list[str]]] = {}
FILES: set[str] = set()
REPLACE: dict[str, list[list[str]]] = {}


def backup() -> None:
    backup_path = os.path.join(BASE_DIR, 'backup')
    os.makedirs(backup_path, exist_ok=True)
    for file_path in FILES:
        print(f'backup {file_path}')
        if os.path.isfile(file_path):
            shutil.copy2(file_path, backup_path)


def get_choices() -> list[str]:
    r = ['backup', 'rebuild', 'reset']
    r.extend(COMMANDS.keys())
    return r


def load_config() -> None:
    global APPEND, COMMANDS, FILES, REPLACE
    with open(os.path.join(BASE_DIR, 'polina_config.json')) as f:
        data = json.load(f)
    APPEND |= data['append']
    COMMANDS |= data['commands']
    REPLACE |= data['replace']
    FILES |= set(APPEND.keys()) | set(REPLACE.keys())


def rebuild() -> None:
    reset()
    v: list[str] | list[list[str]]
    for file_path, v in APPEND.items():
        print(f'append {file_path}')
        path, _ = os.path.split(file_path)
        os.makedirs(path, exist_ok=True)
        with open(file_path, 'a') as f:
            f.write('\n'.join(v))
            f.write('\n')
    for file_path, v in REPLACE.items():
        print(f'replace {file_path}')
        with open(file_path, 'r+') as f:
            data = f.read()
            for vv in v:
                data = data.replace(vv[0], vv[1])
            f.seek(0)
            f.write(data)
            f.truncate()


def reset() -> None:
    for file_path in FILES:
        path, file = os.path.split(file_path)
        backup_path = os.path.join(BASE_DIR, 'backup', file)
        if os.path.isfile(backup_path):
            print(f'reset {file_path}')
            shutil.copy2(backup_path, path)
        elif os.path.isfile(file_path):
            s = input(f'rm {file_path}? [Y/n] ') or 'Y'
            if s == 'Y':
                os.remove(file_path)


def run_command(action: str) -> None:
    for command in COMMANDS[action]:
        print(' '.join(command))
        subprocess.run(command, check=True)


if __name__ == '__main__':
    load_config()
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=get_choices(), type=str)
    args = parser.parse_args()
    if args.action in globals():
        eval(f'{args.action}()')
    else:
        run_command(args.action)
    sys.exit(0)
