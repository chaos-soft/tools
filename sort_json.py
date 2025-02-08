#!/usr/bin/env python3
import argparse
import json
import sys


def main(file: str) -> int:
    with open(file) as f:
        data = json.load(f)
        sort(data)
        print(json.dumps(data, sort_keys=True, indent=4, ensure_ascii=False))
    return 0


def sort(dict_: dict) -> None:
    for k, v in dict_.items():
        if isinstance(v, dict):
            sort(v)
        else:
            v.sort()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str)
    args = parser.parse_args()
    sys.exit(main(args.file))
