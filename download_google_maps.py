#!/usr/bin/env python3
import subprocess
import sys


def main() -> int:
    for i in range(1, 31):
        run("xdotool key Ctrl+c")
        run("xdotool key Down")
        print("curl -LOJ '{}'".format(run("xsel --clipboard --output")))
    return 0


def run(args: str) -> str:
    cp = subprocess.run(args.split(" "), capture_output=True)
    return cp.stdout.decode("utf-8")


if __name__ == "__main__":
    sys.exit(main())
