#!/usr/bin/env python3
from pathlib import Path
import argparse
import subprocess
import sys
import time

HOME = Path.home()
TIMEOUT_1S: int = 1
TIMEOUT_5S: int = 5


def main(file: str) -> int:
    with open(file) as f:
        for v in f.readlines():
            v = v.strip()
            if not v or v.startswith('#'):
                continue
            run(f'{HOME}/Downloads/waterfox/waterfox --new-tab {v}', TIMEOUT_5S)
            run('xdotool key F12')
            run('xdotool mousemove 1110 540', TIMEOUT_1S)
            run('xdotool click 1', TIMEOUT_5S)
            run('xdotool key Escape')
            run('xdotool mousemove 1110 810 click 3')
            run('xdotool key c')
            run('xdotool key c')
            print(run('xsel --clipboard --output') + ' -LOJ')
            print('sleep 0.5')
    return 0


def run(command: str, sleep: int = TIMEOUT_1S) -> str:
    args = command.split(' ')
    cp = subprocess.run(args, capture_output=True)
    time.sleep(sleep)
    return cp.stdout.decode('utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str)
    args = parser.parse_args()
    sys.exit(main(args.file))
