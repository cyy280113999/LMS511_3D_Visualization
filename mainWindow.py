# sys pk
import sys
from functools import partial
# third pk
import vtk
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import *
from PyQt5.QtGui import QIcon
# from PyQt5.QtWidgets import QDesktopWidget
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QPushButton

from PyQt5.QtCore import *
from PyQt5.QtCore import pyqtSignal

from PyQt5.QtWidgets import QFileDialog

# user pk
from VtkPointCloud import VtkPointCloud
from InformationWindow import InformationWindow
from mySock import MySock
from VtkWindow import VtkWindow
from TelegramProcess import *

# Settings:
_ip = "169.254.104.114"
_port = 2111
# _scan = "\x02sRN LMDscandata\x03"
# Debug
Debug_ColorOn = False

Debug_Round_Period = 20  # (s)
Debug_Round_Gap = 0.02  # (s)

Debug_Round_Bottom = -0.5
Debug_Round_Top = 2.5
Debug_Round_anglemin = 0
Debug_Round_anglemax = 150


class MainWindow(QMainWindow):
    Debug_info_widget_open = False
    refresh_signal = pyqtSignal()

    later_process_signal = pyqtSignal(int)

    def __init__(self):
        #
        super().__init__()
        # 先放置UI控件
        # 初始化VTK窗口
        # 初始化网络接口
        # 按钮连接最后执行

        ### set mainFrame UI
        ##  main window settings
        self.setGeometry(200, 100, 1000, 800)  # this is nonsense
        # self.frameGeometry().moveCenter(QDesktopWidget.availableGeometry().center())
        self.setWindowTitle("LMS511_Connector")
        self.setWindowIcon(QIcon('lidar.ico'))
        self.setIconSize(QSize(20, 20))

        # add Tab to main window
        mainTab = QTabWidget()
        self.setCentralWidget(mainTab)
        ## tab settings
        # add first tab, control
        tabControl = QWidget()
        mainTab.addTab(tabControl, "Controller")
        # tab control has a horizonal field, include two vertical field , containing button and others
        control_layout = QHBoxLayout()
        cleft_panel = QVBoxLayout()
        cright_panel = QVBoxLayout()
        tabControl.setLayout(control_layout)  # goes h
        control_layout.addLayout(cleft_panel)  # v
        control_layout.addLayout(cright_panel)  # v
        # controller's items
        # on the left
        # net connector , includes texts , your input ip and port , a button
        ip_group = IpGroup()
        cleft_panel.addWidget(ip_group)
        # grouped panel of all setting items .
        settings_group = QGroupBox()
        settings_group.setTitle("设置面板")
        settings_panel = QVBoxLayout()
        settings_group.setLayout(settings_panel)
        cleft_panel.addWidget(settings_group)
        # settings: log in
        self.login_btn = QPushButton("log in")
        self.logout_btn = QPushButton("log out")
        self.savepara_btn = QPushButton("save paraments")
        login_panel = QHBoxLayout()
        login_panel.addWidget(self.login_btn)
        login_panel.addWidget(self.logout_btn)
        login_panel.addWidget(self.savepara_btn)
        login_group = QGroupBox()
        login_group.setTitle("登录控制")
        login_group.setLayout(login_panel)
        settings_panel.addWidget(login_group)
        # frequency & resolution
        self.frequency_list = QComboBox()
        self.resolution_list = QComboBox()
        self.frequency_btn = QPushButton("change frequency resolution")
        temp = QStandardItemModel()
        for str_ in ["25", "35", "50", "75", "100"]:
            temp2 = QStandardItem(str_ + 'hz')
            temp2.setData(str_ + '00', Qt.ToolTipRole)
            temp.appendRow(temp2)
        self.frequency_list.setModel(temp)
        self.frequency_list.setCurrentIndex(2)
        temp3 = QStandardItemModel()
        for str_, str_res in zip(["0.1667°", "0.25°", "0.3333°", "0.5°", "0.667°", "1°"],
                                 ["1667", "2500", "3333", "5000", "6670", "10000"]):
            temp4 = QStandardItem(str_)
            temp4.setData(str_res, Qt.ToolTipRole)
            temp3.appendRow(temp4)
        self.resolution_list.setModel(temp3)
        self.resolution_list.setCurrentIndex(3)
        freq_panel = QHBoxLayout()
        freq_panel.addWidget(self.frequency_list)
        freq_panel.addWidget(self.resolution_list)
        freq_panel.addWidget(self.frequency_btn)
        freq_group = QGroupBox()
        freq_group.setLayout(freq_panel)
        freq_group.setTitle("扫描频率及角度分辨率")
        settings_panel.addWidget(freq_group)
        # change scanning angle
        self.angle_min = QSpinBox()
        self.angle_max = QSpinBox()
        self.angle_btn = QPushButton("change angle")
        angle_panel = QHBoxLayout()
        angle_panel.addWidget(self.angle_min)
        self.angle_min.setRange(-5, 185)
        self.angle_min.setValue(Debug_Round_anglemin)
        angle_panel.addWidget(self.angle_max)
        self.angle_max.setRange(-5, 185)
        self.angle_max.setValue(Debug_Round_anglemax)
        angle_panel.addWidget(self.angle_btn)
        angle_group = QGroupBox()
        angle_group.setLayout(angle_panel)
        angle_group.setTitle("扫描角度范围")
        settings_panel.addWidget(angle_group)
        # other hardware settings
        hardware_group = QGroupBox()
        hardware_panel = QVBoxLayout()
        hardware_group.setLayout(hardware_panel)
        hardware_group.setTitle("其他及硬件控制")
        # rewrite ip addr
        ipchange_panel = QHBoxLayout()
        ipchange_edit = QLineEdit(_ip)
        ipchange_btn = QPushButton("change device ip")
        ipchange_panel.addWidget(ipchange_edit)
        ipchange_panel.addWidget(ipchange_btn)
        hardware_panel.addLayout(ipchange_panel)
        # reboot
        reboot_btn = QPushButton("reboot device")
        hardware_panel.addWidget(reboot_btn)
        settings_panel.addWidget(hardware_group)
        #
        cleft_panel.addStretch(1)
        # on the right
        self.showInformationButton = QPushButton("Debug info window")
        cright_panel.addWidget(self.showInformationButton)
        # self.showInformationButton.setCheckable(True)
        # round settings
        self.round_period = QDoubleSpinBox()
        self.round_gap = QDoubleSpinBox()
        round_panel = QHBoxLayout()
        round_panel.addWidget(QLabel("Round Period"))
        round_panel.addWidget(self.round_period)
        self.round_period.setRange(1, 100)
        self.round_period.setValue(Debug_Round_Period)
        round_panel.addWidget(QLabel("Gap"))
        self.round_gap.setRange(0.010, 1.000)
        self.round_gap.setSingleStep(0.001)
        self.round_gap.setDecimals(3)
        self.round_gap.setValue(Debug_Round_Gap)
        round_panel.addWidget(self.round_gap)
        round_panel.addStretch(1)
        round_group = QGroupBox()
        round_group.setLayout(round_panel)
        round_group.setTitle("旋转扫描参数")
        cright_panel.addWidget(round_group)
        #
        cright_panel.addWidget(QPushButton("unused"))
        cright_panel.addWidget(QPushButton("unused"))
        #
        cright_panel.addStretch(1)

        # tab visual
        tabVisualization = QWidget()
        visualization_layout = QVBoxLayout()
        vtop_panel = QHBoxLayout()
        vbottom_container = QHBoxLayout()
        vleft_panel = QVBoxLayout()
        vright_panel = QVBoxLayout()
        mainTab.addTab(tabVisualization, "Visualization")
        tabVisualization.setLayout(visualization_layout)  # |
        visualization_layout.addLayout(vtop_panel)  # -
        visualization_layout.addLayout(vbottom_container)  # --
        vbottom_container.addLayout(vleft_panel)  # |
        vbottom_container.addLayout(vright_panel)  # |
        # visual items
        self.DEM_min = QDoubleSpinBox()
        # QLineEdit(str(Debug_Round_Bottom))
        self.DEM_max = QDoubleSpinBox()
        # QLineEdit(str(Debug_Round_Top))
        self.colorOn_btn = QPushButton("DEM on")
        self.loadPoint_btn = QPushButton("load")
        self.savePoint_btn = QPushButton("save")
        # self.default_login_btn = QtWidgets.QPushButton("default login")
        self.read_once_btn = QPushButton("read once")
        self.read_always_btn = QPushButton()
        self.RoundModeBtn = QPushButton("Round Scan")
        self.progressBar = QProgressBar()

        vtop_panel.addStretch(1)
        vtop_panel.addWidget(self.DEM_min)
        self.DEM_min.setRange(-100, 100)
        self.DEM_min.setValue(Debug_Round_Bottom)
        vtop_panel.addWidget(self.DEM_max)
        self.DEM_max.setRange(-100, 100)
        self.DEM_max.setValue(Debug_Round_Top)
        vtop_panel.addWidget(self.colorOn_btn)
        self.colorOn_btn.setCheckable(True)
        vtop_panel.addWidget(self.loadPoint_btn)
        vtop_panel.addWidget(self.savePoint_btn)
        vleft_panel.addWidget(self.read_once_btn)
        vleft_panel.addWidget(self.read_always_btn)
        vleft_panel.addWidget(self.RoundModeBtn)
        vleft_panel.addStretch(1)
        vleft_panel.addWidget(self.progressBar)

        self.progressBar.setMaximumWidth(200)
        # self.progressBar.setTextVisible(True)
        self.progressBar.setValue(0)
        self.progressBar.setVisible(True)
        # self.progressBar.setVisible(False)

        #
        # self.buttonpanel.addWidget(self.defaultlogin)
        # self.left_panel.addStretch(1)
        # points screen
        self.vtkWindow = VtkWindow(vright_panel)
        # self.right_panel.addWidget(self.qvtkinteract)

        # others
        self.mysock = MySock(self)
        self.pointCloud = VtkPointCloud(zMin=Debug_Round_Bottom, zMax=Debug_Round_Top)
        # display
        self.vtkWindow.addActor(self.pointCloud.getActor())
        # status message
        self.statusBar().showMessage("unconnected")
        # Information Window
        self.informationWindow = InformationWindow()

        # functions , buttons
        # set button press
        # self.connect_btn.clicked.connect(
        #     lambda: self.mysock.connect((self.connect_ip.text(), int(self.connect_port.text()))))
        ip_group.connect(self.mysock.connect)  # use class instead
        self.login_btn.clicked.connect(self.mysock.login)
        self.logout_btn.clicked.connect(self.mysock.logout)
        self.savepara_btn.clicked.connect(self.mysock.savepara)
        self.frequency_btn.clicked.connect(
            lambda: self.mysock.change_freq(self.frequency_list.currentData(Qt.ToolTipRole),
                                            self.resolution_list.currentData(Qt.ToolTipRole)))
        self.angle_btn.clicked.connect(
            lambda: self.mysock.change_angle(self.angle_min.value(), self.angle_max.value()))
        ipchange_btn.clicked.connect(lambda: self.mysock.changeip(ipchange_edit.text()))
        reboot_btn.clicked.connect(self.mysock.reboot)

        self.showInformationButton.clicked.connect(self.show_information_window)

        self.read_once_btn.clicked.connect(self.mysock.readonce)
        self.read_always_btn.clicked.connect(self.mysock.readalways)
        self.DEM_max.valueChanged.connect(
            lambda: self.pointCloud.setColorRange(float(self.DEM_min.text()), float(self.DEM_max.text())))
        self.DEM_min.valueChanged.connect(
            lambda: self.pointCloud.setColorRange(float(self.DEM_min.text()), float(self.DEM_max.text())))
        # self.colorOn_btn.toggled.connect(
        #     lambda: self.pointCloud.setColorRange(float(self.DEM_min.text()), float(self.DEM_max.text())))
        self.savePoint_btn.clicked.connect(self.savePointCloud)
        self.loadPoint_btn.clicked.connect(self.loadPointCloud)
        self.RoundModeBtn.clicked.connect(
            lambda: self.mysock.round_read(self.round_period.value(), self.round_gap.value()))
        self.RoundModeBtn.setShortcut("Left")
        self.refresh_signal.connect(self.refresh_fun)
        # Button Text
        # eg:
        self.read_always_btn.Text_Off = lambda: self.read_always_btn.setText("read always")
        self.read_always_btn.Text_On = partial(self.read_always_btn.setText, "stop reading")
        self.read_always_btn.Text_Off()

        # Show
        self.showMaximized()

    # solve returned data to add in screen----------------------------------
    def process_once_data(self, data):
        points = data_process(data)
        self.pointCloud.setPoints(points)
        self.refresh()
        # self.qvtkinteract.GetRenderWindow().Render()

    def process_round_data(self, data, now_in_period, period):
        # clear in thread
        points = Debug_rounddata_process(data, now_in_period, period)
        self.pointCloud.addPoints(points)
        self.refresh()

    def _old_process_round_data(self, data, temp_time, total_times):
        if temp_time == 0:
            self.pointCloud.clearPoints()
        points = Debug_rounddata_process(data, temp_time, total_times)
        self.pointCloud.addPoints(points)
        self.refresh()

    def _old_process_round_data_later(self, data, temp_time, total_times):

        if temp_time == 0:
            self.pointCloud.clearPoints()
            self.later_data = []
            # self.later_process_signal=QtCore.pyqtSignal(int)  # class attr
            self.later_process_signal.connect(self.process_round_data_final)

        self.later_data.append(data)

        if temp_time == total_times - 1:
            self.later_process_signal.emit(total_times)

    def _old_process_round_data_final(self, total_times):
        ii = 0
        for data in self.later_data:
            points = Debug_rounddata_process(data, ii, total_times)
            self.pointCloud.addPoints(points)
            self.refresh()
            ii = ii + 1

    # save point cloud-------------------------------------
    def savePointCloud(self):
        # import os
        # cwd = os.getcwd()
        # filename = QtWidgets.QFileDialog.getSaveFileName(self,directory=)
        filename_long, f_type = QFileDialog.getSaveFileName(self,
                                                            caption="保存点云",
                                                            filter="PLY Files (*.ply);;STL Files (*.stl)")
        filename = filename_long.split('/')[-1]
        # print(filename, f_type, type(f_type))
        if filename:
            if f_type == "PLY Files (*.ply)":
                try:
                    plyWriter = vtk.vtkPLYWriter()
                    plyWriter.SetFileName(filename)
                    plyWriter.SetInputData(self.pointCloud.getPoly())
                    plyWriter.Write()
                except Exception as e:
                    print(e)
            elif f_type == 'STL Files (*.stl)':
                try:
                    stlWriter = vtk.vtkSTLWriter()
                    stlWriter.SetFileName(filename)
                    stlWriter.SetInputData(self.pointCloud.getPoly())
                    stlWriter.Write()
                except Exception as e:
                    print(e)
        else:
            print('no file saved')

    # load point cloud
    def loadPointCloud(self):
        # import os
        # cwd = os.getcwd()
        # filename = QtWidgets.QFileDialog.getSaveFileName(self,directory=)
        try:
            filename_long, f_type = QFileDialog.getOpenFileName(self,
                                                                caption="读取点云", filter="PLY Files (*.ply)")
            filename = filename_long.split('/')[-1]
            if filename:
                try:
                    self.pointCloud.clearPoints()
                    reader = vtk.vtkPLYReader()
                    reader.SetFileName(filename)
                    reader.Update()
                    polydata = reader.GetOutput()
                    self.pointCloud.setOutPoly(polydata, colorOn=self.colorOn_btn.isChecked())
                    self.refresh()
                except Exception as e:
                    print(e)

            else:
                self.add_information('no file loaded')
        except Exception as e:
            print(e)

    # Refresh Screen-----------------------------------------
    def refresh(self):
        self.refresh_signal.emit()

    def refresh_fun(self):
        self.vtkWindow.refresh()
        # self.renderer.Render()

    def showInMessageBar(self, s):
        self.statusBar().showMessage(s)

    # Window ,show information----------------------------------------
    def show_information_window(self):
        if not self.informationWindow.isShow:
            self.informationWindow.show()
        else:
            self.informationWindow.close()

    def add_information(self, s):
        if self.informationWindow.isShow:
            try:
                self.informationWindow.append(s)
            except Exception as e:
                print(e)

    def warning_information(self, s):
        try:
            self.informationWindow.warning(s)
        except Exception as e:
            print(e)


