#!/usr/bin/env python3
from typing import Iterator
import argparse
import sys

GARBAGE: str = ' ,{'
INDENTATION: str = '  '
ORDER: list[str] = ['roots', 'multiple', 'elements', 'ids', 'classes', 'at_rules']
SEPARATOR: str = ',\n'


def build_block(block: list) -> str:
    if '{' in block[0]:
        blocks = {}
        keys = []
        for k, v in get_blocks(block):
            keys.append(k)
            # TODO: INDENTATION, несмотря на рекурсию, всегда будет одинаковый.
            blocks[k] = f'{INDENTATION}{k} {{\n{build_block(v)}\n{INDENTATION}}}'
        keys.sort()
        return '\n\n'.join([blocks[k] for k in keys])
    else:
        block.sort()
        return '\n'.join(block)


def get_blocks(data: list) -> Iterator[tuple[str, list]]:
    block: list[str] = []
    key: list[str] = []
    level: int = 1
    for v in data:
        if level == 1:
            if ',' in v:
                key += list(map(lambda vv: vv.strip(GARBAGE), v.split(',')))
            else:
                key.append(v.strip(GARBAGE))
        else:
            if '}' in v and '{' not in block[0]:
                pass
            else:
                block.append(f'{INDENTATION}{v}')
        if '{' in v:
            level += 1
        elif '}' in v:
            level -= 1
            if level == 1:
                key = list(filter(None, key))
                key.sort()
                yield SEPARATOR.join(key), block
                block = []
                key = []


def main(file: str) -> int:
    at_rules: dict[str, list] = {}
    blocks: dict[str, list] = {}
    classes: dict[str, list] = {}
    elements: dict[str, list] = {}
    ids: dict[str, list] = {}
    multiple: dict[str, list] = {}
    roots: dict[str, list] = {}
    with open(file) as f:
        data = f.readlines()
        data = list(map(lambda v: v.strip(), data))
        data = list(filter(None, data))
        for k, v in get_blocks(data):
            if k in blocks:
                blocks[k] += v
            else:
                blocks[k] = v
    for k, v in blocks.items():
        if SEPARATOR in k:
            multiple[k] = v
        elif k.startswith('.'):
            classes[k] = v
        elif k.startswith(':'):
            roots[k] = v
        elif k.startswith('#'):
            ids[k] = v
        elif k.startswith('@'):
            at_rules[k] = v
        else:
            elements[k] = v
    for kk in ORDER:
        keys = list(locals()[kk].keys())
        keys.sort()
        for k in keys:
            v = locals()[kk][k]
            print(f'{k} {{\n{build_block(v)}\n}}\n')
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str)
    args = parser.parse_args()
    sys.exit(main(args.file))
