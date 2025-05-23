# -*- coding: utf-8 -*-
__author__ = 'LiYuanhe'

import re

from Lib import *

# TODO: Allow for custom input
solvent = "CH2Cl2"


# Test this program like:
# python Process_Job.py "E:\My_Program\xTB_in_Chem3D\Tests\ethane.mop" "ethane" "E:\My_Program\xTB_in_Chem3D\Process_Job.py"

def call_xtb(mopac_file, output_folder):
    xTB_run_path = filename_remove_append(temp_input_file)
    xyz_filepath = mopac_file + '.xyz'
    out_file = os.path.join(xTB_run_path, 'Run_xTB.out')
    _molden_file = os.path.join(xTB_run_path, 'molden.input')
    xtbopt_xyz_file = os.path.join(xTB_run_path, 'xtbopt.xyz')

    _charge = 0
    _multiplicity = 1
    GFN_label = "GFN2"
    GFN = ["--gfn", "2"]

    mopac_file_content = open(mopac_file, encoding='utf-8', errors='ignore').read().splitlines()

    command_line = mopac_file_content[0].lower()
    single_point_only = "sp" in command_line.split()
    charge_re_ret = re.findall(r"charge\=(-*\d+)", command_line)
    is_triplet = "triplet" in command_line
    MS_setting = re.findall(r"ms\=(-*\d+\.*\d*)", command_line)
    if MS_setting:
        _multiplicity = int(abs(float(MS_setting[0])) * 2 + 1)
    if MS_setting and is_triplet:
        print("\n\nYou should not set MS and TRIPLET at the same time.\n\n")
        sys.exit(1)
    GFN_keywords = {"GFN2": ["--gfn", "2"],
                    "GFN1": ["--gfn", "1"],
                    "GFN0": ["--gfn", "0"],
                    "GFNFF": ["--gfnff"]}
    for i in GFN_keywords:
        if i.lower() in command_line:
            GFN_label = i
            GFN = GFN_keywords[i]

    if charge_re_ret:
        _charge = int(charge_re_ret[0])
    regex_pattern = r"^([A-Z][a-z]{0,2})\s+(-*\d+\.\d*)\s+\d+\s+(-*\d+\.\d*)\s+\d+\s+(-*\d+\.\d*)"
    input_coordinate = []
    input_coordinate_lines = []
    elements = []
    for i in mopac_file_content:
        if re_ret := re.findall(regex_pattern, i):
            re_ret = re_ret[0]
            if re_ret[0] in element_to_num_dict:
                elements.append(element_to_num_dict[re_ret[0]])
                input_coordinate.append(re_ret)
                input_coordinate_lines.append("\t".join(re_ret))

    total_electron = sum(elements) - _charge
    if total_electron % 2 == 1:
        _multiplicity = 2
    if is_triplet:
        _multiplicity = 3

    print(f"Charge: {_charge}; Multiplicity: {_multiplicity}")

    xyz_file_content = f"{len(input_coordinate)}\n{mopac_file}\n" + "\n".join("\t".join(atom) for atom in input_coordinate) + '\n'
    with open(xyz_filepath, 'w', encoding='utf-8', errors='ignore') as xyz_filepath_object:
        xyz_filepath_object.write(xyz_file_content)

    os.makedirs(xTB_run_path, exist_ok=True)
    print("Running xTB in:", xTB_run_path)
    os.chdir(xTB_run_path)

    print("Running for:", out_file, "...")
    if single_point_only:
        xTB_command = [xTB_bin, xyz_filepath, "--chrg", str(_charge), "--alpb", solvent, '--uhf', str(_multiplicity - 1), "--molden"] + GFN
    else:
        xTB_command = [xTB_bin, xyz_filepath, '--opt', 'vtight', "--chrg", str(_charge), "--alpb", solvent, '--uhf', str(_multiplicity - 1), "--molden"] + GFN
    print("Command args:", " ".join(xTB_command))

    # 不知道如何同时输出到stdout和file stream，反正很快，直接跑两遍算了
    process = subprocess.Popen(xTB_command, stdout=open(out_file, 'w'))
    subprocess.call(xTB_command)

    process.wait()

    electronic_energy = 0
    if single_point_only:
        print("\n\n\nxTB Single Point calculation ended.\n\n")
        output_coordinate_lines = input_coordinate_lines
        xtb_out_lines = open(out_file, encoding='utf-8', errors='ignore').read().splitlines()
        for line in reversed(xtb_out_lines):
            re_ret = re.findall(r"TOTAL ENERGY\s+(-*\d+\.\d+)\s+Eh", line)
            if re_ret:
                electronic_energy = float(re_ret[0]) * 2625.49962
                break
    else:
        if not os.path.isfile(xtbopt_xyz_file):
            print("\n\n\nxTB calculation failed.\n\n")
            sys.exit(1)

        with open(xtbopt_xyz_file, encoding='utf-8', errors='ignore') as xtbopt_xyz_file_object:
            xtbopt_xyz_file_content = xtbopt_xyz_file_object.read().splitlines()

        output_coordinate_lines = []
        for line in reversed(xtbopt_xyz_file_content):
            if not re.findall(r"^([A-Z][a-z]{0,2})\s+(-*\d+\.\d*)\s+(-*\d+\.\d*)\s+(-*\d+\.\d*)", line):
                electronic_energy = re.findall(r'energy\: (-*\d+\.\d*)', line)[0]
                electronic_energy = float(electronic_energy) * 2625.49962
                break
            output_coordinate_lines.append(line)
        if electronic_energy is None:
            raise Exception("Electronic Energy Not Found.")

    out_xyz_filename = os.path.join(output_folder,
                                    input_filename_stem +
                                    "_[" + GFN_label + " = {:.1f}".format(electronic_energy) + f" kJ_mol]_[Chg {_charge}]_[Mult {_multiplicity}].xyz")

    with open(out_xyz_filename, 'w', encoding='utf-8', errors='ignore') as output_gjf_file_object:
        output_gjf_file_object.write(f"{len(output_coordinate_lines)}\n\n" +
                                     "\n".join(reversed(output_coordinate_lines)))

    _out_sdf_filename = filename_replace_last_append(out_xyz_filename, 'sdf')
    print("Output SDF file:", _out_sdf_filename)
    os.environ['BABEL_DATADIR'] = os.path.join(executable_directory, "OpenBabel", 'data')
    subprocess.call([os.path.join(executable_directory, "OpenBabel", 'obabel.exe'), '-ixyz', out_xyz_filename, "-osdf", '-O', _out_sdf_filename])

    return _out_sdf_filename, out_file, _multiplicity, _molden_file


