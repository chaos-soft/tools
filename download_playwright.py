#!/usr/bin/env python3
import argparse
import subprocess
import sys
import time

from playwright.sync_api import sync_playwright

TIMEOUT: int = 2


def main(file: str) -> int:
    playwright = sync_playwright().start()
    browser = playwright.firefox.launch(headless=False)
    with open(file) as f:
        for v in f.readlines():
            v = v.strip()
            if not v or v.startswith('#'):
                continue
            page = browser.new_page()
            page.goto(v, wait_until='domcontentloaded')
            image = page.locator('.wrap > a:nth-child(1) > img:nth-child(1)')
            args = ['curl', '-LOJ', image.evaluate('(e) => e.src')]
            print(subprocess.run(args))
            page.close()
            time.sleep(TIMEOUT)
    browser.close()
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str)
    args = parser.parse_args()
    sys.exit(main(args.file))
