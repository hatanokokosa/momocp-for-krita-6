"""Filesystem safety regressions for the one-time plugin installer."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "install_plugin.py"
spec = importlib.util.spec_from_file_location("install_plugin", SCRIPT)
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallationSafetyTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="momo-install-test-")
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        environment = patch.dict(os.environ, {
            "HOME": str(self.directory / "home"),
            "XDG_DATA_HOME": str(self.directory / "data"),
            "XDG_STATE_HOME": str(self.directory / "state"),
            "PYTHONDONTWRITEBYTECODE": "1",
        })
        environment.start()
        self.addCleanup(environment.stop)
        self.package = self.directory / ("a" * 32 + "-momo-color-picker-plugin-test")
        data = self.package / "share" / "krita"
        module = data / "pykrita" / "hsv_picker"
        module.mkdir(parents=True)
        (module / "__init__.py").write_text("# package fixture\n")
        (module / "_python_dependencies").mkdir()
        (data / "pykrita" / "hsv_picker.desktop").write_text("[Desktop Entry]\n")
        (data / "actions").mkdir()
        (data / "actions" / "hsv_picker.action").write_text("<ActionCollection/>\n")

    def test_late_destination_conflict_does_not_partially_install(self):
        pykrita, actions, roots = installer.paths()
        actions.mkdir(parents=True)
        existing = actions / "hsv_picker.action"
        original = b"user-owned action file\n"
        existing.write_bytes(original)
        with self.assertRaises(RuntimeError):
            installer.install(self.package)
        self.assertEqual(existing.read_bytes(), original)
        self.assertFalse(pykrita.exists(), "Conflict must be detected before writing plugin links")
        self.assertFalse(roots.exists(), "Conflict must be detected before registering a GC root")

    def test_uninstall_preserves_user_replacements_even_inside_package(self):
        pykrita, actions, roots = installer.paths()
        root = roots / "hsv_picker"
        roots.mkdir(parents=True)
        root.symlink_to(self.package)
        links = installer.destinations(root)
        for path, target in links:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.symlink_to(target)
        desktop = pykrita / "hsv_picker.desktop"
        desktop.unlink()
        desktop.write_text("user replacement\n")
        foreign = self.package / "LICENSE"
        foreign.write_text("user-selected artifact\n")
        action = actions / "hsv_picker.action"
        action.unlink()
        action.symlink_to(foreign)
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--uninstall"],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((pykrita / "hsv_picker").is_symlink())
        self.assertFalse(root.is_symlink())
        self.assertEqual(desktop.read_text(), "user replacement\n")
        self.assertTrue(action.is_symlink())
        self.assertEqual(action.read_text(), "user-selected artifact\n")


if __name__ == "__main__":
    unittest.main()
