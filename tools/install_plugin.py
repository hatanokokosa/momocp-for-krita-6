#!/usr/bin/env python3
"""Install the Momo Color Picker into a user's existing Krita data directory."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

PLUGIN_NAME = "hsv_picker"
OWNER = "momo-color-picker"


def xdg_path(name: str, fallback: str) -> Path:
    value = os.environ.get(name)
    if value:
        candidate = Path(value).expanduser()
        if candidate.is_absolute():
            return candidate
    return Path.home() / fallback


def paths() -> tuple[Path, Path, Path]:
    data = xdg_path("XDG_DATA_HOME", ".local/share") / "krita"
    state = xdg_path("XDG_STATE_HOME", ".local/state") / OWNER
    return data / "pykrita", data / "actions", state / "gcroots"


def link_target(path: Path) -> Path | None:
    if not path.is_symlink():
        return None
    return Path(os.path.abspath(path.parent / os.readlink(path)))


def refuse(path: Path, target: Path) -> None:
    if path.is_symlink() and link_target(path) == target:
        return
    if path.exists() or path.is_symlink():
        raise RuntimeError(
            f"refusing to replace existing {path}; back it up and move it aside first"
        )


def destinations(root: Path) -> list[tuple[Path, Path]]:
    pykrita, actions, _ = paths()
    data = root / "share" / "krita"
    return [
        (pykrita / PLUGIN_NAME, data / "pykrita" / PLUGIN_NAME),
        (
            pykrita / f"{PLUGIN_NAME}.desktop",
            data / "pykrita" / f"{PLUGIN_NAME}.desktop",
        ),
        (actions / f"{PLUGIN_NAME}.action", data / "actions" / f"{PLUGIN_NAME}.action"),
    ]


def check_root(root: Path, store: Path | None = None) -> None:
    if not root.exists() and not root.is_symlink():
        return
    target = link_target(root)
    if (
        target is None
        or not target.name.partition("-")[2].startswith("momo-color-picker-plugin-")
        or (store is not None and target.parent != store)
    ):
        raise RuntimeError(f"refusing to replace unrecognized GC root {root}")


def install(package: Path) -> None:
    data = package / "share" / "krita"
    required = [
        data / "pykrita" / PLUGIN_NAME / "__init__.py",
        data / "pykrita" / f"{PLUGIN_NAME}.desktop",
        data / "actions" / f"{PLUGIN_NAME}.action",
    ]
    if not all(path.is_file() for path in required):
        raise RuntimeError(f"not a complete Momo Color Picker package: {package}")
    if not (data / "pykrita" / PLUGIN_NAME / "_python_dependencies").is_dir():
        raise RuntimeError(f"package has no private NumPy runtime: {package}")
    _, _, roots = paths()
    root = roots / PLUGIN_NAME
    check_root(root, package.parent)
    links = destinations(root)
    # Preflight every destination before creating or updating anything.
    for path, target in links:
        refuse(path, target)
    roots.mkdir(parents=True, exist_ok=True)
    # An ordinary symlink is NOT a GC root. Register the indirect root with
    # Nix; updating this one stable link also atomically updates all data links.
    subprocess.run(
        ["nix-store", "--add-root", str(root), "--indirect", "--realise", str(package)],
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    for path, target in links:
        if not path.is_symlink():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.symlink_to(target)
    print(f"Installed {PLUGIN_NAME} for ordinary Krita under {paths()[0].parent}")
    print(f"Registered persistent Nix GC root: {root}")
    print(
        "Start Krita normally; enable Momo Color Picker in Python Plugin Manager and restart."
    )


def uninstall() -> None:
    _, _, roots = paths()
    root = roots / PLUGIN_NAME
    check_root(root)
    for path, target in destinations(root):
        if link_target(path) == target:
            path.unlink()
            print(f"Removed {path}")
    if root.is_symlink():
        root.unlink()
        print(f"Removed {root}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Install Momo Color Picker for an existing Krita"
    )
    parser.add_argument(
        "--uninstall", action="store_true", help="remove only installer-owned symlinks"
    )
    parser.add_argument("plugin", nargs="?", default=os.environ.get("MOMO_PLUGIN_PATH"))
    args = parser.parse_args()
    try:
        if args.uninstall:
            uninstall()
        elif args.plugin:
            install(Path(args.plugin).expanduser().resolve())
        else:
            parser.error("plugin package path is required")
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"install-plugin: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
