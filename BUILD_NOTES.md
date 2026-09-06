# Packaging TraditionalAstrologyEngine as a portable desktop app

## Files
- `desktop_launcher.py` — spawns Streamlit headlessly, opens it in a pywebview window.
- `build.spec` — PyInstaller build configuration.
- `app.py` — your existing Streamlit script, bundled as a data file (not imported).

## 1. Test in dev mode first
Before packaging anything:
```
pip install pywebview
python desktop_launcher.py
```
This should open a native window showing your app. Fix any issues here —
they'll be much harder to debug once frozen.

## 2. Why onedir instead of onefile
PyInstaller's `--onefile` mode self-extracts to a temp directory on *every
launch*, adding a real startup delay, and its unsigned self-extracting
`.exe`s are flagged by antivirus heuristics far more often than a plain
folder of files. `build.spec` uses `--onedir` (via `COLLECT`) instead:

- **Windows:** you get a folder (`dist/TraditionalAstrologyEngine/`) containing
  `TraditionalAstrologyEngine.exe` plus its dependencies. Zip the folder — that *is* the
  portable, no-install form. Users unzip and double-click the `.exe`.
- **macOS:** the spec's `BUNDLE` step wraps that same folder into a proper
  `TraditionalAstrologyEngine.app`, which behaves as a single double-clickable icon even
  though it's technically a directory. Zip or `.dmg` it for distribution.

If startup-folder-of-files bothers you aesthetically, `--onefile` still
works fine for personal use — just change `EXE(..., exclude_binaries=True)`
to a single onefile `EXE(...)` per PyInstaller's docs and drop `COLLECT`.

## 3. Platform-specific requirements

### Windows
pywebview uses the **Qt (PySide6/QtWebEngine)** backend, which bundles its
own Chromium build via the `PySide6` pip package — no external runtime
dependency like WebView2, no version detection, nothing to install on the
end user's machine beyond the app itself.

Unsigned `.exe`s trigger a Windows SmartScreen warning ("Windows protected
your PC"). Users can click **More info → Run anyway**. A proper fix requires
a code-signing certificate (~$100+/yr) — not necessary for personal/private
distribution.

### macOS
pywebview uses the built-in WebKit — no extra runtime needed, which is a
genuine advantage for portability here.

Unsigned `.app` bundles trigger Gatekeeper's "unidentified developer"
block. First run: **right-click the app → Open → Open** (this only needs
doing once). For wider distribution without this friction you'd need an
Apple Developer ID ($99/yr) and to notarize the build — out of scope unless
you're distributing beyond yourself/trusted users.

## 4. Gotchas specific to this app's dependencies

- **Windows GUI backend: Qt (PySide6), not WebView2.** Earlier versions of
  this project used pywebview's EdgeChromium backend, which depends on the
  Microsoft Edge WebView2 Runtime being present on the end user's machine
  (usually true on stock Windows 10/11, but not guaranteed — debloated
  installs, locked-down corporate images, or older systems can be missing
  it entirely, and there's no way to know in advance whose machine it'll
  run on). We switched to pywebview's Qt backend instead: `PySide6`
  bundles its own complete Chromium build (QtWebEngine) directly in the
  pip wheel, so there's nothing external to detect, download, or bundle
  separately — `pip install -r requirements.txt` is the whole story.
  `desktop_launcher.py` forces `gui="qt"` on Windows; macOS keeps using
  its native Cocoa/WebKit backend, since that already works well there
  with no equivalent runtime-availability problem.
- **pyswisseph / ephemeris precision:** `app.py` never calls
  `swe.set_ephe_path()`, so it already falls back to the built-in Moshier
  ephemeris (no external `.se1` files needed). This is arc-second-level
  precision, which is far finer than anything the app displays (minutes of
  arc) — no need to bundle Swiss Ephemeris data files unless you have a
  specific reason to want JPL-grade precision.
- **timezonefinder:** ships a sizeable internal dataset (tens of MB) that
  `collect_all("timezonefinder")` in `build.spec` should pull in
  automatically. This is the single biggest contributor to final build
  size. If you want a much smaller build and can tolerate coarser timezone
  boundaries, `TimezoneFinderL` is a lighter drop-in alternative — not
  something I'd swap in without you asking, since it trades accuracy for size.
- **Geocoding is offline.** Place lookup reads the bundled `atlas.db`
  (SQLite, ~24 MB, listed in `build.spec`'s `datas`), so the packaged app
  needs no internet access and no geopy/Nominatim or certifi -- neither is
  a dependency any more, and neither is in `requirements*.txt` or the spec.
  If you ever swap the atlas for a live geocoder, both of those come back:
  a network requirement at runtime, and certifi's CA bundle for frozen
  HTTPS calls.

## 5. Building for both platforms without owning both machines
PyInstaller does not cross-compile — a build run on Linux/Mac cannot
produce a Windows `.exe`, and vice versa. If you don't have physical access
to both a Windows and a Mac machine, the standard solution is a CI matrix,
e.g. GitHub Actions with `runs-on: [windows-latest, macos-latest]`, each
job running `pip install -r requirements.txt pyinstaller
pyinstaller-hooks-contrib` then `pyinstaller build.spec`, uploading
`dist/` as a build artifact.

## 6. Debugging a frozen build that fails silently
Set `console=True` in `build.spec` temporarily — this gives you a terminal
window showing Streamlit's actual startup errors/tracebacks, which are
otherwise invisible with `console=False`. Switch back to `False` for the
release build once it's working.
