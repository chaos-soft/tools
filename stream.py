#!/usr/bin/env python3
import asyncio
import sys

blank = '/root/tmp/obs.mp4'
input_ = 'xxx/xxx'
ip = '127.0.0.1'
output = 'xxx/xxx'

ffmpeg_blank = f'ffmpeg -v quiet -re -stream_loop -1 -i {blank} -c copy -f flv rtmp://{ip}/{output}'.split(' ')
ffmpeg_output = f'ffmpeg -v quiet -re -i rtmp://{ip}/{input_} -c copy -f flv rtmp://{ip}/{output}'.split(' ')
ffprobe = f'timeout 4s ffprobe -v quiet rtmp://{ip}/{input_}'.split(' ')


async def main():
    proc_blank = None
    proc_output = None
    while True:
        proc = await asyncio.create_subprocess_exec(ffprobe[0], *ffprobe[1:])
        returncode = await proc.wait()
        if returncode == 0:
            if proc_blank:
                proc_blank.kill()
                proc_blank = None
            if not proc_output:
                proc_output = await asyncio.create_subprocess_exec(ffmpeg_output[0], *ffmpeg_output[1:])
        else:
            if proc_output:
                proc_output.kill()
                proc_output = None
            if not proc_blank:
                proc_blank = await asyncio.create_subprocess_exec(ffmpeg_blank[0], *ffmpeg_blank[1:])


if __name__ == '__main__':
    asyncio.run(main())
    sys.exit(0)
