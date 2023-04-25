#!/usr/bin/env python3
import json
import os
import subprocess
import sys

BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
CONFIG: dict[str, list[str]] = {}


def load_config() -> None:
    global CONFIG
    with open(os.path.join(BASE_DIR, 'jill_config.json')) as f:
        CONFIG = json.load(f)


def main() -> int:
    if CONFIG['install']:
        command = CONFIG['install_command'] + CONFIG['install']
        print(' '.join(command))
        subprocess.run(command)
    if CONFIG['remove']:
        command = CONFIG['remove_command'] + CONFIG['remove']
        print(' '.join(command))
        subprocess.run(command)
    return 0


if __name__ == '__main__':
    load_config()
    sys.exit(main())
