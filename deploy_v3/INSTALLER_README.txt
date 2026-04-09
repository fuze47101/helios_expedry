================================================================================
FeatherV2 Application Installer (install_v3.py)
================================================================================

OVERVIEW
--------
install_v3.py is a self-contained Python script that deploys all Python and
Kivy source files to a Raspberry Pi running the ExpeDRY FeatherV2 test system.

All source files are embedded as base64-encoded strings within the installer
script, making it easy to transfer as a single file without directory structure.


USAGE
-----

Default installation to /home/allied2/FeatherV2:
    python3 install_v3.py

Install to a custom directory:
    python3 install_v3.py /custom/install/path

The script will:
  1. Create the base directory if it doesn't exist
  2. Create subdirectories: utils/, components/, camera/, assets/
  3. Decode and write all 25 Python and Kivy files
  4. Print progress for each file
  5. Remind you to manually copy PNG assets to assets/


EMBEDDED FILES (25 total)
------------------------
  Python files:
    - main.py (16 KB)
    - camera/ColormapEnum.py, guiController.py, thermalcameraController.py, values.py
    - components/Controls.py, SaveDialog.py, Test_Settings.py, WarningDialog.py, WeighDialog.py, WifiDialog.py
    - utils/Relay.py, RS485.py, Scale.py, theme.py
    - All __init__.py files

  Kivy UI files:
    - tester.kv (17 KB)
    - components/*.kv (Controls, SaveDialog, Test_Settings, WarningDialog, WeighDialog, WifiDialog)


MANUAL STEPS AFTER INSTALLATION
--------------------------------
1. Copy PNG assets to assets/ directory:
   - ExpeDRY_logo.png
   - save-24.png

   These files are NOT embedded and must be copied manually.

2. Ensure all required Python dependencies are installed:
   pip3 install kivy cv2 numpy neukivy


EXAMPLE OUTPUT
--------------
$ python3 install_v3.py /home/allied2/FeatherV2

======================================================================
FeatherV2 Application Installer (v3)
======================================================================

[*] Installing to /home/allied2/FeatherV2
  [ 1/25] camera/ColormapEnum.py                             OK
  [ 2/25] camera/__init__.py                                 OK
  ...
  [25/25] utils/theme.py                                     OK

[+] Successfully wrote 25/25 files

[!] Assets (PNG files) — Manual copy required:
    Copy ExpeDRY_logo.png and save-24.png to:
    /home/allied2/FeatherV2/assets/

[+] Installation complete!


FILE MANIFEST
-------------
camera/
  ColormapEnum.py
  __init__.py
  guiController.py
  thermalcameraController.py
  values.py

components/
  Controls.kv
  Controls.py
  SaveDialog.kv
  SaveDialog.py
  Test_Settings.kv
  Test_Settings.py
  WarningDialog.kv
  WarningDialog.py
  WeighDialog.kv
  WeighDialog.py
  WifiDialog.kv
  WifiDialog.py
  __init__.py

utils/
  RS485.py
  Relay.py
  Scale.py
  __init__.py
  theme.py

root:
  main.py
  tester.kv


TROUBLESHOOTING
---------------
Q: ImportError when running main.py?
A: Ensure all Python dependencies are installed via pip3

Q: Missing PNG files warning?
A: Copy ExpeDRY_logo.png and save-24.png to the assets/ directory

Q: "Permission denied" when writing files?
A: Ensure you have write permissions in the target directory or use sudo


NOTES
-----
- The installer script is idempotent (safe to run multiple times)
- Existing files will be overwritten silently
- Asset files are excluded to allow for custom branding/updates
- The installer requires Python 3.x

