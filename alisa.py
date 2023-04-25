#!/usr/bin/env python3
from typing import Iterable
import json
import os
import subprocess
import sys
import time

BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
RANGES: dict[int, Iterable[int]] = {}


def load_config() -> None:
    global RANGES
    with open(os.path.join(BASE_DIR, 'alisa_config.json')) as f:
        data = json.load(f)
    for k, v in data.items():
        RANGES[int(k)] = range(v[0], v[1])


def main() -> int:
    try:
        args = ['nvidia-settings', '-a', 'GPUFanControlState=1']
        subprocess.run(args, check=True)
        while True:
            args = ['nvidia-settings', '-q', 'GPUCoreTemp', '-t']
            cp = subprocess.run(args, check=True, capture_output=True)
            temp = int(cp.stdout)
            for k, v in RANGES.items():
                if temp in v:
                    set_fan_speed(k)
                    break
            time.sleep(2)
    except KeyboardInterrupt:
        print()
    return 0


fan_speed: int = 0


def set_fan_speed(fs: int) -> None:
    global fan_speed
    if fan_speed != fs:
        fan_speed = fs
        args = ['nvidia-settings', '-a', f'GPUTargetFanSpeed={fan_speed}']
        subprocess.run(args, check=True)


if __name__ == '__main__':
    load_config()
    sys.exit(main())
