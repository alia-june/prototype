"""Command-line construction for the declared prototype example."""

import argparse
import json
from pathlib import Path
import sys

from .rehydration import ConstructionError, rehydrate


def write_outputs(directory, result):
    payloads = {
        "example.py": result["python"],
        "CONTRACT.md": "# Rehydrated example contract\n\n" + result["human"] + "\n",
        "TRACE.json": json.dumps(
            {key: result[key] for key in ("trace", "inverse", "spans")},
            ensure_ascii=False, indent=2
        ) + "\n",
    }
    if directory.exists():
        if not directory.is_dir():
            raise FileExistsError("output location is not a directory")
        conflicts = [name for name in payloads if (directory / name).exists()]
        if conflicts:
            raise FileExistsError(
                "refusing to overwrite existing outputs: " + ", ".join(conflicts)
            )
    directory.mkdir(parents=True, exist_ok=True)
    for name, content in payloads.items():
        with (directory / name).open("x", encoding="utf-8", newline="\n") as output:
            output.write(content)


def main(argv):
    parser = argparse.ArgumentParser(
        prog="python -m code_lexigraph",
        description="Reconstruct the declared code-lexigraph prototype example."
    )
    parser.add_argument("bundle", type=Path, help="UTF-8 JSON construction bundle")
    parser.add_argument(
        "--out", type=Path, default=argparse.SUPPRESS,
        help="write example.py, CONTRACT.md and TRACE.json into this directory"
    )
    args = parser.parse_args(argv)
    try:
        bundle = json.loads(args.bundle.read_text(encoding="utf-8"))
        result = rehydrate(bundle)
        if hasattr(args, "out"):
            write_outputs(args.out, result)
            print("Constructed example.py, CONTRACT.md and TRACE.json in " + str(args.out))
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, UnicodeError, ConstructionError, KeyError, TypeError,
            ValueError, SyntaxError, IndexError, AttributeError) as error:
        print("code-lexigraph: " + str(error), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
