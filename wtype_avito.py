#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys
import time

HOME = Path.home()
TIMEOUT_1S: int = 1
TIMEOUT_5S: int = 5
URL: str = "https://www.avito.ru/profile/items/old/all?p={}&s=4"
XPATH: str = (
    "/html/body/div[2]/div/div[9]/div/div[2]/personal-items-items/div/div/div/div/form/div/div/div[3]"
)


def main() -> int:
    for i in range(1, 4 + 1):
        run(f"{HOME}/Downloads/waterfox/waterfox --new-tab {URL.format(i)}", TIMEOUT_5S)
        run("wtype -k f12")
        run("wtype -M ctrl f -m ctrl")
        run(f"wtype {XPATH}")
        run("wtype -k return")
        for i in range(1, 6 + 1):
            run("wtype -k tab")
        run("wtype -k menu")
        for i in range(1, 5 + 1):
            run("wtype -k up")
        run("wtype -k return")
    return 0


def run(args: str, sleep: int = TIMEOUT_1S) -> None:
    print(subprocess.run(args, shell=True))
    time.sleep(sleep)


if __name__ == "__main__":
    sys.exit(main())
