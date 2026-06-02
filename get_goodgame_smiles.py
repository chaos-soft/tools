#!/usr/bin/env python3
import argparse
import json
import sys

import STPyV8


def main(file: str) -> int:
    with open(file) as f:
        data = f.read()
        smiles = {}
        with STPyV8.JSContext() as ctxt:
            r = ctxt.eval(data[4:])
            for v in r.Smiles:
                smiles[v.name] = v.img_gif if v.animated else v.img_big
            r = ctxt.eval("Object.entries(Global.Channel_Smiles)")
            for vv in r:
                for v in vv[1]:
                    smiles[v.name] = v.img_gif if v.animated else v.img_big
        print(json.dumps(smiles, sort_keys=True, indent=4, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str)
    args = parser.parse_args()
    sys.exit(main(args.file))
