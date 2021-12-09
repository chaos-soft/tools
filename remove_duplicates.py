#!/usr/bin/env python3
import argparse
import sys


def main(infile: str) -> None:
    unique = []
    for line in infile:
        line = line.rstrip('\n')
        if line and line not in unique:
            print(line)
            unique.append(line)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'),
                        default=sys.stdin)
    args = parser.parse_args()
    main(args.infile)
