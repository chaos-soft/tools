#!/usr/bin/env python3
from pathlib import Path
import argparse
import subprocess
import sys
import time
import yaml

HOME = Path.home()
TIMEOUT_1S: int = 1
TIMEOUT_5S: int = 5
URL: str = 'https://studio.rutube.ru/video-editor/'


def main(file: str) -> int:
    with open(file) as f:
        data = yaml.safe_load(f)
        for i, v in enumerate(data):
            run(f'{HOME}/Downloads/waterfox/waterfox --new-tab {URL}{v['u']}', TIMEOUT_5S)

            run('xdotool mousemove 1000 350 click 1')
            run('xdotool key --delay 100 Ctrl+a BackSpace')
            run(['xdotool', 'type', v['t']])
            run('xdotool mousemove 1000 500 click 1')
            run('xdotool key --delay 100 Ctrl+a BackSpace')
            run(['xdotool', 'type', v['d'].replace('\n', '\r\n')])

            run('xdotool click 5 click 5 click 5')

            run('xdotool mousemove 1100 460 click 1')
            run('xdotool mousemove 1100 500 click 1')

            run('xdotool mousemove 350 980 click 1')

            run('xdotool mousemove 360 650 click 3')
            run('xdotool key o')
            print(v['u'] + ': ' + run('xsel --clipboard --output'))
        print(i + 1)
    return 0


def run(args: str | list, sleep: int = TIMEOUT_1S) -> str:
    if type(args) is str:
        args = args.split(' ')
    cp = subprocess.run(args, capture_output=True)
    time.sleep(sleep)
    return cp.stdout.decode('utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str)
    args = parser.parse_args()
    sys.exit(main(args.file))
