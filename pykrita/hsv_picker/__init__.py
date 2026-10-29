import os
import sys
import tempfile
import traceback

__version__ = "1.1.0"

# Nix installs an ABI-matched NumPy runtime beside the plugin. Expose it only
# during import, without changing Krita's launch environment or leaving extra
# packages on sys.path. Source ZIPs can use NumPy already provided by the host.
_DEPENDENCIES = os.path.join(os.path.dirname(__file__), "_python_dependencies")
_ADDED_DEPENDENCIES = os.path.isdir(_DEPENDENCIES) and _DEPENDENCIES not in sys.path
if _ADDED_DEPENDENCIES:
    sys.path.append(_DEPENDENCIES)

try:
    import numpy as _np          # noqa: F401
    import numpy.linalg as _npl  # noqa: F401
except Exception as error:
    try:
        _dbg = os.path.join(tempfile.gettempdir(), "hsv_picker_import_error.log")
        with open(_dbg, "a", encoding="utf-8", newline="\n") as _fh:
            _fh.write("numpy 导入失败（hsv_picker v%s）：\n" % __version__
                      + traceback.format_exc() + "\n")
    except Exception:
        pass
    raise ImportError(
        "Momo Color Picker requires NumPy matching Krita's embedded Python. "
        "On NixOS, use the one-time install-plugin command, then start Krita normally; "
        "see the installation guide."
    ) from error
else:
    # 正常启动不留下仓库内/临时目录里的旧诊断日志
    try:
        _dbg = os.path.join(tempfile.gettempdir(), "hsv_picker_import_error.log")
        if os.path.isfile(_dbg):
            os.remove(_dbg)
    except Exception:
        pass
finally:
    if _ADDED_DEPENDENCIES:
        sys.path.remove(_DEPENDENCIES)

from .hsv_picker import *   # noqa: E402,F401,F403
