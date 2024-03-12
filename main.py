from __future__ import annotations

from typing import List, Any, TypeAlias
from dataclasses import dataclass
from pathlib import Path
import os
import json


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


Json: TypeAlias = str | int | float | list["Json"] | dict[str, "Json"]


def build_themes_from_json(themes_json: Json) -> List[Theme]:
    themes_list = []
    if not isinstance(themes_json, int) and not isinstance(themes_json, float):
        for theme_json in themes_json:
            app_cfg_list = {}
            apps_cfg = theme_json.get("apps_cfg")  # type: ignore

            if apps_cfg is None:
                raise Exception("cant decode config file")

            for app_name, app_conf_json in apps_cfg.items():  # type: ignore
                app_conf = AppConf(
                    real_cfg_path=Path(app_conf_json.get("real_cfg_path")),  # type: ignore
                    theme_cfg=Path(app_conf_json.get("theme_cfg")),  # type: ignore
                )
                app_cfg_list[app_name] = app_conf

            theme = Theme(name=theme_json["name"], apps_cfg=app_cfg_list)  # type: ignore
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

        app_cfg.real_cfg_path.hardlink_to(app_cfg.theme_cfg)


if __name__ == "__main__":
    cfg = read_themes_file("./config.json")
    set_theme(cfg[0])