class IpGroup(QGroupBox):
    def __init__(self):
        super().__init__()
        self.connect_ip = QLineEdit(_ip)
        self.connect_port = QLineEdit(str(_port))
        self.connect_btn = QPushButton("connect")
        ip_panel = QGridLayout()
        temp = QLabel("IP:")
        # temp.setFixedWidth(30)
        ip_panel.addWidget(temp, 0, 0)
        # ip_panel.addSpacing(1)
        # self.connect_ip.setMaximumWidth(150)
        self.connect_ip.setMaxLength(15)
        ip_panel.addWidget(self.connect_ip, 1, 0)
        temp = QLabel("port:")
        # temp.setFixedWidth(30)
        ip_panel.addWidget(temp, 0, 1)
        # ip_panel.addSpacing(1)
        # self.connect_port.setMaximumWidth(40)
        # self.connect_port.setFixedWidth(40)
        self.connect_port.setMaxLength(5)
        ip_panel.addWidget(self.connect_port, 1, 1)
        # self.connect_btn.setFixedWidth(100)
        ip_panel.addWidget(self.connect_btn, 1, 2)
        # self.connect_btn.setMaximumWidth(200)
        # ip_group = QGroupBox()  # zip all in one box
        # ip_group.setTitle("Connection")
        self.setTitle("Connection")
        # ip_group.setGeometry(QRect(0,0,500,200))
        # ip_group.setLayout(ip_panel)
        self.setLayout(ip_panel)

    def ip(self):
        return self.connect_ip.text()

    def port(self):
        return int(self.connect_port.text())

    def addr(self):
        return self.ip(), self.port()

    def connect(self, fun_connect):
        # self.connect_fun = fun
        # self.connect_btn.clicked.connect(lambda: fun('hello'))
        # addr = (self.ip(), self.port())
        self.connect_btn.clicked.connect(lambda: fun_connect(self.addr()))


def main():
    app = QApplication(sys.argv)
    MainWindow()
    sys.exit(app.exec_())



if __name__ == "__main__":
    main()
