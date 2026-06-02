#!/usr/bin/env python3
import argparse
import sys

LS = list[str]
TS = tuple[str, ...]

GARBAGE: str = " {;"
INDENTATION: str = "  "
ORDER: LS = ["roots", "multiple", "elements", "ids", "classes", "at_rules"]


class Block:
    elements: LS
    key: TS

    def __init__(self, key: TS) -> None:
        self.elements = []
        self.key = key

    def __repr__(self) -> str:
        return "\n".join(self.get_elements())

    def add(self, element: str) -> None:
        self.elements.append(element)

    def get_close(self) -> str:
        indentation = INDENTATION * (len(self.key) - 1)
        return "{0}}}".format(indentation)

    def get_element(self, indentation: str, value: str) -> str:
        return "{}{}{}".format(indentation, value, {"/": ""}.get(value[-1], ";"))

    def get_elements(self) -> LS:
        self.elements.sort()
        indentation = INDENTATION * len(self.key)
        return list(map(lambda v: self.get_element(indentation, v), self.elements))

    def get_key(self, index: int = -1) -> str:
        indentation = INDENTATION * (len(self.key) + index)
        return "{0}{1} {{".format(indentation, self.key[index])

    def to_list(self) -> LS:
        r: LS = []
        r.append(self.get_key())
        if elements := self.get_elements():
            r.extend(elements)
        r.append(self.get_close())
        r.append("")
        return r


DTSB = dict[TS, Block]
LB = list[Block]
TREE: DTSB = {}


def get_tree(data: LS) -> None:
    key: LS = []
    tree: LB = []
    for v in data:
        if "{" in v:
            k = ",\n".join(sorted(map(lambda vv: vv.strip(GARBAGE), v.split(","))))
            key.append(k)
            tree.append(Block(key=tuple(key)))
        elif "}" in v:
            block = tree.pop()
            TREE[tuple(key)] = block
            key.pop()
        else:
            tree[-1].add(v.strip(GARBAGE))
    assert len(key) == 0
    assert len(tree) == 0


def main(file: str) -> int:
    at_rules: DTSB = {}
    classes: DTSB = {}
    elements: DTSB = {}
    ids: DTSB = {}
    multiple: DTSB = {}
    roots: DTSB = {}

    data = file.replace(",\n", ",").split("\n")
    data = list(filter(None, data))
    get_tree(data)

    for k, v in TREE.items():
        if "," in k[0]:
            multiple[k] = v
        elif k[0].startswith("."):
            classes[k] = v
        elif k[0].startswith(":"):
            roots[k] = v
        elif k[0].startswith("#"):
            ids[k] = v
        elif k[0].startswith("@"):
            at_rules[k] = v
        else:
            elements[k] = v

    output: LS = []
    for kk in ORDER:
        dict_: DTSB = locals()[kk]
        if dict_:
            keys = list(dict_.keys())
            # Сортировка по алфавиту всех ключей.
            keys.sort()
            # Обратная сортировка для древовидных ключей.
            keys = list(
                sorted(
                    keys,
                    key=lambda v: "".join(v) if len(v) > 1 else "z",
                    reverse=True,
                )
            )
            # Сортировка по длине ключа.
            keys = list(sorted(keys, key=lambda v: len(v)))
            for k in keys:
                if len(k) > 1:
                    i = output.index(dict_[k].get_key(index=-2)) + 1
                    output[i:i] = dict_[k].to_list()
                else:
                    output.extend(dict_[k].to_list())
    str_ = "\n".join(output).replace("}\n\n}", "}\n}")
    print(str_)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "infile",
        default=sys.stdin,
        nargs="?",
        type=argparse.FileType("r"),
    )
    args = parser.parse_args()
    sys.exit(main(args.infile.read()))
