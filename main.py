#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, TypeAlias

Json: TypeAlias = str | int | float | list["Json"] | dict[str, "Json"]


@dataclass
class ConfigFile:
    path: Path


@dataclass
class AppConf:
    real_cfg_path: Path
    theme_cfg: Path


@dataclass
class Theme:
    name: str
    apps_cfg: dict[str, AppConf]


def build_themes_from_json(themes_json: list[Json]) -> List[Theme]:
    themes_list = []
    for theme_json in themes_json:
        apps_cfg = {}
        for app_name, app_conf_json in theme_json.get("apps_cfg").items():  # type: ignore
            app_conf = AppConf(
                real_cfg_path=Path(app_conf_json.get("real_cfg_path")),  # type: ignore
                theme_cfg=Path(app_conf_json.get("theme_cfg")),  # type: ignore
            )
            apps_cfg[app_name] = app_conf

        theme = Theme(name=theme_json["name"], apps_cfg=apps_cfg)  # type: ignore
        themes_list.append(theme)

    return themes_list


def read_themes_file(path: Path | str) -> List[Theme]:
    if isinstance(path, str):
        path = Path(path)

    with path.open() as file:
        themes_json = json.load(file)
        return build_themes_from_json(themes_json)


def set_theme(theme: Theme):
    for app_cfg in theme.apps_cfg.values():
        if app_cfg.real_cfg_path.exists():
            os.remove(app_cfg.real_cfg_path)

        if not app_cfg.theme_cfg.exists():
            raise Exception(f"cfg {app_cfg.theme_cfg} theme not found")
        app_cfg.real_cfg_path.hardlink_to(app_cfg.theme_cfg)


def list_themes(themes: List[Theme]):
    print("Available themes:")
    for theme in themes:
        print(theme.name)


if __name__ == "__main__":
    # cfg = read_themes_file("./config.json")
    # set_theme(cfg[0])
    parser = argparse.ArgumentParser(description="Utility for managing themes.")
    parser.add_argument(
        "action", choices=["list", "set"], help="Action to perform: list or set"
    )
    parser.add_argument("--theme", help="Theme to set (required for 'set' action)")
    # parser.add_argument("file_path", help="Path to the themes JSON file")

    args = parser.parse_args()

    themes = read_themes_file("./config.json")

    if args.action == "list":
        list_themes(themes)
    elif args.action == "set":
        if not args.theme:
            parser.error("Theme argument is required for 'set' action")
        selected_theme = next(
            (theme for theme in themes if theme.name == args.theme), None
        )
        if selected_theme:
            set_theme(selected_theme)
            print(f"Theme '{selected_theme.name}' has been set.")
        else:
            print(f"Theme '{args.theme}' not found.")
