# -*- coding: utf-8 -*-
__author__ = 'LiYuanhe'

# import pathlib
# parent_path = str(pathlib.Path(__file__).parent.resolve())
# sys.path.insert(0,parent_path)
import os
import sys

from Python_Lib.My_Lib_PyQt6 import *
from Lib import open_file_with_Chem3D

Application = QtWidgets.QApplication(sys.argv)
font = Application.font()
font.setFamily("Arial")
Application.setFont(font)

if platform.system() == 'Windows':
    import ctypes

    APPID = 'LYH.xTB_in_Chem3D.0.2'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APPID)
    Application.setWindowIcon(QtGui.QIcon('UI/Icon.png'))
    # matplotlib_DPI_setting = get_matplotlib_DPI_setting(Windows_DPI_ratio)

if __name__ == '__main__':
    # pyqt_ui_compile('Orbital_Viewer_UI.py')
    from UI.Orbital_Viewer_UI import Ui_Orbital_Viewer


def MO_energy_from_molden(molden_file):
    with open(molden_file) as molden_file_content:
        molden_file_content = molden_file_content.read().splitlines()

    HOMOs, LUMOs = [], []
    for count, line in enumerate(molden_file_content):
        if re_ret := re.findall("Ene=\s+(-*\d+\.\d+E*-*\d+)", line):
            re_ret = float(re_ret[0]) * 2625.49962 / 96.484
            re_ret = f"{re_ret:.1f} eV"
            occupied = float(molden_file_content[count + 2].replace("Occup=", ""))
            if occupied > 1.5:
                HOMOs.append(re_ret)
            elif occupied < 0.5:
                LUMOs.append(re_ret)
            else:
                print("HOMOs:",HOMOs)
                print("LUMOs:",LUMOs)
                print("Occupied:",occupied)
                raise Exception("Error in molden occupation number.")
    return HOMOs, LUMOs


# print(MO_energy_from_molden(r"E:\My_Program\xTB_in_Chem3D\Tests\a.molden"))
# input("Paused,")


def run_for_MO(_molden_file, MO_number):
    """

    :param _molden_file:
    :param MO_number: HOMO is 0, LUMO is 1, LUMO+1 = 2
    :return:
    """

    temp_directory = filename_parent(_molden_file)
    orbital_designation = "l" if MO_number > 0 else "h"
    if MO_number < 0:
        orbital_designation += str(MO_number)
    elif MO_number > 1:
        orbital_designation += f"+{MO_number - 1}"

    MO_cube_file = os.path.join(temp_directory, "MOvalue.cub")
    MO_cube_file_new_name = f"{filename_stem(_molden_file)}_{orbital_designation.replace('l', 'LUMO').replace('h', 'HOMO')}.cub"
    MO_cube_file_new_name = os.path.join(temp_directory, MO_cube_file_new_name)
    os.chdir(temp_directory)
    script = f"""5
4
{orbital_designation}
2
6
25
2

"""
    # Create your process
    print(os.path.isfile(multiwfn_executable))
    print(os.path.isfile(_molden_file))
    print(" ".join([multiwfn_executable, _molden_file]))
    subprocess.run([multiwfn_executable, _molden_file],
                   input=script, text=True)
    # print(os.getcwd())
    # print(MO_cube_file)
    # print(os.path.isfile(MO_cube_file))
    # input("Paused")
    # # Pass string as input and get output
    # process.communicate(input=script.encode())
    # process.wait()

    if os.path.isfile(MO_cube_file):
        if os.path.isfile(MO_cube_file_new_name):
            os.remove(MO_cube_file_new_name)
        shutil.move(MO_cube_file, MO_cube_file_new_name)
    MO_cube_file = MO_cube_file_new_name
    open_file_with_Chem3D(MO_cube_file)


class MyWidget(Ui_Orbital_Viewer, QtWidgets.QWidget, Qt_Widget_Common_Functions):
    def __init__(self, _multiwfn_executable, _molden_filename):
        super(self.__class__, self).__init__()

        self.setupUi(self)

        self.multiwfn = _multiwfn_executable
        self.molden_filename = _molden_filename

        self.pushbutton_mapping = {self.HOMO_pushButton: 0,
                                   self.HOMO1_pushButton: -1,
                                   self.HOMO2_pushButton: -2,
                                   self.HOMO3_pushButton: -3,
                                   self.HOMO4_pushButton: -4,
                                   self.HOMO5_pushButton: -5,
                                   self.HOMO6_pushButton: -6,
                                   self.HOMO7_pushButton: -7,
                                   self.HOMO8_pushButton: -8,
                                   self.HOMO9_pushButton: -9,
                                   self.HOMO10_pushButton: -10,
                                   self.HOMO11_pushButton: -11,
                                   self.HOMO12_pushButton: -12,
                                   self.HOMO13_pushButton: -13,
                                   self.HOMO14_pushButton: -14,
                                   self.HOMO15_pushButton: -15,
                                   self.LUMO_pushButton: 1,
                                   self.LUMO1_pushButton: 2,
                                   self.LUMO2_pushButton: 3,
                                   self.LUMO3_pushButton: 4,
                                   self.LUMO4_pushButton: 5,
                                   self.LUMO5_pushButton: 6,
                                   self.LUMO6_pushButton: 7,
                                   self.LUMO7_pushButton: 8,
                                   self.LUMO8_pushButton: 9,
                                   self.LUMO9_pushButton: 10,
                                   self.LUMO10_pushButton: 11,
                                   self.LUMO11_pushButton: 12,
                                   self.LUMO12_pushButton: 13,
                                   self.LUMO13_pushButton: 14,
                                   self.LUMO14_pushButton: 15,
                                   self.LUMO15_pushButton: 16}

        for pushbutton in self.pushbutton_mapping:
            connect_once(pushbutton, self.MO_pushbutton_pressed)

        self.show_energies()

        self.show()

        self.center_the_widget()

    def show_energies(self):
        HOMOs, LUMOs = MO_energy_from_molden(self.molden_filename)
        for pushbutton, MO_number in self.pushbutton_mapping.items():
            energy = ""
            if MO_number <= 0:
                if MO_number - 1 >= -len(HOMOs):
                    energy = HOMOs[MO_number - 1]
            elif MO_number - 1 <= len(LUMOs) - 1:
                energy = LUMOs[MO_number - 1]
            energy = "  [{:>8}]".format(energy)
            pushbutton.setText("{:<7}".format(pushbutton.text().strip()) + energy)

    def MO_pushbutton_pressed(self):
        event_emitter = self.sender()
        print("Running for orbital", self.pushbutton_mapping[event_emitter], 'in file', self.molden_filename)
        run_for_MO(self.molden_filename, self.pushbutton_mapping[event_emitter])


if __name__ == '__main__':
    print("Running:", " ".join(sys.argv))
    if sys.argv[0].lower().endswith('python') or sys.argv[0].lower().endswith('python.exe') or sys.argv[0].lower().endswith('cmd'):
        multiwfn_executable, molden_file = sys.argv[2:4]
    else:
        multiwfn_executable, molden_file = sys.argv[1:3]
    gui = MyWidget(multiwfn_executable, molden_file)
    gui.show()
    sys.exit(Application.exec())
