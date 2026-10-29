"""Qt6 interaction/buffer regressions; run with Python + PyQt6 + NumPy."""
import gc
from pathlib import Path
import sys
import unittest

import numpy as np
from PyQt6.QtCore import QEvent, QPointF, Qt
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QApplication

# These modules intentionally support standalone imports without Krita.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pykrita" / "hsv_picker"))
from history_widget import CELL, HistoryWidget
from keymap_dialog import KeymapDialog
from render import qimage_from_rgb, qimage_from_rgba


class Qt6BehaviorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_rgb_image_owns_unaligned_noncontiguous_rows(self):
        source = np.array([
            [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
            [[10, 11, 12], [13, 14, 15], [16, 17, 18]],
        ], dtype=np.uint8)
        # Reversing the columns requires a contiguous copy; 9-byte rows also
        # exercise QImage's explicit bytesPerLine rather than aligned defaults.
        image = qimage_from_rgb(source[:, ::-1])
        source[:] = 0
        del source
        gc.collect()
        actual = [[image.pixelColor(x, y).getRgb()[:3] for x in range(3)] for y in range(2)]
        self.assertEqual(actual, [
            [(7, 8, 9), (4, 5, 6), (1, 2, 3)],
            [(16, 17, 18), (13, 14, 15), (10, 11, 12)],
        ])

    def test_rgba_image_preserves_channels_and_alpha_after_source_mutation(self):
        source = np.array([[[11, 37, 83, 129], [201, 149, 97, 45]]], dtype=np.uint8)
        image = qimage_from_rgba(source)
        source[:] = 255
        self.assertEqual(image.pixelColor(0, 0).getRgb(), (11, 37, 83, 129))
        self.assertEqual(image.pixelColor(1, 0).getRgb(), (201, 149, 97, 45))

    def test_history_fractional_coordinates_select_correct_row(self):
        selected = []
        widget = HistoryWidget(on_pick=selected.append)
        self.addCleanup(widget.close)
        widget.resize(16, 3 * CELL)
        widget.set_colors(["#112233", "#445566"])
        for y, button in ((CELL - 0.25, Qt.MouseButton.LeftButton),
                          (CELL, Qt.MouseButton.LeftButton),
                          (2 * CELL, Qt.MouseButton.LeftButton),
                          (0.5, Qt.MouseButton.RightButton)):
            point = QPointF(5.5, y)
            event = QMouseEvent(QEvent.Type.MouseButtonPress, point, point,
                                button, button, Qt.KeyboardModifier.NoModifier)
            QApplication.sendEvent(widget, event)
        self.assertEqual(selected, ["#112233", "#445566"])

    def test_keymap_topmost_transition_preserves_other_window_flags(self):
        dialog = KeymapDialog()
        self.addCleanup(dialog.close)
        initial = dialog.windowFlags()
        top = Qt.WindowType.WindowStaysOnTopHint
        dialog.show()
        dialog.apply_effective_top(True)
        self.assertTrue(dialog.windowFlags() & top)
        self.assertEqual(dialog.windowFlags() & ~top, initial & ~top)
        self.assertTrue(dialog.isVisible())
        dialog.apply_effective_top(False)
        self.assertFalse(dialog.windowFlags() & top)
        self.assertEqual(dialog.windowFlags() & ~top, initial & ~top)
        self.assertTrue(dialog.isVisible())


if __name__ == "__main__":
    unittest.main()
