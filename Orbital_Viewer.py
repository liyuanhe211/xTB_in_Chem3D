# -*- coding: utf-8 -*-
__author__ = 'LiYuanhe'

# import pathlib
# parent_path = str(pathlib.Path(__file__).parent.resolve())
# sys.path.insert(0,parent_path)
import os
import random
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


def MO_energy_from_molden(_molden_file):
    with open(_molden_file) as molden_file_content:
        molden_file_content = molden_file_content.read().splitlines()

    HOMOs, LUMOs = [], []
    for count, line in enumerate(molden_file_content):
        if re_ret := re.findall(r"Ene=\s+(-*\d+\.\d+E*-*\d+)", line):
            re_ret = float(re_ret[0]) * 2625.49962 / 96.484
            re_ret = f"{re_ret:.1f} eV"
            occupied = float(molden_file_content[count + 2].replace("Occup=", ""))
            if occupied > 1.5:
                HOMOs.append(re_ret)
            elif occupied < 0.5:
                LUMOs.append(re_ret)
            else:
                print("HOMOs:", HOMOs)
                print("LUMOs:", LUMOs)
                print("Occupied:", occupied)
                raise Exception("Error in molden occupation number.")
    return HOMOs, LUMOs


# print(MO_energy_from_molden(r"E:\My_Program\xTB_in_Chem3D\Tests\a.molden"))
# input("Paused,")


def process_is_CPU_idle(pid, interval=1.0):
    """

    :param pid:
    :param interval: sampling time, seconds
    :return: True if is idle, False if not, None if pid not exist
    """
    import psutil
    try:
        process = psutil.Process(pid)
        cpu_percent = process.cpu_percent(interval=interval)
        if cpu_percent == 0:
            return True
        return False
    except psutil.NoSuchProcess:
        return None


class MyWidget(Ui_Orbital_Viewer, QtWidgets.QWidget, Qt_Widget_Common_Functions):
    def __init__(self, _multiwfn_executable, _molden_filename):
        super(self.__class__, self).__init__()

        self.setupUi(self)

        self.multiwfn = _multiwfn_executable
        self.molden_filename = _molden_filename

        self.lineEdit.setReadOnly(True)
        self.lineEdit.setText(self.molden_filename)

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

    def launch(self, MO_number):
        temp_directory = filename_parent(self.molden_filename)
        orbital_designation = "l" if MO_number > 0 else "h"
        if MO_number < 0:
            orbital_designation += str(MO_number)
        elif MO_number > 1:
            orbital_designation += f"+{MO_number - 1}"

        MO_cube_file = os.path.join(temp_directory, "MOvalue.cub")
        MO_cube_file_new_name = f"{filename_stem(self.molden_filename)}_[{orbital_designation.replace('l', 'LUMO').replace('h', 'HOMO')}]_{random.randint(10,99)}.cub"
        MO_cube_file_new_name = os.path.join(temp_directory, MO_cube_file_new_name)

        os.chdir(temp_directory)

        self.process = QProcess()
        self.process.setWorkingDirectory(temp_directory)
        self.process.start(self.multiwfn, [self.molden_filename])
        connect_once(self.process.readyReadStandardOutput, lambda process=self.process: self.write_output(self.process))
        connect_once(self.process.readyReadStandardError, lambda process=self.process: self.write_output(self.process))

        commands = ['5', '4', orbital_designation, '2', '6', '25', '2', ""]
        for command in commands:
            self.write_input(command)
            Application.processEvents()

        if os.path.isfile(MO_cube_file):
            if os.path.isfile(MO_cube_file_new_name):
                os.remove(MO_cube_file_new_name)
            shutil.move(MO_cube_file, MO_cube_file_new_name)
        MO_cube_file = MO_cube_file_new_name
        open_file_with_Chem3D(MO_cube_file)

    def MO_pushbutton_pressed(self):
        event_emitter = self.sender()
        print("Running for orbital", self.pushbutton_mapping[event_emitter], 'in file', self.molden_filename)
        self.launch(self.pushbutton_mapping[event_emitter])
        # run_for_MO(self.molden_filename, self.pushbutton_mapping[event_emitter])

    def write_text(self, text):
        # Move cursor to end before inserting new text
        cursor = self.output_textEdit.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.output_textEdit.setTextCursor(cursor)
        self.output_textEdit.insertPlainText(text)
        cursor.movePosition(cursor.MoveOperation.End)
        self.output_textEdit.setTextCursor(cursor)

        vertical_scroll_to_end(self.output_textEdit)

    def write_output(self, process):

        text = bytes(process.readAllStandardOutput()).decode('gbk')
        text += bytes(process.readAllStandardError()).decode('gbk')
        self.write_text(text)

    def write_input(self, text):
        self.wait_idle()
        self.write_text("\n\n>>> " + text + '\n\n\n')
        self.process.writeData(bytearray(text + "\n", encoding='gbk'))

    def wait_idle(self, sampling_interval=0.1):
        while process_is_CPU_idle(self.process.processId(), interval=sampling_interval) is False:
            Application.processEvents()
            time.sleep(0.1)


if __name__ == '__main__':
    print("Running:", " ".join(sys.argv))
    if sys.argv[0].lower().endswith('python') or sys.argv[0].lower().endswith('python.exe') or sys.argv[0].lower().endswith('cmd'):
        multiwfn_executable, molden_file = sys.argv[2:4]
    else:
        multiwfn_executable, molden_file = sys.argv[1:3]
    gui = MyWidget(multiwfn_executable, molden_file)
    gui.show()
    sys.exit(Application.exec())
