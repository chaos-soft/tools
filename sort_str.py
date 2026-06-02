#!/usr/bin/env python3
import argparse
import sys


def main(clipboard: str) -> int:
    separators = (("\n", "\n"), ("|", "|"), (",", ", "), (" ", " "))
    for sep in separators:
        if sep[0] in clipboard:
            data = list(
                set(filter(bool, map(lambda v: v.strip(), clipboard.split(sep[0]))))
            )
            data.sort()
            corrected = sep[1].join(data)
            break
    print(corrected, end="")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "infile",
        default=sys.stdin,
        nargs="?",
        type=argparse.FileType("r"),
    )
    args = parser.parse_args()
    sys.exit(main(args.infile.read()))
