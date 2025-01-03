#!/usr/bin/env python3
from pathlib import Path
from typing import Any
import argparse
import filecmp
import json
import subprocess
import sys

BASE_DIR = Path(__file__).resolve().parent
BACKUP_PATH: Path = BASE_DIR / 'backup'
CONFIG: dict[str, Any] = {}
VARIABLES: dict[str, list[str]] = {}


def append(file_path: str, list_: list[str]) -> None:
    str_ = '\n'.join(list_)
    str_ = replace_variables(str_)
    print(f'append {file_path}')
    Path(file_path).parent.mkdir(mode=0o755, parents=True, exist_ok=True)
    with open(file_path, 'a') as f:
        f.write(f'{str_}\n')


def append_once(file_path: str, list_: list[str]) -> None:
    if not Path(file_path).exists():
        append(file_path, list_)


def backup() -> None:
    BACKUP_PATH.mkdir(mode=0o755, parents=True, exist_ok=True)
    for file_path in CONFIG.keys():
        if Path(file_path).exists() and not (BACKUP_PATH / get_backup_name(file_path)).exists():
            print(f'backup {file_path}')
            subprocess.run(['cp', '-rp', file_path, BACKUP_PATH / get_backup_name(file_path)], check=True)


def check_backup() -> None:
    for file_path in CONFIG.keys():
        bp = BACKUP_PATH / get_backup_name(file_path)
        if Path(file_path).exists() and bp.exists():
            if not filecmp.cmp(file_path, bp, shallow=True):
                print(f'not equal {file_path}')


def get_backup_name(file_path: str) -> str:
    return file_path.replace('/', '__').lstrip('__')


def insert_after(file_path: str, dict_: dict[str, list[str]]) -> None:
    if Path(file_path).exists():
        print(f'insert_after {file_path}')
        with open(file_path, 'r+') as f:
            data = f.readlines()
            for k, v in dict_.items():
                try:
                    i = data.index(k)
                    data.insert(i + 1, '{}\n'.format('\n'.join(v)))
                except ValueError:
                    pass
            f.seek(0)
            f.writelines(data)


def load_config(file: str) -> None:
    global CONFIG, VARIABLES
    with open(file) as f:
        CONFIG = json.load(f)
        if CONFIG.get('variables'):
            VARIABLES = CONFIG.pop('variables')


def rebuild() -> None:
    reset()
    for file_path, actions in CONFIG.items():
        if 'append' in actions:
            append(file_path, actions['append'])
        if 'append_once' in actions:
            append_once(file_path, actions['append_once'])
        if 'insert_after' in actions:
            insert_after(file_path, actions['insert_after'])
        if 'remove' in actions:
            list_ = [[v, ''] for v in actions['remove']]
            if 'replace' in actions:
                actions['replace'].extend(list_)
            else:
                actions['replace'] = list_
        if 'replace' in actions:
            replace(file_path, actions['replace'])


def replace(file_path: str, list_: list[list[str]]) -> None:
    if Path(file_path).exists():
        print(f'replace {file_path}')
        with open(file_path, 'r+') as f:
            data = f.read()
            for v in list_:
                data = data.replace(v[0], v[1])
            f.seek(0)
            f.write(data)
            f.truncate()


def replace_variables(str_: str) -> str:
    for var, list_ in VARIABLES.items():
        if var in str_:
            str_ = str_.replace(var, '\n'.join(list_))
    return str_


def reset() -> None:
    for file_path, actions in CONFIG.items():
        if 'append_once' in actions:
            continue
        fp = Path(file_path)
        bp = BACKUP_PATH / get_backup_name(file_path)
        if bp.exists():
            print(f'reset {file_path}')
            fp.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
            subprocess.run(['cp', '-rp', bp, fp], check=True)
        elif fp.exists():
            s = input(f'rm {file_path}? [Y/n] ') or 'Y'
            if s == 'Y':
                fp.unlink()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', type=str)
    parser.add_argument('action', choices=['backup', 'check_backup', 'rebuild', 'reset'], type=str)
    args = parser.parse_args()
    load_config(args.config_file)
    eval(f'{args.action}()')
    sys.exit(0)
