# build.spec
#
# Build with:  pyinstaller build.spec
#
# Run this SEPARATELY on Windows (produces TraditionalAstrologyEngine.exe in dist/) and
# on macOS (produces TraditionalAstrologyEngine.app in dist/) -- PyInstaller bundles the
# native interpreter and platform libraries, so it cannot cross-compile.
#
# Before running: pip install pyinstaller pyinstaller-hooks-contrib
# (pyinstaller-hooks-contrib includes maintained hooks for Streamlit and
# several of its dependencies; without it you will likely need to add more
# --hidden-import / --collect-all entries by trial and error.)

import sys
from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None

datas = []
binaries = []
hiddenimports = []

# These packages ship data files, C extensions, or dynamic imports that
# static analysis alone won't find -- pull in everything for each.
# NOTE: "webview" (pywebview's actual import name -- not the "pywebview"
# distribution name) was MISSING from this list entirely in earlier
# versions of this spec. pywebview's platform backends (edgechromium.py,
# winforms.py, mshtml.py, cocoa.py, etc.) are imported dynamically inside
# functions in guilib.py, which PyInstaller's static analysis can't see --
# so without explicitly collecting them, some backends silently never
# make it into the bundle at all. That's what caused pywebview to keep
# falling through to the broken legacy WinForms/IE renderer even after
# explicitly forcing gui="edgechromium" in desktop_launcher.py: the
# edgechromium backend module itself wasn't present to import.
# NOTE: pyswisseph's PyPI distribution name and its actual import name
# ("swisseph") differ -- listing "pyswisseph" here silently collects
# nothing, since collect_all() operates on the importable module name, not
# the PyPI package name. This went unnoticed for a while because every
# earlier build crashed (on pywebview issues) before app.py ever got far
# enough to actually execute `import swisseph`.
collect_pkgs = ["streamlit", "altair", "pandas", "swisseph", "timezonefinder", "pytz", "webview"]
if sys.platform == "win32":
    # pywebview's Qt backend on Windows needs PySide6 (which bundles its own
    # complete Chromium build via QtWebEngine -- no external runtime to
    # install or bundle separately) and qtpy, the Qt-binding-agnostic shim
    # pywebview's own qt.py imports through. PyInstaller has mature,
    # well-tested hooks for PySide6/QtWebEngine via pyinstaller-hooks-contrib
    # (this is an extremely common combination to bundle), unlike the
    # WebView2/pythonnet/.NET interop path this replaced.
    collect_pkgs += ["PySide6", "qtpy"]

for pkg in collect_pkgs:
    d, b, h = collect_all(pkg)
    datas += d
    binaries += b
    hiddenimports += h

# Belt-and-suspenders on top of collect_all("webview") above: explicitly
# force in every submodule of webview by name, matching the exact fix
# used by other pywebview+PyInstaller projects that hit this same issue.
hiddenimports += collect_submodules("webview")

# Belt-and-suspenders for swisseph too: it's a single compiled C-extension
# file with no submodule structure, so this just directly confirms
# PyInstaller's binary-dependency resolution picks it up.
hiddenimports += ["swisseph"]

# app.py is loaded at runtime via _resource_path("app.py") in the launcher,
# not imported as a module -- bundle it as a plain data file alongside the
# executable rather than analyzing it as code. atlas.db is the offline
# GeoNames lookup database queried in place of a network geocoding API.
# app_icon.ico is loaded at runtime via _resource_path("app_icon.ico") for
# the pywebview window icon, and doubles as the .exe icon below.
datas += [("app.py", "."), ("atlas.db", "."), ("app_icon.ico", ".")]

a = Analysis(
    ["desktop_launcher.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # collect_submodules("webview") above force-imports every webview.platforms.*
    # submodule so pywebview's Qt backend -- itself only ever loaded dynamically
    # by guilib.py -- gets discovered. That net also catches winforms.py,
    # mshtml.py, and edgechromium.py: pywebview's legacy Windows backends,
    # superseded by the Qt/PySide6 backend desktop_launcher.py forces on
    # win32 (the WinForms fallback is explicitly disabled there too). All
    # three `import clr` at module scope, so pulling them in also drags in
    # pythonnet -- and its bundled .NET interop DLLs -- purely because that
    # import statement exists, never because anything here actually runs it.
    excludes=["webview.platforms.winforms", "webview.platforms.mshtml", "webview.platforms.edgechromium", "pythonnet", "clr", "clr_loader"],
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Declares Per-Monitor-V2 DPI awareness in the .exe's embedded manifest,
# which Windows reads at process-creation time -- before a single line of
# Python runs. That sidesteps the reliability problem with the runtime
# alternative (ctypes.windll.shcore.SetProcessDpiAwareness() in
# desktop_launcher.py, kept as a defensive fallback): that call only takes
# effect if it runs before the *first* GDI/window-related Win32 call
# anywhere in the process, and nothing guarantees Python/PyInstaller's own
# startup hasn't already made one. Without either, Windows DPI-virtualizes
# an unaware process -- bitmap-scaling its window to compensate for display
# scaling while it still thinks it drew at the requested size/position --
# which is what made the window open oversized and shifted off-screen.
# Includes the common-controls dependency PyInstaller's own default
# manifest normally carries, so native controls keep the modern Windows
# theme instead of falling back to unthemed Windows Classic controls.
WINDOWS_MANIFEST = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel level="asInvoker" uiAccess="false"/>
      </requestedPrivileges>
    </security>
  </trustInfo>
  <dependency>
    <dependentAssembly>
      <assemblyIdentity type="win32" name="Microsoft.Windows.Common-Controls" version="6.0.0.0" processorArchitecture="*" publicKeyToken="6595b64144ccf1df" language="*"/>
    </dependentAssembly>
  </dependency>
  <application xmlns="urn:schemas-microsoft-com:asm.v3">
    <windowsSettings>
      <dpiAwareness xmlns="http://schemas.microsoft.com/SMI/2016/WindowsSettings">PerMonitorV2</dpiAwareness>
      <dpiAware xmlns="http://schemas.microsoft.com/SMI/2005/WindowsSettings">true/PM</dpiAware>
    </windowsSettings>
  </application>
</assembly>
""" if sys.platform == "win32" else None

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="TraditionalAstrologyEngine",
    debug=False,
    strip=False,
    upx=False,      # UPX compression trips some antivirus heuristics; leave off
    console=False,  # set True temporarily if you need to see startup errors
    icon="app_icon.ico",  # Windows .exe icon (Explorer, taskbar, alt-tab)
    manifest=WINDOWS_MANIFEST,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name="TraditionalAstrologyEngine",
)

# On macOS, wrap the onedir output into a proper double-clickable .app bundle.
if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="TraditionalAstrologyEngine.app",
        icon="app_icon.icns",
        bundle_identifier="org.almuten.traditionalastrologyengine",
    )
