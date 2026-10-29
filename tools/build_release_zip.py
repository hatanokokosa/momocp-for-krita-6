"""Build the Linux/Krita6 Momo Color Picker source archive.

Usage::

    python tools/build_release_zip.py [--version 2.0.0] [--out dist]

The archive contains the Qt6/Krita6 plugin source, desktop descriptor, action
file, manual, and installation notes. It contains no native NumPy runtime:
Linux users can install the Nix plugin package once, or provide matching NumPy
in Krita's Python environment, without changing how Krita is launched.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG_REL = Path("pykrita") / "hsv_picker"
DESKTOP_REL = Path("pykrita") / "hsv_picker.desktop"
INSTALL_FILES = ("install.txt", "LICENSE")
SKIP_DIRS = {"__pycache__", "vendor", "_python_dependencies"}
SKIP_SUFFIX = (".pyc", ".pyo")


def read_version() -> str:
    text = (ROOT / PKG_REL / "__init__.py").read_text(encoding="utf-8")
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', text, re.MULTILINE)
    if not match:
        raise SystemExit("找不到插件 __version__")
    return match.group(1)


def copy_plugin(src: Path, dst: Path) -> int:
    """Copy plugin source without native vendor binaries or Python caches."""
    count = 0
    for dirpath, dirnames, filenames in os.walk(src):
        rel = os.path.relpath(dirpath, src)
        parts = [] if rel == "." else rel.replace(os.sep, "/").split("/")
        if parts and parts[0] in SKIP_DIRS:
            dirnames[:] = []
            continue
        dirnames[:] = [name for name in dirnames if name not in SKIP_DIRS]
        out_dir = dst if not parts else dst.joinpath(*parts)
        out_dir.mkdir(parents=True, exist_ok=True)
        for name in sorted(filenames):
            if name.endswith(SKIP_SUFFIX):
                continue
            shutil.copy2(Path(dirpath) / name, out_dir / name)
            count += 1
    return count


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="构建 Krita 6 平台无关源代码 zip")
    parser.add_argument("--version", default=None, help="默认读取插件 __version__")
    parser.add_argument(
        "--out", default=str(ROOT / "dist"), help="输出目录（默认 dist/）"
    )
    args = parser.parse_args(argv)

    version = args.version or read_version()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="momo_release_"))
    try:
        plugin_dir = stage / "hsv_picker"
        plugin_count = copy_plugin(ROOT / PKG_REL, plugin_dir)
        for name in INSTALL_FILES:
            shutil.copy2(ROOT / name, stage / name)
        shutil.copy2(ROOT / DESKTOP_REL, stage / "hsv_picker.desktop")

        zip_path = out_dir / (f"MomoColorPicker-{version}-krita6-source.zip")
        dirs = sorted(path for path in stage.rglob("*") if path.is_dir())
        files = sorted(path for path in stage.rglob("*") if path.is_file())
        with zipfile.ZipFile(
            zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9
        ) as archive:
            # Krita's importer uses the top-level directory entry to locate the
            # plugin module, so retain explicit directory entries.
            for path in dirs:
                name = str(path.relative_to(stage)).replace(os.sep, "/") + "/"
                archive.write(path, name)
            for path in files:
                name = str(path.relative_to(stage)).replace(os.sep, "/")
                archive.write(path, name)

        with zipfile.ZipFile(zip_path) as archive:
            all_infos = archive.infolist()
            infos = [info for info in all_infos if not info.is_dir()]
            dir_infos = [info for info in all_infos if info.is_dir()]
            top = {}
            for info in infos:
                root = info.filename.split("/", 1)[0]
                top.setdefault(root, [0, 0])
                top[root][0] += 1
                top[root][1] += info.file_size

        forbidden = [
            info.filename
            for info in infos
            if "__pycache__" in info.filename
            or info.filename.endswith(SKIP_SUFFIX)
            or info.filename.startswith("hsv_picker/vendor/")
            or info.filename.startswith("hsv_picker/_python_dependencies/")
        ]
        print(f"插件源码文件数 : {plugin_count:d}")
        print(f"zip 路径        : {zip_path}")
        print(f"zip 大小        : {zip_path.stat().st_size:d} 字节")
        print(
            f"zip 条目数      : {len(all_infos):d}（文件 {len(infos):d} + 目录 {len(dir_infos):d}）"
        )
        print(
            "顶层结构        : "
            + ", ".join(f"{key}({value[0]:d})" for key, value in sorted(top.items()))
        )
        if forbidden:
            print(f"!! 不应出现的条目：{forbidden[:5]!r}")
            return 1
        expected = {
            "hsv_picker",
            "hsv_picker.desktop",
            "install.txt",
            "LICENSE",
        }
        if set(top) != expected:
            print(f"!! 顶层结构不符合预期：{sorted(top)}")
            return 1
    finally:
        shutil.rmtree(stage, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
