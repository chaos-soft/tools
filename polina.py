#!/usr/bin/env python3
from pathlib import Path
from typing import Any
import argparse
import filecmp
import re
import subprocess
import sys

import yaml

APPLICATIONS_PATH: Path = Path.home() / ".local/share/applications"
BACKUP_PATH: Path = Path.home() / ".polina_backup"
CONFIG: dict[str, Any] = {}
DESKTOP_FILES: dict[str, Any] = {}
VARIABLES: dict[str, str] = {}

ENDC: str = "\033[0m"
WARNING: str = "\033[91m"

DESKTOP_ENTRY: str = """[Desktop Entry]
Name={}
Type=Application
{}
"""


def append(file_path: str, str_: str) -> None:
    str_ = replace_variables(str_)
    print(f"append {file_path}")
    Path(file_path).parent.mkdir(mode=0o755, parents=True, exist_ok=True)
    with open(file_path, "a") as f:
        f.write(str_)


def append_once(file_path: str, str_: str) -> None:
    if not Path(file_path).exists():
        append(file_path, str_)


def backup() -> None:
    BACKUP_PATH.mkdir(mode=0o755, parents=True, exist_ok=True)
    for file_path in CONFIG.keys():
        if "append_once" in CONFIG[file_path]:
            continue
        if (
            Path(file_path).exists()
            and not (BACKUP_PATH / get_backup_name(file_path)).exists()
        ):
            print(f"backup {file_path}")
            subprocess.run(
                ["cp", "-rp", file_path, BACKUP_PATH / get_backup_name(file_path)],
                check=True,
            )


def check_append(file_path: str, str_: str) -> None:
    if not Path(file_path).exists():
        return None
    with open(file_path) as f:
        data = f.read()
        str_ = replace_variables(str_)
        for v in str_.strip().split("\n"):
            if v not in data:
                print(f"{v} {WARNING}not in{ENDC} {file_path}")


def check_backup() -> None:
    for file_path in CONFIG.keys():
        bp = BACKUP_PATH / get_backup_name(file_path)
        if Path(file_path).exists() and bp.exists():
            if not filecmp.cmp(file_path, bp, shallow=True):
                print(f"not equal {file_path}")


def check_lines() -> None:
    for file_path, actions in CONFIG.items():
        if "append" in actions:
            check_append(file_path, actions["append"])
        if "append_once" in actions:
            check_append(file_path, actions["append_once"])
        if "insert_after" in actions:
            check_append(
                file_path,
                "".join([x for y in actions["insert_after"].values() for x in y]),
            )
        if "replace_old" in actions:
            check_replace(
                file_path, actions["replace_old"], actions.get("replace_new", "")
            )


def check_replace(file_path: str, old: str, new: str) -> None:
    if not Path(file_path).exists():
        return None
    with open(file_path) as f:
        data = f.read()
        old_list = list(filter(None, old.split("\n")))
        new_list = list(filter(None, new.split("\n")))
        for i, _ in enumerate(old_list):
            remove = old_list[i]
            remove = replace_variables(remove)
            if remove in data:
                print(f"{remove} {WARNING}in{ENDC} {file_path}")
            try:
                insert = new_list[i]
                insert = replace_variables(insert)
                if insert not in data:
                    print(f"{insert} {WARNING}not in{ENDC} {file_path}")
            except IndexError:
                pass


def desktop() -> None:
    for name, item in DESKTOP_FILES.items():
        file_path = APPLICATIONS_PATH / re.sub(
            r"[/]", "", f"{name.lower()}.desktop"
        ).replace(" ", "-")
        print(file_path)
        with open(file_path, "w") as f:
            de = DESKTOP_ENTRY.format(name, item.strip("\n"))
            de = replace_variables(de)
            f.write(de)


def get_backup_name(file_path: str) -> str:
    return file_path.replace("/", "__").lstrip("__")


def insert_after(file_path: str, dict_: dict[str, str]) -> None:
    if Path(file_path).exists():
        print(f"insert_after {file_path}")
        with open(file_path, "r+") as f:
            data = f.readlines()
            for k, v in dict_.items():
                try:
                    i = data.index(k)
                    data.insert(i + 1, v)
                except ValueError:
                    pass
            f.seek(0)
            f.writelines(data)


def load_config(file: str) -> None:
    global CONFIG, DESKTOP_FILES, VARIABLES
    with open(file) as f:
        CONFIG = yaml.safe_load(f)
        if CONFIG.get("desktop_files"):
            DESKTOP_FILES = CONFIG.pop("desktop_files")
        if CONFIG.get("variables"):
            VARIABLES = CONFIG.pop("variables")


def rebuild() -> None:
    reset()
    for file_path, actions in CONFIG.items():
        if "append" in actions:
            append(file_path, actions["append"])
        if "append_once" in actions:
            append_once(file_path, actions["append_once"])
        if "insert_after" in actions:
            insert_after(file_path, actions["insert_after"])
        if "replace_old" in actions:
            replace(file_path, actions["replace_old"], actions.get("replace_new", ""))


def replace(file_path: str, old: str, new: str) -> None:
    if Path(file_path).exists():
        print(f"replace {file_path}")
        with open(file_path, "r+") as f:
            data = f.read()
            old = replace_variables(old)
            new = replace_variables(new)
            old_list = list(filter(None, str(old).split("\n")))
            new_list = list(filter(None, str(new).split("\n")))
            for i, _ in enumerate(old_list):
                try:
                    data = data.replace(old_list[i], new_list[i])
                except IndexError:
                    data = data.replace(old_list[i], "")
            f.seek(0)
            f.write(data)
            f.truncate()


def replace_variables(str_: str) -> str:
    for var, str__ in VARIABLES.items():
        if var in str_:
            str_ = str_.replace(var, str__)
    return str_


def reset() -> None:
    for file_path, actions in CONFIG.items():
        if "append_once" in actions:
            continue
        fp = Path(file_path)
        bp = BACKUP_PATH / get_backup_name(file_path)
        if bp.exists():
            print(f"reset {file_path}")
            fp.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
            if fp.exists():
                fp.unlink()
            subprocess.run(["cp", "-rp", bp, fp], check=True)
        elif fp.exists():
            s = input(f"{WARNING}rm{ENDC} {file_path}? [Y/n] ") or "Y"
            if s == "Y":
                fp.unlink()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", type=str)
    parser.add_argument(
        "action",
        choices=[
            "backup",
            "check_backup",
            "check_lines",
            "desktop",
            "rebuild",
            "reset",
        ],
        type=str,
    )
    args = parser.parse_args()
    load_config(args.config_file)
    eval(f"{args.action}()")
    sys.exit(0)
