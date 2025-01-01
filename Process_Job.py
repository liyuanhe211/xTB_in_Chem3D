# -*- coding: utf-8 -*-
__author__ = 'LiYuanhe'

import shutil
import sys
import time

import psutil
import pyperclip
import win32gui
import win32process
import keyboard

from Python_Lib.My_Lib_Stock import *
from Python_Lib.My_Lib_File import filename_parent, filename_stem

# TODO: Allow for custom input
solvent = "CH2Cl2"


# Test this program like:
# python Process_Job.py "E:\My_Program\xTB_in_Chem3D\example.mop" "example" "C:\Program Files\MOPAC\Process_Job.exe""

def open_gjf_with_Chem3D(file_path):
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
        win32gui.SetForegroundWindow(hwnd)
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


def call_xtb(mopac_file, output_folder):
    xTB_run_path = filename_remove_append(temp_input_file)
    xyz_filepath = mopac_file + '.xyz'
    out_file = os.path.join(xTB_run_path, 'Run_xTB.out')
    xtbopt_xyz_file = os.path.join(xTB_run_path, 'xtbopt.xyz')

    charge = 0
    multiplicity = 1

    mopac_file_content = open(mopac_file).read().splitlines()
    charge_re_ret = re.findall(r"charge\=(\d+)", mopac_file_content[0].lower())
    if charge_re_ret:
        charge = int(charge_re_ret[0])
    regex_pattern = r"^([A-Z][a-z]{0,2})\s+(-*\d+\.\d*)\s+\d+\s+(-*\d+\.\d*)\s+\d+\s+(-*\d+\.\d*)"
    coordinates = []
    for i in mopac_file_content:
        if re_ret := re.findall(regex_pattern, i):
            re_ret = re_ret[0]
            if re_ret[0] in element_to_num_dict:
                coordinates.append(re_ret)

    xyz_file_content = f"{len(coordinates)}\n{mopac_file}\n" + "\n".join("\t".join(atom) for atom in coordinates) + '\n'
    with open(xyz_filepath, 'w') as xyz_filepath_object:
        xyz_filepath_object.write(xyz_file_content)

    os.makedirs(xTB_run_path, exist_ok=True)
    print("Running xTB in:", xTB_run_path)
    os.chdir(xTB_run_path)

    print("Running for:", out_file, "...")
    xTB_command = [xTB_bin, xyz_filepath, '--opt', "--chrg", str(charge), "--alpb", solvent, '--uhf', str(multiplicity - 1)]
    print("Command args:", " ".join(xTB_command))

    # 不知道如何同时输出到stdout和file stream，反正很快，直接跑两遍算了
    process = subprocess.Popen(xTB_command, stdout=open(out_file,'w'))
    subprocess.call(xTB_command)

    process.wait()
    with open(xtbopt_xyz_file) as xtbopt_xyz_file_object:
        xtbopt_xyz_file_content = xtbopt_xyz_file_object.read().splitlines()

    output_coordinate_lines = []
    electronic_energy = None
    for line in reversed(xtbopt_xyz_file_content):
        if not re.findall(r"^([A-Z][a-z]{0,2})\s+(-*\d+\.\d*)\s+(-*\d+\.\d*)\s+(-*\d+\.\d*)", line):
            electronic_energy = re.findall(r'energy\: (-*\d+\.\d*)', line)[0]
            electronic_energy = float(electronic_energy) * 2625.49962
            break
        output_coordinate_lines.append(line)
    if electronic_energy is None:
        raise Exception("Electronic Energy Not Found.")
    out_gjf_filename = filename_stem(mopac_file)
    out_gjf_filename = out_gjf_filename.split('_xTB')[0]
    out_gjf_filename = os.path.join(output_folder,
                                    out_gjf_filename + '_xTB_' + readable_timestamp() + "_" + "[E = {:.1f}".format(electronic_energy) + " J]" + ".gjf")

    with open(out_gjf_filename, 'w') as output_gjf_file_object:
        output_gjf_file_object.write(f"#p\n\ntitle\n\n{charge} {multiplicity}\n" + "\n".join(reversed(output_coordinate_lines)))

    return out_gjf_filename, out_file


if __name__ == '__main__':
    if sys.argv[0].lower().endswith('python') or sys.argv[0].lower().endswith('python.exe') or sys.argv[0].lower().endswith('cmd'):
        temp_input_file = sys.argv[2]
        input_filename_stem = sys.argv[3]
        executable_directory = filename_parent(sys.argv[4])
    else:
        temp_input_file = sys.argv[1]
        input_filename_stem = sys.argv[2]
        executable_directory = filename_parent(sys.argv[3])

    temp_folder = filename_parent(temp_input_file)
    output_directory = filename_parent(temp_folder)
    chem3D_path = open(os.path.join(executable_directory, "0_Chem3D_Path.txt")).read().splitlines()[0]
    xTB_bin = open(os.path.join(executable_directory, "0_xTB_executable_path.txt")).read().splitlines()[0]
    xTB_bin = os.path.join(executable_directory, xTB_bin)

    out_gjf, xtb_out = call_xtb(temp_input_file, output_directory)

    shutil.move(xtb_out, xtb_out + '.txt')
    os.startfile(xtb_out + '.txt')
    open_gjf_with_Chem3D(out_gjf)
