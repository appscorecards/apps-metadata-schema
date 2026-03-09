"""Validate scorecard markdown files against ``schema/scorecard.schema.json``.

Usage:
    python -m validator.validate <file.md> [<file.md> ...]

Requires ``PyYAML`` and ``jsonschema``. Exits non-zero on any failure.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    import yaml  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]

try:
    from jsonschema import Draft202012Validator  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover
    Draft202012Validator = None  # type: ignore[assignment]


FRONT_MATTER_DELIM = "---"
SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schema" / "scorecard.schema.json"


def extract_front_matter(text: str) -> str:
    """Return the YAML front-matter block of ``text`` or raise ``ValueError``.

    A well-formed scorecard starts with ``---`` on the first line and has a
    matching ``---`` a few lines down.
    """

    lines = text.splitlines()
    if not lines or lines[0].strip() != FRONT_MATTER_DELIM:
        raise ValueError("file does not start with front-matter delimiter '---'")
    for idx in range(1, len(lines)):
        if lines[idx].strip() == FRONT_MATTER_DELIM:
            return "\n".join(lines[1:idx])
    raise ValueError("front-matter block is not closed")


def parse_front_matter(text: str) -> Dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is required; run `pip install pyyaml`.")
    raw = extract_front_matter(text)
    data = yaml.safe_load(raw)
    if not isinstance(data, dict):
        raise ValueError("front-matter is not a mapping")
    return data


def load_schema() -> Dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def validate_data(data: Dict[str, Any]) -> List[str]:
    """Return a list of human-readable error messages (empty if valid)."""

    if Draft202012Validator is None:
        raise RuntimeError("jsonschema is required; run `pip install jsonschema`.")
    validator = Draft202012Validator(load_schema())
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))
    return [
        f"{'.'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}"
        for e in errors
    ]


def validate_file(path: Path) -> Tuple[bool, List[str]]:
    try:
        text = path.read_text(encoding="utf-8")
        data = parse_front_matter(text)
    except (OSError, ValueError) as err:
        return False, [str(err)]
    errors = validate_data(data)
    return (not errors), errors


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="validate-scorecard",
        description="Validate scorecard markdown files against the JSON schema.",
    )
    parser.add_argument("files", nargs="+", type=Path)
    args = parser.parse_args(argv)

    any_fail = False
    for path in args.files:
        ok, errors = validate_file(path)
        if ok:
            print(f"{path}: OK")
        else:
            any_fail = True
            print(f"{path}: FAIL")
            for err in errors:
                print(f"  - {err}")

    return 1 if any_fail else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
