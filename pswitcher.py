#!/usr/bin/env python3
import subprocess
import sys

CYRILLIC = r"йцукенгшщзхъфывапролджэячсмитьбю." + r"ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ?"
LATIN = r"qwertyuiop[]asdfghjkl;'zxcvbnm,./" + r'QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?'


def main() -> int:
    run("xdotool key --delay 100 Ctrl+x")
    clipboard = run("xsel --clipboard --output")
    for char in LATIN:
        if char in clipboard:
            TABLE = str.maketrans(LATIN, CYRILLIC)
            break
    else:
        TABLE = str.maketrans(CYRILLIC, LATIN)
    corrected = clipboard.translate(TABLE).strip()
    run("xsel --clipboard", input=corrected.encode("utf-8"))
    run("xdotool key --delay 100 Ctrl+v")
    return 0


def run(args_: str, **kwargs) -> str:
    args = args_.split(" ")
    cp = subprocess.run(args, capture_output=True, **kwargs)
    return cp.stdout.decode("utf-8")


sys.exit(main())
