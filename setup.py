from setuptools import setup
import sys
import os
from pathlib import Path

# Find libffi.8.dylib in the current Python environment
libffi_path = None
env_lib_dir = Path(sys.prefix) / "lib"
if (env_lib_dir / "libffi.8.dylib").exists():
    libffi_path = str(env_lib_dir / "libffi.8.dylib")

APP = ["pingbar.py"]
OPTIONS = {
    "argv_emulation": False,
    "plist": {
        "LSUIElement": True,  # hide Dock icon
        "CFBundleName": "PingBar",
        "CFBundleShortVersionString": "1.0.0",
    },
    "packages": ["rumps"],
}

# Add libffi.8.dylib to frameworks if found
if libffi_path:
    OPTIONS["frameworks"] = [libffi_path]
    print(f"Adding libffi from: {libffi_path}")
else:
    print("Warning: libffi.8.dylib not found in Python environment")

setup(
    app=APP,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
