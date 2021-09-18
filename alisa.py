#!/usr/bin/env python3
import subprocess
import time
import xml.etree.ElementTree as ET

fan_speed: int = 25


def main() -> None:
    args = ['nvidia-settings', '-a', 'GPUFanControlState=1']
    subprocess.run(args, check=True)
    set_fan_speed(5)
    while True:
        args = ['nvidia-smi', '-q', '-x']
        cp = subprocess.run(args, check=True, capture_output=True)
        root = ET.fromstring(cp.stdout)
        temperature = root[4].find('temperature')[0]
        if temperature.tag != 'gpu_temp':
            return
        t = int(temperature.text.split(' ')[0])
        if t > 65:
            set_fan_speed(5)
        elif t < 55:
            set_fan_speed(-5)
        # set_fan_speed(10) if t > 60 else set_fan_speed(-10)
        time.sleep(2.5)


def set_fan_speed(offset: int = 0) -> None:
    global fan_speed
    fs = fan_speed + offset
    if fs > 25 and fs < 100:
        fan_speed = fs
        args = ['nvidia-settings', '-a', f'GPUTargetFanSpeed={fan_speed}']
        subprocess.run(args, check=True)


if __name__ == '__main__':
    main()
