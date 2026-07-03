"""Stable JSON IO helpers."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any


def read_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return data


def write_json_atomic(path: str | Path, data: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=target.parent,
        delete=False,
        newline="\n",
    ) as file:
        json.dump(data, file, ensure_ascii=True, indent=2, sort_keys=True)
        file.write("\n")
        temp_name = file.name

    os.replace(temp_name, target)
