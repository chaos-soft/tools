#!/usr/bin/env python3
import subprocess
import sys

BLANK: str = "/mnt/xxx2/memory card/cinelerra/blank/obs.mp4"
OUTPUT: str = "rtmp://xxx/xxx/xxx"

DOCKER_START: str = "docker compose up -d"
DOCKER_STOP: str = "docker compose stop"
FFMPEG: str = (
    "ffmpeg -loglevel error -stats -re -stream_loop -1 -i '{}' -c copy -f flv {}"
).format(BLANK, OUTPUT)


def main() -> int:
    try:
        while True:
            s = input("blank [1], docker_start [2], docker_stop [3], quit [q] ") or "1"
            match s:
                case "1":
                    print("blank")
                    subprocess.run(FFMPEG, shell=True)
                case "2":
                    print("docker_start")
                    subprocess.run(DOCKER_START, shell=True)
                case "3":
                    print("docker_stop")
                    subprocess.run(DOCKER_STOP, shell=True)
                case "q":
                    break
    except KeyboardInterrupt:
        print()
        return 128 + 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
