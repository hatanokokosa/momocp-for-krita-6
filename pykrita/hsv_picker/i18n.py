"""界面文本的小型双语选择器。

- 语言探测顺序：Krita 设置 language（若有）→ QLocale 默认/系统 uiLanguages → 环境变量 LANG/LC_ALL。
- 本模块只依赖 PyQt6.QtCore（krita 为可选导入），不参与数学层；math_core 不得引用。
"""

import os


def _is_zh():
    candidates = []
    try:
        import krita
    except ImportError:
        krita = None
    if krita is not None:
        app = krita.Krita.instance()
        lang = app.readSetting("", "language", "")
        if lang:
            candidates.append(lang)
    try:
        from PyQt6.QtCore import QLocale
    except ImportError:
        QLocale = None
    if QLocale is not None:
        for loc in (QLocale(), QLocale.system()):
            candidates.extend(loc.uiLanguages() or [])
    candidates.extend((os.environ.get("LANG", ""), os.environ.get("LC_ALL", "")))
    return any(str(x).lower().startswith(("zh", "cn", "tw", "hk")) for x in candidates)


_ZH = _is_zh()


def is_zh():
    """Return the language selected when this module was initialized."""
    return _ZH


def t(zh, en):
    return zh if _ZH else en
