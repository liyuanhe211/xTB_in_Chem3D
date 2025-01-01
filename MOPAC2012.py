# -*- coding: utf-8 -*-
__author__ = 'LiYuanhe'

import os.path
import re
import sys

from Python_Lib.My_Lib_Stock import *
from Python_Lib.My_Lib_File import filename_parent, filename_stem

home_directory = os.path.expanduser("~")
temp_directory = os.path.join(home_directory, 'Documents', "xTB_in_Chem3D", 'temp')
executable_directory = filename_parent(sys.argv[0])
os.chdir(executable_directory)  # 否则pwd会在chem3d.exe的目录下
os.makedirs(temp_directory, exist_ok=True)
random_int = str(random.randint(100, 900))

# How Chem3D calls MOPAC
# The MOPAC menu is activated when the C:\Program Files\MOPAC folder contains the files MOPAC2012.exe and "password for MOPAC2012"
# When running, for example a minimization, it creates the mop input file in C:\Users\LiYuanhe\Documents\Mopac Interface
# It calls something like: "C:\Program Files\MOPAC\MOPAC2012.exe" "C:\Users\LiYuanhe\DOCUME~1\MOPACI~1\Untitled-2.mop" 1028360364:1941695816
# Example input mop file
#
# AUX  PM7 CHARGE=0 EF GNORM=0.100 SHIFT=80
# Untitled-1
#
# C          -1.2079 1         0.6974 1         0.0000 1
# C          -1.2080 1        -0.6974 1         0.0000 1
# C           0.0000 1        -1.3948 1         0.0001 1
# C           1.2079 1        -0.6974 1         0.0001 1
# C           1.2080 1         0.6974 1         0.0000 1
# C           0.0000 1         1.3948 1         0.0000 1
# H          -2.1606 1         1.2474 1         0.0000 1
# H          -2.1606 1        -1.2474 1        -0.0001 1
# H           0.0000 1        -2.4948 1         0.0001 1
# H           2.1606 1        -1.2474 1         0.0001 1
# H           2.1606 1         1.2474 1        -0.0001 1
# H           0.0000 1         2.4948 1         0.0000 1
#
# After running, it will delete the mop file,  generate .aux and .out files, which will be read back to Chem3D, examples of output file in folder.


if __name__ == '__main__':
    input_filepath = filename_parent(sys.argv[1])
    input_filename_stem = filename_stem(sys.argv[1])
    input_filename_stem = re.sub(r"\[.+\]", "", input_filename_stem)
    temp_input_file = os.path.join(temp_directory, 'temp_xTB_in_Chem3D_[' + input_filename_stem + "]_" + readable_timestamp() +
                                   "_" + random_int + '.mop')

    with open(sys.argv[1]) as input_file:
        log_file_path = os.path.join(filename_parent(temp_directory), "0_xTB_in_Chem3D.log")
        with open(log_file_path, 'a') as input_file_log:
            input_file_content = input_file.read()
            input_file_log.write(input_file_content + '\n-------------\n')

    with open(temp_input_file, 'w') as temp_input_file_object:
        temp_input_file_object.write(input_file_content)

    if os.path.isfile("Process_Job.exe"):
        # 因为Process_Job.exe被打包后，是在TEMP里执行，所以__file__不对了
        full_executable_path = os.path.realpath("Process_Job.exe")
        # Construct the command to open cmd.exe and run your executable
        command = f'start /B start cmd.exe /k ""{full_executable_path}" "{temp_input_file}" "{input_filename_stem}" "{full_executable_path}""'
        print("Running CMD command:", command)
        os.system(command)

    else:
        subprocess.call(["python", "Process_Job.py", temp_input_file, input_filename_stem, os.path.realpath("Process_Job.py")])
