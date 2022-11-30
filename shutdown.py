#!/usr/bin/env python3
import argparse
import os
import time


def main(time_str: str) -> None:
    while True:
        t = time.localtime()
        if f'{t.tm_hour}:{t.tm_min}' == time_str:
            os.system('poweroff')
        time.sleep(60)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('time', type=str)
    args = parser.parse_args()
    main(args.time)
