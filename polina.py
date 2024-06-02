#!/usr/bin/env python3
from pathlib import Path
import argparse
import json
import subprocess
import sys

BASE_DIR = Path(__file__).resolve().parent
APPEND: dict[str, list[str]] = {}
BACKUP_PATH: Path = BASE_DIR / 'backup'
FILES: set[str] = set()
INSERT: dict[str, dict[str, list[str]]] = {}
IS_REVERSE: bool = False
REPLACE: dict[str, list[list[str]]] = {}
VARIABLES: dict[str, list[str]] = {}


def add2replace(k, list_) -> None:
    if k in REPLACE:
        REPLACE[k].extend(list_)
    else:
        REPLACE[k] = list_


def append() -> None:
    v: list[str]
    for file_path, v in APPEND.items():
        str_ = '\n'.join(v)
        str_ = replace_variables(str_)
        print(f'append {file_path}')
        Path(file_path).parent.mkdir(mode=0o755, parents=True, exist_ok=True)
        with open(file_path, 'a') as f:
            f.write(f'{str_}\n')


def backup() -> None:
    BACKUP_PATH.mkdir(mode=0o755, parents=True, exist_ok=True)
    for file_path in FILES:
        fp = Path(file_path)
        if fp.exists() and not (BACKUP_PATH / get_backup_name(file_path)).exists():
            print(f'backup {file_path}')
            subprocess.run(['cp', '-rp', file_path, BACKUP_PATH / get_backup_name(file_path)], check=True)


def get_backup_name(file_path: str) -> str:
    return file_path.replace('/', '__').lstrip('__')


def insert() -> None:
    v: dict[str, list[str]]
    for file_path, v in INSERT.items():
        if Path(file_path).exists():
            print(f'insert {file_path}')
            with open(file_path, 'r+') as f:
                data = f.readlines()
                for k, vv in v.items():
                    data.insert(int(k) - 1, '{}\n'.format('\n'.join(vv)))
                f.seek(0)
                f.writelines(data)


def load_config() -> None:
    global APPEND, COMMANDS, FILES, INSERT, REPLACE, VARIABLES
    with open(BASE_DIR / 'polina_config.json') as f:
        data = json.load(f)
    if IS_REVERSE:
        if 'variables' in data:
            VARIABLES |= data['variables']
        if 'append' in data:
            for k, v in data['append'].items():
                str_ = '\n'.join(v)
                str_ = replace_variables(str_)
                list_ = [[f'{str_}\n', '']]
                add2replace(k, list_)
            FILES |= set(REPLACE.keys())
        if 'insert' in data:
            for k, v in data['insert'].items():
                list_ = [['{}\n'.format('\n'.join(vv)), ''] for vv in v.values()]
                add2replace(k, list_)
            FILES |= set(REPLACE.keys())
        if 'replace' in data:
            for k, v in data['replace'].items():
                list_ = [[vv[1], vv[0]] for vv in v]
                add2replace(k, list_)
            FILES |= set(REPLACE.keys())
        if 'remove' in data:
            APPEND |= data['remove']
            FILES |= set(APPEND.keys())
        return None
    if 'append' in data:
        APPEND |= data['append']
        FILES |= set(APPEND.keys())
    if 'insert' in data:
        INSERT |= data['insert']
        FILES |= set(INSERT.keys())
    if 'replace' in data:
        REPLACE |= data['replace']
        FILES |= set(REPLACE.keys())
    if 'variables' in data:
        VARIABLES |= data['variables']
    if 'remove' in data:
        for k, v in data['remove'].items():
            list_ = [[vv, ''] for vv in v]
            add2replace(k, list_)
        FILES |= set(REPLACE.keys())


def rebuild() -> None:
    reset()
    append()
    insert()
    replace()


def replace() -> None:
    v: list[list[str]]
    for file_path, v in REPLACE.items():
        if Path(file_path).exists():
            print(f'replace {file_path}')
            with open(file_path, 'r+') as f:
                data = f.read()
                for vv in v:
                    data = data.replace(vv[0], vv[1])
                f.seek(0)
                f.write(data)
                f.truncate()


def replace_variables(str_: str) -> str:
    for var, v in VARIABLES.items():
        if var in str_:
            str_ = str_.replace(var, '\n'.join(v))
    return str_


def reset() -> None:
    for file_path in FILES:
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
    load_config()
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['backup', 'rebuild', 'reset'], type=str)
    args = parser.parse_args()
    eval(f'{args.action}()')
    sys.exit(0)
