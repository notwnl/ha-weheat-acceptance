#!/usr/bin/env python3
"""Build a standalone Weheat Acceptance custom integration from HA Core."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

DOMAIN_OLD = "weheat"
DOMAIN_NEW = "weheat_acceptance"
NAME_NEW = "Weheat Acceptance"


def run(*args: str) -> None:
    subprocess.run(args, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ref", default="2026.2.3")
    parser.add_argument("--version", default="2026.2.3-acc.1")
    parser.add_argument("--workspace", default=".build/home-assistant-core")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    workspace = repo_root / args.workspace
    source = workspace / "homeassistant/components/weheat"
    target = repo_root / "custom_components/weheat_acceptance"

    if workspace.exists():
        shutil.rmtree(workspace)
    workspace.parent.mkdir(parents=True, exist_ok=True)

    run("git", "clone", "--depth", "1", "--branch", args.ref,
        "https://github.com/home-assistant/core.git", str(workspace))

    if not source.is_dir():
        raise RuntimeError(f"Upstream component not found: {source}")

    if target.exists():
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target)

    # Endpoints: fail below if expected production values were not present.
    changed_auth = 0
    changed_api = 0
    for path in target.rglob("*"):
        if not path.is_file() or path.suffix not in {".py", ".json", ".yaml", ".yml"}:
            continue
        text = path.read_text(encoding="utf-8")
        auth_count = text.count("auth.weheat.nl")
        api_count = text.count("https://api.weheat.nl/third_party")
        text = text.replace("auth.weheat.nl", "auth.acc.weheat.nl")
        text = text.replace(
            "https://api.weheat.nl/third_party",
            "https://api.acc.weheat.nl/third_party",
        )
        changed_auth += auth_count
        changed_api += api_count
        path.write_text(text, encoding="utf-8")

    const_path = target / "const.py"
    const_text = const_path.read_text(encoding="utf-8")
    new_const, count = re.subn(
        r'(?m)^DOMAIN\s*=\s*["\']weheat["\']\s*$',
        'DOMAIN = "weheat_acceptance"',
        const_text,
        count=1,
    )
    if count != 1:
        raise RuntimeError("Expected exactly one DOMAIN assignment in const.py")
    const_path.write_text(new_const, encoding="utf-8")

    manifest_path = target / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("domain") != DOMAIN_OLD:
        raise RuntimeError(f"Unexpected upstream domain: {manifest.get('domain')!r}")
    manifest["domain"] = DOMAIN_NEW
    manifest["name"] = NAME_NEW
    manifest["version"] = args.version
    # Custom repository documentation; preserve requirements and integration metadata.
    manifest["documentation"] = "https://github.com/OWNER/REPOSITORY"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Update visible title only; do not rename the external Python package or model names.
    strings_path = target / "strings.json"
    if strings_path.exists():
        strings = json.loads(strings_path.read_text(encoding="utf-8"))
        strings["title"] = NAME_NEW
        strings_path.write_text(json.dumps(strings, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if changed_auth < 1:
        raise RuntimeError("No production OAuth host was found; inspect upstream changes")
    if changed_api < 1:
        raise RuntimeError("No production /third_party API URL was found; inspect upstream changes")

    # Ensure no production endpoints remain in executable/configuration files.
    leftovers = []
    for path in target.rglob("*"):
        if path.is_file() and path.suffix in {".py", ".json", ".yaml", ".yml"}:
            text = path.read_text(encoding="utf-8")
            if "auth.weheat.nl" in text or "https://api.weheat.nl" in text:
                leftovers.append(str(path.relative_to(repo_root)))
    if leftovers:
        raise RuntimeError(f"Production endpoints remain in: {leftovers}")

    print(f"Built {target.relative_to(repo_root)} from Home Assistant Core {args.ref}")
    print(f"OAuth replacements: {changed_auth}; API replacements: {changed_api}")


if __name__ == "__main__":
    main()
