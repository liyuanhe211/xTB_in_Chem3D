# -*- coding: utf-8 -*-
__author__ = 'LiYuanhe'

import os
import shutil

from Python_Lib.My_Lib_Stock import *

import PyInstaller.__main__

version = "0.1"
path = 'Pyinstaller_Packing'
work_path = os.path.join(path, f'temp_{version}')
output_path = os.path.join(path, "xTB_in_Chem3D_"+version)
os.remove(output_path)
include_all_folder_contents = []
include_folders = ["Python_Lib", 'xtb-6.7.1']
include_files = ["0_xTB_executable_path.txt", "0_Chem3D_Path.txt", "password for MOPAC2012"]

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

open_explorer_and_select(os.path.realpath(output_path))
