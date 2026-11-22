import os
import sys

# Ensure Chromium sandbox does not crash headless, in Docker, or on Windows
flags = os.environ.get("QTWEBENGINE_CHROMIUM_FLAGS", "")
for f in ["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]:
    if f not in flags:
        flags = f"{flags} {f}".strip()
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = flags

# Ensure GUI attaches to interactive user desktop on Windows
if sys.platform == "win32":
    try:
        import ctypes
        user32 = ctypes.windll.user32
        GENERIC_ALL = 0x10000000
        hwinsta = user32.OpenWindowStationW("WinSta0", False, GENERIC_ALL)
        if hwinsta:
            user32.SetProcessWindowStation(hwinsta)
        hdesk = user32.OpenDesktopW("Default", 0, False, GENERIC_ALL)
        if hdesk:
            user32.SetThreadDesktop(hdesk)
    except Exception:
        pass

# Ensure qt_version directory is on sys.path
qt_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qt_version")
if qt_dir not in sys.path:
    sys.path.insert(0, qt_dir)

if __name__ == "__main__":
    from app import main
    sys.exit(main())
