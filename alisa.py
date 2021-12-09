#!/usr/bin/env python3
from typing import Iterable
import re
import subprocess
import time

RANGES: dict[int, Iterable[int]] = {
    30: range(0, 50),
    50: range(50, 60),
    60: range(60, 65),
    65: range(65, 70),
    100: range(70, 100),
}


def main() -> None:
    re_temp = re.compile(r'GPUCoreTemp.+(\d{2})\.')
    args = ['nvidia-settings', '-a', 'GPUFanControlState=1']
    subprocess.run(args, check=True)
    while True:
        args = ['nvidia-settings', '-q', 'GPUCoreTemp']
        cp = subprocess.run(args, check=True, capture_output=True)
        temp = int(re_temp.search(str(cp.stdout)).group(1))
        for k, v in RANGES.items():
            if temp in v:
                set_fan_speed(k)
                break
        time.sleep(3)


fan_speed: int = 0


def set_fan_speed(fs: int) -> None:
    global fan_speed
    if fan_speed != fs:
        fan_speed = fs
        args = ['nvidia-settings', '-a', f'GPUTargetFanSpeed={fan_speed}']
        subprocess.run(args, check=True)


if __name__ == '__main__':
    main()
