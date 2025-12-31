import os
import subprocess
import sys

# ชื่อโปรแกรม
APP_NAME = "PDFTimeSealer"
ICON_FILE = "app_icon.ico"

def main():
    print(f"--- Building {APP_NAME} ---")

    # 1. Check for Icon
    if not os.path.exists(ICON_FILE):
        print(f"❌ Error: '{ICON_FILE}' not found!")
        print("Please place your custom .ico file in this folder and try again.")
        return

    print(f"✅ Icon found: {ICON_FILE}")
    print("🚀 Starting PyInstaller...")

    # 2. Build Command
    # --add-data "app_icon.ico;." คือการฝังไฟล์ icon ลงไปใน exe เพื่อให้ main.py เรียกใช้ได้
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        f"--name={APP_NAME}",
        f"--icon={ICON_FILE}",
        f"--add-data={ICON_FILE};.", 
        "--collect-all=tkinterdnd2",
        "--clean",
        "main.py"
    ]
    
    # หมายเหตุ: Linux/Mac ใช้ตัวคั่น ':' แทน ';' ใน --add-data
    if sys.platform != "win32":
        cmd[7] = f"--add-data={ICON_FILE}:."

    try:
        subprocess.check_call(cmd)
        print("\n" + "="*30)
        print("🎉 BUILD SUCCESSFUL!")
        print(f"Executable is located at: dist/{APP_NAME}.exe")
        print("="*30)
    except subprocess.CalledProcessError as e:
        print(f"❌ Build Failed: {e}")

if __name__ == "__main__":
    main()