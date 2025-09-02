#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys


def get_extensions(path):
    output = subprocess.run(['file', '-b', '--extension', path], capture_output=True, text=True)
    return output.stdout.rstrip('\n')


def main() -> int:
    for v in Path.cwd().iterdir():
        converter = {
            'jpeg/jpg/jpe/jfif': '.jpg',
            'png': '.png',
        }
        ext = converter.get(get_extensions(v))
        if ext:
            new = v.with_suffix(ext)
            if new != v:
                print(v)
                print(new)
                subprocess.run(['mv', '-n', v, new], check=True)
    return 0


sys.exit(main())
