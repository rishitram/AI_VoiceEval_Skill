"""
Validate all transcripts in transcripts/ against the schema.

Usage:
    python validate_transcripts.py
    python validate_transcripts.py ../transcripts/
"""

import json
import sys
from pathlib import Path

from schema import Transcript

TRANSCRIPTS_DIR = Path(__file__).resolve().parent.parent / "transcripts"


def validate(path: Path) -> list[str]:
    errors = []
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return [f"invalid JSON: {e}"]

    required_top = {"call_id", "scenario", "turns"}
    missing = required_top - set(data.keys())
    if missing:
        errors.append(f"missing top-level keys: {missing}")

    if data.get("call_id") != path.stem:
        errors.append(f"call_id '{data.get('call_id')}' != filename '{path.stem}'")

    scenario = data.get("scenario", {})
    for key in ("description", "goal"):
        if key not in scenario:
            errors.append(f"scenario missing '{key}'")

    turns = data.get("turns", [])
    if len(turns) < 2:
        errors.append("fewer than 2 turns")

    for i, turn in enumerate(turns):
        for key in ("speaker", "text", "turn_index", "timestamp"):
            if key not in turn:
                errors.append(f"turn {i} missing '{key}'")
        if turn.get("speaker") not in ("patient", "agent"):
            errors.append(f"turn {i} invalid speaker: {turn.get('speaker')}")
        if turn.get("turn_index") != i:
            errors.append(f"turn {i} has turn_index {turn.get('turn_index')}")

    try:
        Transcript.from_dict(data)
    except Exception as e:
        errors.append(f"schema load failed: {e}")

    return errors


def main():
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else TRANSCRIPTS_DIR
    files = sorted(target.glob("*.json"))
    if not files:
        print(f"No JSON files in {target}", file=sys.stderr)
        sys.exit(1)

    total_errors = 0
    for f in files:
        errs = validate(f)
        if errs:
            total_errors += len(errs)
            print(f"FAIL {f.name}:")
            for e in errs:
                print(f"  - {e}")

    if total_errors:
        print(f"\n{total_errors} error(s) in {len(files)} files", file=sys.stderr)
        sys.exit(1)

    print(f"OK — {len(files)} transcripts validated")


if __name__ == "__main__":
    main()
