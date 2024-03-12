from __future__ import annotations

from typing import List
from dataclasses import dataclass
from pathlib import Path
import json


@dataclass
class ConfigFile:
    path: Path


@dataclass
class AppConf:
    app_cfg_path: Path
    app_theme_cfg: Path


@dataclass
class Theme:
    name: str
    apps_cfg: dict[str, AppConf]


def read_json_file(path: Path) -> dict:
    with path.open() as file:
        return json.load(file)


def build_themes_from_json(themes_json: dict) -> List[Theme]:
    themes_list = []
    for theme_json in themes_json:
        apps_cfg = {}
        for app_name, app_conf_json in theme_json["apps_cfg"].items():
            app_conf = AppConf(
                app_cfg_path=Path(app_conf_json["app_cfg_path"]),
                app_theme_cfg=Path(app_conf_json["app_theme_cfg"]),
            )
            apps_cfg[app_name] = app_conf

        theme = Theme(name=theme_json["name"], apps_cfg=apps_cfg)
        themes_list.append(theme)

    return themes_list


def read_themes_file(path: Path | str) -> List[Theme]:
    if isinstance(path, str):
        path = Path(path)

    themes_json = read_json_file(path)
    return build_themes_from_json(themes_json)


if __name__ == "__main__":
    print(read_themes_file("./config.json"))
