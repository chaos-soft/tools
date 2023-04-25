#!/usr/bin/env python3
import argparse
import os
import sys
import time


def main(hour: int, min: int) -> int:
    try:
        while True:
            t = time.localtime()
            if t.tm_hour == hour and t.tm_min == min:
                os.system('poweroff')
            time.sleep(60)
    except KeyboardInterrupt:
        print()
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('time', type=str)
    args = parser.parse_args()
    hour, min = map(int, args.time.split(':'))
    sys.exit(main(hour, min))
