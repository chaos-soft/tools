#!/usr/bin/env python3
from pathlib import Path
import argparse
import json
import subprocess
import sys

BASE_DIR = Path(__file__).resolve().parent
APPEND: dict[str, list[str]] = {}
BACKUP_PATH = BASE_DIR / 'backup'
FILES: set[str] = set()
INSERT: dict[str, dict[str, list[str]]] = {}
REPLACE: dict[str, list[list[str]]] = {}


def append() -> None:
    v: list[str]
    for file_path, v in APPEND.items():
        print(f'append {file_path}')
        Path(file_path).parent.mkdir(mode=0o755, parents=True, exist_ok=True)
        with open(file_path, 'a') as f:
            f.write('\n'.join(v))
            f.write('\n')


def backup() -> None:
    BACKUP_PATH.mkdir(mode=0o755, parents=True, exist_ok=True)
    for file_path in FILES:
        fp = Path(file_path)
        if fp.exists() and not (BACKUP_PATH / fp.name).exists():
            print(f'backup {file_path}')
            subprocess.run(['cp', '-rp', file_path, BACKUP_PATH], check=True)


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
    global APPEND, COMMANDS, FILES, INSERT, REPLACE
    with open(BASE_DIR / 'polina_config.json') as f:
        data = json.load(f)
    if 'append' in data:
        APPEND |= data['append']
        FILES |= set(APPEND.keys())
    if 'insert' in data:
        INSERT |= data['insert']
        FILES |= set(INSERT.keys())
    if 'replace' in data:
        REPLACE |= data['replace']
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


def reset() -> None:
    for file_path in FILES:
        fp = Path(file_path)
        bp = BACKUP_PATH / fp.name
        if bp.exists():
            print(f'reset {file_path}')
            fp.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
            subprocess.run(['cp', '-rp', bp, fp.parent], check=True)
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
