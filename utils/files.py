"""
Functions for file utilities
"""

from pathlib import Path
import json

import jq


def read_json(path: Path, jq_program: str | None):
    """
    Read the json file at path and extract key(s), if any, using a jq program
    """

    try:
        with open(path, "r", encoding="utf-8") as f:

            obj = json.load(f)

            if not jq_program:
                return obj

            return jq.compile(jq_program).input_value(obj).first()

    except Exception as e:

        if not jq_program:
            raise ValueError(f"Error reading {path} as JSON") from e

        raise ValueError(
            f"Error reading {path} as JSON and program {jq_program}"
        ) from e


def write_json(path: Path, obj):
    """
    Write the object to a path
    """

    assert path.suffix == ".json", f"Path {path} not a .json file"

    with open(path, "w+", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False)
