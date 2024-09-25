#!/usr/bin/env python3
import argparse
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
            page.goto(v)
            page.locator('.product-page').wait_for()
            canvas = page.locator('canvas.photo-zoom__preview')
            canvas.wait_for()
            canvas.click()
            gf = page.locator('.gallery-full')
            gf.wait_for()
            images = gf.locator('.gallery-full__item')
            for vv in images.all():
                print(vv.get_attribute('data-zoom-image'))
            page.close()
            time.sleep(TIMEOUT)
    browser.close()
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str)
    args = parser.parse_args()
    sys.exit(main(args.file))
