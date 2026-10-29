# Momo Color Picker 1.1.0

Momo Color Picker is an Oklab/Oklch-aware color picker plugin for Krita. It keeps the familiar HSV-style hue ring and S/V square, while lightness and chroma are locked and read in Oklab (or in Krita's grayscale soft-proof value).

![Overview](https://raw.githubusercontent.com/zmom0/momo-color-picker/windows-release/pykrita/hsv_picker/manual/images/demo-first.gif)

## Changes in 1.1.0

- **Absolute chroma, fully wired**: with the C strip on absolute C, the blue guide line, the cluster lines and the middle-button lock all follow the same scale; the absolute-C isoline now meets the current point exactly on the S=1 gamut edge (previously off by up to 0.136).
- **Numeric row that fits any width**: H/S/V and HEX are measured from the real font, always show complete values (`359.99`, `#RRGGBB`), switch to left-aligned display when the panel is narrow instead of truncating, and the current-color swatch takes the remaining width.
- **Simpler default keymap + a global temporary switch key**: the default ring is 4 rows (left/middle/right lock the current chroma mode, Ctrl+left is plain HSV) and the square is 3 rows; the switch key (default Shift; none / Shift / Ctrl / Alt and their combinations) temporarily flips the chroma mode. Old default keymaps migrate as a whole, customized keymaps are never overwritten.
- **Hover preview and drag-time switching**: hold the switch key with the cursor over the panel and the C strip, the numeric field, the guide lines and the clusters immediately show the other chroma mode; the mode chosen when you press is kept for the whole drag, so the L strip holds absolute C instead of C_rel and the C strip reads and applies values on the same scale. Release restores the persistent mode.
- **Absolute-C cluster density**: fixed 18 steps (`0.02 … 0.36`, default) or 9 steps evenly spaced over the pure-color C_max of the current hue.
- **Popup closes together with Krita**: the popup no longer blocks Krita's exit (it could leave `krita.exe` running) and is now closed on window close, on `applicationClosing` and on `aboutToQuit`.
- **Docs**: README and the bilingual manual updated for the new keymap, the C strip options and the absolute-chroma behavior.

## Changes in 1.0.0

- First public release: color engine with Oklab L / Oklab C, switchable Grayscale lightness standard, relative/absolute chroma modes and reachability hints.
- Complete picking UI: ring + S/V square, L/C/a/b strips, editable numeric fields, current-color HEX swatch and history.
- Panel, popup and preview overlay with persistent settings and Docker/popup synchronization.
- Editable keymap supporting all modifier + mouse-button combinations.
- Simplified Chinese / English manual and reproducible image assets.
- Release packaging: one Windows zip with bundled numpy 2.3.0, portable `install.bat`, GPL-3.0 license text and a tag-triggered GitHub Actions release workflow.

## Krita 6 / Qt6 Nix port

The supported deployment for this Qt6 port is Linux through the repository's Nix flake:

- Qt6-only Python bindings, scoped enums, floating-point mouse positions, native key combinations and dialog execution; Krita plugin/action/settings IDs are preserved.
- Native Wayland uses a resizable subwindow and passive preview inside Krita. The size grip has its own footer rather than intercepting numeric-field input; host resizing preserves the remembered user size. X11/XWayland uses a parented tool window.
- Numeric-field measurements include the active Qt style's inner frame margins, avoiding clipped values under KDE Breeze.
- Shortcut matching reads the current Krita action, including shortcut changes made during the session, without stealing text input.
- Removed the obsolete Windows NumPy vendor tree. Linux diagnostic logs use `XDG_STATE_HOME` (default `~/.local/state`), with `HSV_PICKER_DEBUG_LOG` still available as an override.
- Source archives and Nix plugin packages include the GPL license; source releases no longer bundle platform-specific NumPy binaries.

1. Run `nix run .#install-plugin` once (use `path:.#install-plugin` for an untracked checkout). It installs user data links and registers a persistent Nix GC root; it does not start Krita.
2. Start your existing Krita from the application menu or with `krita`. Enable the plugin in Python Plugin Manager and restart. `nix develop` provides the development/test environment.
3. The source release asset is `MomoColorPicker-1.1.0-krita6-source.zip`. It contains no native NumPy extension and is platform-neutral plugin source.

The plugin package associates a private ABI-matched NumPy runtime with the plugin directory, imports NumPy with a temporary search path, then removes that path. No custom Krita launcher, `PYTHONPATH` or `XDG_DATA_DIRS` changes are needed. Installation refuses foreign files, preflights conflicts before mutation, and supports idempotent upgrades through a stable registered GC root; uninstall preserves unrelated files and settings. Ordinary Krita must use a compatible Python ABI. Native Wayland popup behavior remains host-local, not desktop-global always-on-top.

Verification: the Nix-built plugin passed actual Krita 6.0.4.1 GUI probes on NixOS x86_64, both native Wayland and XWayland (`xcb`), using Python 3.14.8 and NumPy 2.5.3. Four standalone Qt6 regressions passed for RGB/RGBA buffer ownership, fractional history-cell hit testing and dialog flag transitions. Source archive layout, action/desktop descriptors, GPL license and absence of native vendor binaries were checked. Physical multi-monitor operation, aarch64 and Windows were not runtime-tested.

Launcher-free deployment verification used the ordinary system Krita executable with isolated user data and no custom Python/data search environment. Private NumPy and linalg remained functional after removing the temporary import path; foreground input, popup/preview, shortcuts and shutdown passed. Installer upgrades, idempotency, registered GC roots and settings-preserving uninstall were exercised. The regression suite now has six passing cases, including refusal to partially install on conflicts and preservation of user replacements on uninstall.

## Historical Windows package status

The 1.1.0 Windows/Krita 5.3 package and its bundled NumPy 2.3.0 are historical release artifacts. The current Qt6 source archive does not include that Windows-only native binary. `install.bat` is retained as a source-file copier, but Krita 6 on Windows and NumPy discovery there are unverified; no Windows compatibility claim is made.

## Highlights

- **HSV-style picking, Oklab precision** — hue ring (0° red at 9 o'clock, clockwise) plus S/V square; lightness can be locked as Oklab L (default) or as the Grayscale (soft proof) value.
- **Chroma in Oklab C** — relative chroma C_rel (default, always reachable) or absolute chroma C; unreachable hues at the locked (L, C) are marked with hatching, and absolute-C drags clamp to the nearest reachable hue.
- **L / C strips and optional Oklab a / b strips** — every value can also be typed into its numeric field; strips and ring stay in sync.
- **Temporary chroma-mode switch key** — hold it to preview and drag in the other chroma mode (absolute C vs C_rel), then release to return.
- **Popup panel on `Shift+B`** — auto-close outside, always-on-top and follow-mouse options; the same picker is also available as a docker.
- **Preview overlay** — current color plus the last two colors, with off / 1s / 2s / hover / always modes.
- **Color history and HEX swatch** — click a history entry to reuse it; click the current color swatch to copy its HEX code.
- **Fully customizable keymap** — 8 modifier combinations × left/middle/right button per area (ring, square, strips, numeric fields), editable in a table and persisted immediately.
- **Bilingual manual** — Simplified Chinese and English manual generated from one source, opened from the plugin's Manual button.

## Historical 1.1.0 Windows installation

The original 1.1.0 Windows release was installed as follows:

1. Download `MomoColorPicker-1.1.0-win64-krita5.3.zip` from the historical Release assets.
2. In Krita, open **Tools → Scripts → Import Python Plugin From File...** and select the zip.
3. When Krita offers to restart, choose **Yes**; then restart Krita.
4. In **Settings → Configure Krita → Python Plugin Manager**, enable **Momo Color Picker** and restart it once more.
5. Open it from **Settings → Dockers → Momo Color Picker**, or press `Shift+B`.

This historical package bundled NumPy 2.3.0 for its tested Krita 5.3 / Python 3.13 environment. That binary is not reused by the Krita 6 port.

## License and third-party components

- **Momo Color Picker:** GPL-3.0-or-later.
- **Historical bundled NumPy 2.3.0:** BSD-3-Clause; its license text remains in the historical package's `pykrita/hsv_picker/vendor/numpy-2.3.0.dist-info/LICENSE.txt`.
- **Nix deployment NumPy:** supplied by pinned nixpkgs; consult the Nix store license metadata. The current source archive contains no NumPy binary.

## 中文说明

馍馍拾色器 1.1.0：这是一个 Oklab/Oklch 拾色器，保留 HSV 色相环 + S/V 方块的顺手操作，同时用 Oklab L 精确锁定明度（可切换到 Krita 灰阶校样口径），彩度使用 Oklab C（默认相对彩度 C_rel，任何色相都可达）。支持 L/C/a/b 色条与数值框、弹出面板、预览浮层、历史颜色、可视化按键表和中英双语说明书。

1.1.0 更新要点：绝对彩度口径全面联动（蓝线、线簇、中键锁定，S=1 边界过点线精确过点）；数值行按字体实测自适应、文本始终完整、窄时左对齐；默认键表精简为色环 4 行 / 方块 3 行；新增全局「临时切换键」（默认 Shift，可改 Alt / Shift+Alt 等），按住即可悬停预览并在拖动全程使用另一彩度口径；绝对 C 线簇支持固定 18 档（默认）/ 按色相等分 9 档；关闭 Krita 时弹出面板跟着关闭（不再残留 `krita.exe`）。

### Krita 6 / Qt6 Nix 部署

当前 Qt6 端支持 Linux + Nix：只需执行一次 `nix run .#install-plugin` 安装（未跟踪工作树用 `path:.#install-plugin`），以后从应用菜单或 `krita` 正常启动。插件目录关联 ABI 匹配的私有 NumPy，导入后移除临时搜索路径；不再提供 Krita 专用启动器，不修改启动环境或用户设置。安装器拒绝覆盖外来文件，并注册持久 Nix GC root 防止依赖被回收。源码 ZIP 仍不包含 NumPy，要求宿主已有匹配依赖。

移植内容：Qt6 原生 API 与按键组合；Wayland 宿主内可缩放浮窗和鼠标穿透预览；KDE Breeze 输入框内容区测量，避免数值首位被裁；运行时快捷键更新；保留原有插件 ID、动作 ID 和设置键。旧 Windows NumPy vendor 已移除，Linux 诊断日志遵循 `XDG_STATE_HOME`（默认 `~/.local/state`）。

旧 Windows 包 `MomoColorPicker-1.1.0-win64-krita5.3.zip` 与其中的 NumPy 2.3.0 属于历史发布物。当前 `install.bat` 只复制源文件，Krita 6 Windows 与 NumPy 发现尚未验证，不作兼容性承诺。
