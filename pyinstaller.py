# -*- coding: utf-8 -*-
__author__ = 'LiYuanhe'

import os
import shutil

from Python_Lib.My_Lib_Stock import *

import PyInstaller.__main__

version = "0.2"
path = 'Pyinstaller_Packing'
NSIS_executable = r"C:\Program Files (x86)\NSIS\Bin\makensis.exe"
assert os.path.isfile(NSIS_executable), 'You need to install NSIS 3.10 with the installer in Pyinstaller_Packaging'
work_path = os.path.join(path, f'temp_{version}')
output_path = os.path.join(path, "xTB_in_Chem3D_" + version)
installer_filename = f"xTB_in_Chem3D {version}.exe"
if os.path.isdir(output_path):
    shutil.rmtree(output_path)
if os.path.isfile(os.path.join("Pyinstaller_Packing", installer_filename)):
    os.remove(os.path.join("Pyinstaller_Packing", installer_filename))
include_all_folder_contents = []
include_folders = ["Python_Lib", 'xtb-6.7.1', 'OpenBabel', "Multiwfn"]
include_files = ["0_xTB_executable_path.txt", "0_Chem3D_Path.txt", "password for MOPAC2012", "vcredist_x86.exe"]

include_files += [r"C:\Anaconda3\Library\plugins\platforms\qdirect2d.dll",
                  r"C:\Anaconda3\Lib\site-packages\PyQt6\Qt6\plugins\platforms\qminimal.dll",
                  r"C:\Anaconda3\Lib\site-packages\PyQt6\Qt6\plugins\platforms\qoffscreen.dll",
                  r"C:\Anaconda3\Library\plugins\platforms\qwebgl.dll",
                  r"C:\Anaconda3\Lib\site-packages\PyQt6\Qt6\plugins\platforms\qwindows.dll",
                  r"C:\Anaconda3\Library\plugins\platformthemes\qxdgdesktopportal.dll",
                  r"C:\Anaconda3\Lib\site-packages\PyQt6\Qt6\plugins\iconengines\qsvgicon.dll",
                  r"C:\Anaconda3\Lib\site-packages\PyQt6\Qt6\plugins\imageformats\qgif.dll",
                  r"C:\Anaconda3\Lib\site-packages\PyQt6\Qt6\plugins\imageformats\qicns.dll",
                  r"C:\Anaconda3\Lib\site-packages\PyQt6\Qt6\plugins\imageformats\qico.dll",
                  r"C:\Anaconda3\Lib\site-packages\PyQt6\Qt6\plugins\imageformats\qjpeg.dll",
                  r"C:\Anaconda3\Lib\site-packages\PyQt6\Qt6\plugins\imageformats\qpdf.dll",
                  r"C:\Anaconda3\Lib\site-packages\PyQt6\Qt6\plugins\imageformats\qsvg.dll",
                  r"C:\Anaconda3\Lib\site-packages\PyQt6\Qt6\plugins\imageformats\qtga.dll",
                  r"C:\Anaconda3\Lib\site-packages\PyQt6\Qt6\plugins\imageformats\qtiff.dll",
                  r"C:\Anaconda3\Lib\site-packages\PyQt6\Qt6\plugins\imageformats\qwbmp.dll",
                  r"C:\Anaconda3\Lib\site-packages\PyQt6\Qt6\plugins\imageformats\qwebp.dll",
                  r"C:\Anaconda3\Lib\site-packages\PyQt6\Qt6\plugins\styles\qwindowsvistastyle.dll"]

PyInstaller.__main__.run(["MOPAC2012.py",
                          # "--icon", icon,
                          "--name", "MOPAC2012.exe",
                          "--workpath", work_path,
                          "--distpath", output_path,
                          '--onefile',
                          '--paths', '.\\Python_Lib',
                          '--clean'])

PyInstaller.__main__.run(["Process_Job.py",
                          # "--icon", icon,
                          "--name", "Process_Job.exe",
                          "--workpath", work_path,
                          "--distpath", output_path,
                          '--onefile',
                          '--paths', '.\\Python_Lib',
                          '--clean'])

PyInstaller.__main__.run(["Orbital_Viewer.py",
                          "--icon", "UI/Icon.png",
                          "--name", "Orbital_Viewer.exe",
                          "--workpath", work_path,
                          "--distpath", output_path,
                          '--onefile',
                          '--paths', '.\\Python_Lib',
                          '--hidden-import', 'PyQt6',
                          '--exclude-module', 'PyQt5',
                          '--clean',
                          "--console"])


def copy_folder(src, dst):
    """

    :param src:
    :param dst: dst will *contain* src folder
    :return:
    """
    _target = os.path.realpath(os.path.join(dst, filename_class(src).name))
    if os.path.isdir(_target):
        try:
            shutil.rmtree(_target)
            print("Deleting:", _target)
        except Exception:
            print("Delete Failed:", _target)
            return None
    print("Copying:", src, 'to', dst)
    shutil.copytree(src, _target)


for file in include_files:
    print(f"Copying {file} to {output_path}")
    shutil.copy(file, output_path)

for folder in include_folders:
    copy_folder(folder, output_path)

for folder in include_all_folder_contents:
    target = os.path.realpath(os.path.join(output_path, filename_class(folder).name))
    for current_object in os.listdir(folder):
        current_object = os.path.join(folder, current_object)
        if os.path.isfile(current_object):
            shutil.copy(current_object, output_path)
        else:
            copy_folder(current_object, output_path)

files_to_move = list(os.listdir(output_path))

target_path = os.path.join(output_path, "Program Files", "MOPAC")

if not os.path.exists(target_path):
    os.makedirs(target_path)

for item in files_to_move:
    s = os.path.join(output_path, item)
    d = os.path.join(target_path, item)
    shutil.move(s, d)

output_path = os.path.realpath(output_path)

os.chdir("Pyinstaller_Packing")

with open("NSIS_Script.nsi", 'w') as nsis_script:
    nsis_script.write(rf"""Outfile "{installer_filename}"
SetCompressor /SOLID zlib
InstallDir "$PROGRAMFILES64\MOPAC"

Page instfiles

Section "PreInstall"
    IfFileExists $INSTDIR\*.* AskOverwrite
    GoTo Install

    AskOverwrite:
    MessageBox MB_YESNO|MB_ICONQUESTION "Install directory already exists. Do you want to overwrite it? You should NOT install this program if you do need the original MOPAC function in Chem3D." IDYES Install
    Quit

    Install: 
SectionEnd

Section "Install"
    SetOutPath $INSTDIR
    File /r "xTB_in_Chem3D_{version}\Program Files\MOPAC\*"
    CreateDirectory "$SMPROGRAMS\MOPAC"
    CreateShortCut "$SMPROGRAMS\MOPAC\Uninstall.lnk" "$INSTDIR\Uninstaller.exe"
    WriteUninstaller "$INSTDIR\Uninstaller.exe"  ; 
    
    IfFileExists "$SYSDIR\MSVCP100.dll" 0 installVcredist
    DetailPrint "vcredist_x86 is already installed."
    Goto endInstall
    
    installVcredist:
    DetailPrint "vcredist_x86 is not installed. Installing now..."
    ExecWait '$INSTDIR\vcredist_x86.exe'
        
    endInstall:
    
SectionEnd

Section "Uninstall"
    Delete "$SMPROGRAMS\MOPAC\Uninstall.lnk"
    RMDir /r "$INSTDIR"
    RMDir "$SMPROGRAMS\MOPAC"
SectionEnd
""")

subprocess.call([NSIS_executable, 'NSIS_Script.nsi'])
open_explorer_and_select(output_path)
