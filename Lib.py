import os.path
import shutil
import subprocess
import ctypes
import sys
import time

import psutil
import pyperclip
import win32gui
import win32process
import keyboard

from Python_Lib.My_Lib_Stock import *
from Python_Lib.My_Lib_File import filename_parent, filename_stem

def open_file_with_Chem3D(file_path):
    def find_window_by_process_name(process_name):
        hwnd_list = []

        def enum_windows_proc(_hwnd, _lparam):
            if win32gui.IsWindowVisible(_hwnd) and win32gui.IsWindowEnabled(_hwnd):
                _, pid = win32process.GetWindowThreadProcessId(_hwnd)
                try:
                    proc = psutil.Process(pid)
                    if proc.name().lower() == process_name.lower():
                        hwnd_list.append(_hwnd)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass

        win32gui.EnumWindows(enum_windows_proc, None)
        if hwnd_list:
            return hwnd_list[0]  # Return the first matching window handle
        else:
            return None

    def is_process_running(process_name):
        # Iterate over all running process
        for proc in psutil.process_iter():
            try:
                # Check if process name contains the given name string.
                if process_name.lower() in proc.name().lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False

    if not is_process_running("chem3d.exe"):
        print("Chem3D is not running. Starting Chem3D...")
        subprocess.Popen(chem3D_path)
        # Wait for Chem3D to start
        time.sleep(10)

    hwnd = find_window_by_process_name("chem3d.exe")
    if hwnd:
        print("Chem3D window found. Bringing it to the foreground.")
        try:
            win32gui.SetForegroundWindow(hwnd)
            ctypes.windll.user32.SetForegroundWindow(hwnd)
        except Exception as e:
            print("Failed to bring Chem3D window to foreground")
    else:
        print("Unable to find Chem3D window.")
        return

    time.sleep(0.5)
    # Send Ctrl+O to open the 'Open File' dialog
    keyboard.send('ctrl+o')
    time.sleep(1)

    # Copy the file path to clipboard and paste it
    pyperclip.copy(file_path)
    keyboard.send('ctrl+v')

    # Press Enter to open the file
    keyboard.send('enter')

    print("\n\nIf the output file is not opened in Chem3D, you can open it manually:\n" + file_path + "\n\n\n")

