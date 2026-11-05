#!/usr/bin/env python3
"""[GENERATED-SCAFFOLD] Deterministic assembler for modular hardening prompts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from string import Template


ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.json"
MODULE_DIR = ROOT / "modules"
BUILD_DIR = ROOT / "builds"
UNLOCK_BINDING_EXCLUDED = {
    "AGE_GATE_CONTROL_STATE",
    "AGE_GATE_UNLOCK_CONTROL_PLANE",
    "AGE_GATE_UNLOCK_RECEIPT_ID",
    "AGE_GATE_UNLOCK_EXPIRES_AT",
    "AGE_GATE_UNLOCK_CONFIG_SHA256",
    "AGE_GATE_UNLOCK_REPLAY_STATE",
}


@dataclass(frozen=True)
class Assembly:
    text: str
    profiles: tuple[str, ...]
    modules: tuple[str, ...]
    unresolved_variables: tuple[str, ...]
    missing_required_values: tuple[str, ...]


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def parse_assignments(items: list[str], allowed: set[str]) -> dict[str, str]:
    values: dict[str, str] = {}
    for item in items:
        if "=" not in item:
            raise SystemExit(f"invalid --set value {item!r}; expected NAME=VALUE")
        key, value = item.split("=", 1)
        key = key.strip()
        if not key:
            raise SystemExit("variable name cannot be empty")
        if key not in allowed:
            raise SystemExit(f"unknown variable: {key}")
        if key in values:
            raise SystemExit(f"variable assigned more than once: {key}")
        values[key] = value
    return values


def parse_profiles(items: list[str], config: dict) -> list[str]:
    raw = items or ["standard"]
    profiles: list[str] = []
    for item in raw:
        for name in item.split(","):
            name = name.strip()
            if not name:
                raise SystemExit("profile name cannot be empty")
            if name not in config["profiles"]:
                raise SystemExit(f"unknown profile: {name}")
            if name not in profiles:
                profiles.append(name)
    return profiles


def validate_module_names(names: set[str], known: set[str], operation: str) -> None:
    unknown = names - known
    if unknown:
        raise SystemExit(f"unknown modules for {operation}: {', '.join(sorted(unknown))}")


def close_dependencies(
    selected: set[str], dependencies: dict[str, list[str]], disabled: set[str]
) -> set[str]:
    changed = True
    while changed:
        changed = False
        for module in tuple(selected):
            for dependency in dependencies.get(module, []):
                if dependency in disabled:
                    raise SystemExit(
                        f"cannot disable {dependency}; it is required by {module}"
                    )
                if dependency not in selected:
                    selected.add(dependency)
                    changed = True
    return selected


def select_modules(
    config: dict,
    profiles: list[str],
    enables: list[str],
    disables: list[str],
) -> set[str]:
    known = set(config["module_order"])
    enabled = set(enables)
    disabled = set(disables)
    validate_module_names(enabled, known, "--enable")
    validate_module_names(disabled, known, "--disable")

    overlap = enabled & disabled
    if overlap:
        raise SystemExit(
            "modules cannot be both enabled and disabled: "
            + ", ".join(sorted(overlap))
        )

    mandatory = set(config["mandatory_modules"])
    forbidden_disable = mandatory & disabled
    if forbidden_disable:
        raise SystemExit(
            "mandatory modules cannot be disabled: "
            + ", ".join(sorted(forbidden_disable))
        )

    profile_modules: set[str] = set()
    for profile in profiles:
        profile_modules.update(config["profiles"][profile])

    profile_downgrade = profile_modules & disabled
    if profile_downgrade:
        raise SystemExit(
            "selected-profile modules cannot be disabled; choose a smaller base profile "
            "and add modules explicitly: "
            + ", ".join(sorted(profile_downgrade))
        )

    selected = mandatory | profile_modules | enabled
    unselected_disable = disabled - selected
    if unselected_disable:
        raise SystemExit(
            "cannot disable modules that are not selected: "
            + ", ".join(sorted(unselected_disable))
        )
    selected -= disabled
    return close_dependencies(selected, config["dependencies"], disabled)


def encode_prompt_scalar(value: str) -> str:
    """Encode a value as one ASCII JSON string that cannot escape Markdown fences."""
    encoded = json.dumps(str(value), ensure_ascii=True)
    return (
        encoded.replace("`", "\\u0060")
        .replace("$", "\\u0024")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
    )


def missing_required_values(config: dict, selected: set[str], values: dict[str, str]) -> list[str]:
    required = set(config["required_variables"].get("always", []))
    by_module = config["required_variables"].get("by_module", {})
    for module in selected:
        required.update(by_module.get(module, []))
    unset = set(config["unset_values"])
    return sorted(name for name in required if values.get(name, "") in unset)


def validate_allowed_values(config: dict, values: dict[str, str]) -> None:
    for name, allowed in config.get("allowed_values", {}).items():
        value = values.get(name)
        if value not in allowed:
            raise SystemExit(
                f"invalid value for {name}: {value!r}; allowed: "
                + ", ".join(allowed)
            )


def age_gate_binding_sha256(
    config: dict, selected: set[str], values: dict[str, str]
) -> str:
    """Hash the exact non-secret configuration an unlock receipt authorizes."""
    payload = {
        "schema_version": config["schema_version"],
        "package_version": config["package_version"],
        "modules": [name for name in config["module_order"] if name in selected],
        "variables": {
            name: values[name]
            for name in sorted(values)
            if name not in UNLOCK_BINDING_EXCLUDED
        },
    }
    canonical = json.dumps(
        payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def validate_age_gate_configuration(
    config: dict, selected: set[str], values: dict[str, str], unset_values: set[str]
) -> None:
    """Reject internally inconsistent age-gate deployment declarations."""
    if "14_age_appropriate_gate" not in selected:
        return

    mode = values["AGE_GATE_DEPLOYMENT_MODE"]
    assurance = values["AGE_GATE_ASSURANCE_STATE"]
    allowed_assurance = {
        "development": {"development-only"},
        "limited-pilot": {"pilot-approved", "production-validated"},
        "production": {"production-validated"},
    }
    if assurance not in allowed_assurance[mode]:
        raise SystemExit(
            "inconsistent age-gate deployment declaration: "
            f"{mode} cannot use {assurance} assurance"
        )

    if (
        values["AGE_DATA_POLICY"] == "no-collection-screen"
        and values["AGE_GATE_RETENTION_POLICY"] != "none"
    ):
        raise SystemExit(
            "no-collection-screen requires AGE_GATE_RETENTION_POLICY=none"
        )

    if values["AGE_GATE_CONTROL_STATE"] == "verified-unlock-receipt":
        required_receipt_values = [
            "AGE_GATE_UNLOCK_RECEIPT_ID",
            "AGE_GATE_UNLOCK_SCOPE",
            "AGE_GATE_UNLOCK_EXPIRES_AT",
            "AGE_GATE_UNLOCK_CONFIG_SHA256",
        ]
        missing_receipt_values = [
            name for name in required_receipt_values if values[name] in unset_values
        ]
        if missing_receipt_values:
            raise SystemExit(
                "verified unlock receipt requires: "
                + ", ".join(missing_receipt_values)
            )
        if values["AGE_GATE_UNLOCK_CONTROL_PLANE"] != "verified-external":
            raise SystemExit(
                "verified unlock receipt requires "
                "AGE_GATE_UNLOCK_CONTROL_PLANE=verified-external"
            )
        if values["AGE_GATE_UNLOCK_REPLAY_STATE"] != "unconsumed":
            raise SystemExit(
                "verified unlock receipt requires "
                "AGE_GATE_UNLOCK_REPLAY_STATE=unconsumed"
            )
        supplied_binding = values["AGE_GATE_UNLOCK_CONFIG_SHA256"].lower()
        if not re.fullmatch(r"[0-9a-f]{64}", supplied_binding):
            raise SystemExit("AGE_GATE_UNLOCK_CONFIG_SHA256 must be 64 hex digits")
        expected_binding = age_gate_binding_sha256(config, selected, values)
        if supplied_binding != expected_binding:
            raise SystemExit(
                "unlock receipt is bound to a different configuration; expected "
                + expected_binding
            )
        if not re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z",
            values["AGE_GATE_UNLOCK_EXPIRES_AT"],
        ):
            raise SystemExit(
                "AGE_GATE_UNLOCK_EXPIRES_AT must be a UTC RFC 3339 timestamp"
            )

    if mode in {"limited-pilot", "production"}:
        required_controls = {
            "HUMAN_REVIEW_STATE": "available",
            "AGE_GATE_INCIDENT_RESPONSE_STATE": "configured-and-tested",
            "AGE_GATE_ROLLBACK_STATE": "configured-and-tested",
        }
        mismatches = [
            f"{name}={expected}"
            for name, expected in required_controls.items()
            if values[name] != expected
        ]
        if values["APPEAL_PATH"] in unset_values:
            mismatches.append("APPEAL_PATH=<specified path>")
        if mismatches:
            raise SystemExit(
                f"{mode} age-gate deployment requires: " + ", ".join(mismatches)
            )


def assemble(
    config: dict,
    profiles: list[str],
    enables: list[str],
    disables: list[str],
    overrides: dict[str, str],
) -> Assembly:
    selected = select_modules(config, profiles, enables, disables)
    values = dict(config["variables"])
    values.update(overrides)
    validate_allowed_values(config, values)
    validate_age_gate_configuration(
        config, selected, values, set(config["unset_values"])
    )
    missing = missing_required_values(config, selected, values)
    rendered_values = {name: encode_prompt_scalar(value) for name, value in values.items()}

    profile_label = "+".join(profiles)
    ordered_modules = tuple(
        module for module in config["module_order"] if module in selected
    )
    sections = [
        "> **FABRICATION FLAG — GENERATED TEXT BEGINS**",
        "",
        f"# Assembled LLM Hardening Prompt — {profile_label}",
        "",
        (
            f"`[GENERATED-PROMPT]` Package: {config['package_version']} | "
            f"Profiles: {profile_label}"
        ),
        "",
        f"`INSTANCE READY: {'true' if not missing else 'false'}`",
        "",
    ]
    if missing:
        sections.extend(
            [
                "`[GENERATED-WARNING]` This is an inert template until these required "
                "values are resolved: "
                + ", ".join(missing),
                "",
            ]
        )

    for module in ordered_modules:
        path = MODULE_DIR / f"{module}.md"
        if not path.exists():
            raise SystemExit(f"missing module file: {path}")
        rendered = Template(path.read_text(encoding="utf-8")).safe_substitute(
            rendered_values
        )
        sections.extend([rendered.rstrip(), ""])

    unresolved = sorted({name for section in sections for name in _unresolved(section)})
    if unresolved:
        sections.extend(
            [
                "## Unresolved template variables",
                "",
                "`[GENERATED-WARNING]` The following placeholders remain unresolved: "
                + ", ".join(unresolved),
                "",
            ]
        )

    sections.extend(["> **FABRICATION FLAG — GENERATED TEXT ENDS**", ""])
    return Assembly(
        text="\n".join(sections),
        profiles=tuple(profiles),
        modules=ordered_modules,
        unresolved_variables=tuple(unresolved),
        missing_required_values=tuple(missing),
    )


def _unresolved(text: str) -> set[str]:
    return set(re.findall(r"\$\{([A-Z0-9_]+)\}", text))


def resolve_output_path(output: Path, replace_build: bool) -> Path:
    target = output if output.is_absolute() else ROOT / output
    target = target.resolve(strict=False)
    root = ROOT.resolve()
    build_dir = BUILD_DIR.resolve()
    inside_root = target == root or root in target.parents
    inside_builds = target != build_dir and build_dir in target.parents

    if inside_root and (not inside_builds or target.suffix != ".md"):
        raise SystemExit("package outputs are restricted to new .md files under builds/")
    if target.exists():
        if not (replace_build and inside_builds):
            raise SystemExit(f"refusing to overwrite existing output: {target}")
    elif replace_build:
        raise SystemExit("--replace-build requires an existing file under builds/")
    return target


def write_atomic(target: Path, text: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(
        dir=target.parent, prefix=f".{target.name}.", suffix=".tmp"
    )
    temporary = Path(temporary_name)
    try:
        os.fchmod(fd, 0o644)
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    finally:
        if temporary.exists():
            temporary.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Assemble selectable LLM hardening prompt modules"
    )
    parser.add_argument(
        "--profile",
        action="append",
        default=[],
        help="repeat or comma-separate profiles to compose their module union",
    )
    parser.add_argument("--enable", action="append", default=[], help="add a module")
    parser.add_argument(
        "--disable",
        action="append",
        default=[],
        help="fail-closed removal; selected-profile and dependency controls cannot be removed",
    )
    parser.add_argument(
        "--set", dest="assignments", action="append", default=[], metavar="NAME=VALUE"
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--replace-build",
        action="store_true",
        help="atomically replace an existing generated .md file under builds/ only",
    )
    parser.add_argument(
        "--require-ready",
        action="store_true",
        help="refuse assembly while a profile-required value is unresolved",
    )
    parser.add_argument("--list", action="store_true", help="list profiles and modules")
    parser.add_argument(
        "--show-age-gate-binding",
        action="store_true",
        help="print the SHA-256 configuration binding for an external unlock issuer",
    )
    args = parser.parse_args()

    config = load_config()
    profiles = parse_profiles(args.profile, config)
    if args.replace_build and not args.output:
        raise SystemExit("--replace-build requires --output")
    if args.list:
        print("profiles:")
        for name in config["profiles"]:
            print(f"  {name}")
        print("modules:")
        for name in config["module_order"]:
            marker = " (mandatory)" if name in config["mandatory_modules"] else ""
            print(f"  {name}{marker}")
        return

    overrides = parse_assignments(args.assignments, set(config["variables"]))
    if args.show_age_gate_binding:
        selected = select_modules(config, profiles, args.enable, args.disable)
        if "14_age_appropriate_gate" not in selected:
            raise SystemExit("--show-age-gate-binding requires the age_gate module")
        values = dict(config["variables"])
        values.update(overrides)
        validate_allowed_values(config, values)
        print(age_gate_binding_sha256(config, selected, values))
        return
    result = assemble(config, profiles, args.enable, args.disable, overrides)
    if result.unresolved_variables:
        raise SystemExit(
            "unresolved template variables: " + ", ".join(result.unresolved_variables)
        )
    if args.require_ready and result.missing_required_values:
        raise SystemExit(
            "required values remain unresolved: "
            + ", ".join(result.missing_required_values)
        )

    if args.output:
        output = resolve_output_path(args.output, args.replace_build)
        write_atomic(output, result.text)
        print(output)
    else:
        print(result.text, end="")


if __name__ == "__main__":
    main()