if __name__ == '__main__':
    if sys.argv[0].lower().endswith('python') or sys.argv[0].lower().endswith('python.exe') or sys.argv[0].lower().endswith('cmd'):
        temp_input_file = sys.argv[2]
        input_filename_stem = sys.argv[3]
        executable_directory = filename_parent(sys.argv[4])
    else:
        temp_input_file = sys.argv[1]
        input_filename_stem = sys.argv[2]
        executable_directory = filename_parent(sys.argv[3])

    print("Temporary input file:", temp_input_file)
    print("Input filename stem:", input_filename_stem)
    print("Executable directory:", executable_directory)

    temp_folder = filename_parent(temp_input_file)
    output_directory = filename_parent(temp_folder)
    chem3D_path = open(os.path.join(executable_directory, "0_Chem3D_Path.txt")).read().splitlines()[0]
    xTB_bin = open(os.path.join(executable_directory, "0_xTB_executable_path.txt")).read().splitlines()[0]
    xTB_bin = os.path.join(executable_directory, xTB_bin)

    out_sdf_filename, xtb_out, multiplicity, molden_file = call_xtb(temp_input_file, output_directory)

    shutil.move(xtb_out, xtb_out + '.txt')
    os.startfile(xtb_out + '.txt')
    open_file_with_Chem3D(out_sdf_filename, chem3D_path)

    multiwfn_executable = os.path.join(executable_directory, 'Multiwfn', "Multiwfn.exe")
    new_molden_file = filename_replace_last_append(out_sdf_filename, 'molden')
    shutil.move(molden_file, new_molden_file)

    orbital_viewer_command = os.path.join(executable_directory, 'Orbital_Viewer.exe')
    if not os.path.isfile(orbital_viewer_command):
        orbital_viewer_command = ["python ", orbital_viewer_command[:-4] + ".py"] + [multiwfn_executable, new_molden_file, out_sdf_filename]
    else:
        # 用start cmd /k后面的命令必须套一层额外的"" 并且作为一个独立的参数
        # orbital_viewer_command = f'""{orbital_viewer_command}" "{multiwfn_executable}" "{new_molden_file}""'
        # orbital_viewer_command = 'start cmd.exe /k ' + orbital_viewer_command
        orbital_viewer_command = [orbital_viewer_command, multiwfn_executable, new_molden_file, out_sdf_filename]

    if multiplicity == 1:
        print("Launching orbital viewer...")
        # print(orbital_viewer_command)
        subprocess.call(orbital_viewer_command)
        # subprocess.call(orbital_viewer_command, shell=True)
