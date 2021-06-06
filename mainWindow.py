# sys pk
import sys
from numpy.random import rand as f_rand
from functools import partial
# third pk
from PyQt5 import QtWidgets, QtCore
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
# user pk
from VtkPointCloud import *
from InformationWindow import InformationWindow
from mySock import MySock

# Debug flags:
DebugFlag_initPoints = True
DebugFlag_ReadPly = False
DebugFlag_RoundMode = True
# Settings:
_ip = "169.254.104.114"
_port = 2111
_scan = "\x02sRN LMDscandata\x03"

Debug_Round_Period = 20  # (s)
Debug_Round_Gap = 0.02  # (s)

Debug_Round_Bottom = -0.5
Debug_Round_Top = 2.5
Debug_Round_anglemin = 0
Debug_Round_anglemax = 150


class MainWindow(QtWidgets.QMainWindow):
    Debug_info_widget_open = False
    refresh_signal = QtCore.pyqtSignal()

    later_process_signal = QtCore.pyqtSignal(int)

    def __init__(self):
        #
        super().__init__()
        # 先放置UI控件
        self.ui_init()
        # 初始化VTK窗口
        self.initScreen()
        # 初始化网络接口
        self.initSock()

        # 按钮连接最后执行
        self.initFunc()

        # Debug

        # Show
        self.showMaximized()

    def ui_init(self):
        # Create Widgets
        self.central_widget = QtWidgets.QWidget()
        self.main_layout1 = QtWidgets.QVBoxLayout()
        self.main_layout2 = QtWidgets.QHBoxLayout()
        self.top_panel = QtWidgets.QHBoxLayout()
        self.left_panel = QtWidgets.QVBoxLayout()
        self.right_panel = QtWidgets.QHBoxLayout()
        self.connect_btn = QtWidgets.QPushButton("connect")

        self.loadPoint_btn = QtWidgets.QPushButton("load")
        self.savePoint_btn = QtWidgets.QPushButton("save")
        # self.default_login_btn = QtWidgets.QPushButton("default login")
        self.read_once_btn = QtWidgets.QPushButton("read once")
        self.read_always_btn = QtWidgets.QPushButton()
        self.showInformationButton = QtWidgets.QPushButton("Debug info window")
        self.qvtkinteract = QVTKRenderWindowInteractor()

        # Button Text
        # eg:
        self.read_always_btn.Text_Off = partial(self.read_always_btn.setText, "read always")
        self.read_always_btn.Text_On = partial(self.read_always_btn.setText, "stop read")
        self.read_always_btn.Text_Off()

        # set mainFrame UI
        self.setCentralWidget(self.central_widget)
        self.setGeometry(200, 100, 1000, 800)  # this is nonsense
        self.setWindowTitle("LMS511_Connector")
        self.central_widget.setLayout(self.main_layout1)
        self.main_layout1.addLayout(self.top_panel)
        self.main_layout1.addLayout(self.main_layout2)
        self.main_layout2.addLayout(self.left_panel)
        self.main_layout2.addLayout(self.right_panel)

        self.top_panel.addWidget(self.connect_btn)
        # self.buttonpanel.addWidget(self.defaultlogin)
        self.top_panel.addWidget(self.read_once_btn)
        self.top_panel.addWidget(self.read_always_btn)

        self.top_panel.addStretch(1)
        self.top_panel.addWidget(self.loadPoint_btn)
        self.top_panel.addWidget(self.savePoint_btn)

        self.left_panel.addWidget(self.showInformationButton)

        # self.left_panel.addStretch(1)
        # points screen
        self.right_panel.addWidget(self.qvtkinteract)

        # status message
        self.statusBar().showMessage("unconnected")

        # Information Window
        self.informationWindow = InformationWindow()

    def initFunc(self):

        self.connect_btn.clicked.connect(self.mysock.connect)
        self.read_once_btn.clicked.connect(self.mysock.readonce)
        self.read_always_btn.clicked.connect(self.mysock.readalways)
        self.showInformationButton.clicked.connect(self.show_information_window)
        self.savePoint_btn.clicked.connect(self.savePointCloud)
        self.loadPoint_btn.clicked.connect(self.loadPointCloud)

        self.refresh_signal.connect(self.refresh_fun)

    def initScreen(self):
        if DebugFlag_RoundMode == True:
            self.pointCloud = VtkPointCloud(zMin=Debug_Round_Bottom, zMax=Debug_Round_Top)
        else:
            self.pointCloud = VtkPointCloud()

        colors = vtk.vtkNamedColors()
        self.iren = self.qvtkinteract.GetRenderWindow().GetInteractor()
        #

        # display

        self.renderer = vtk.vtkRenderer()
        self.pointCloud.setPointSize(3)
        self.renderer.AddActor(self.pointCloud.getActor())
        self.renderer.SetBackground(colors.GetColor3d('black'))

        # add central central_axes
        self.central_axes = vtk.vtkAxesActor()
        transform = vtk.vtkTransform()
        transform.Translate(0.0, 0.0, 0.0)
        self.central_axes.SetUserTransform(transform)
        self.central_axes.GetXAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
        #self.central_axes.GetXAxisCaptionActor2D().GetTextActor().SetNonLinearFontScale(0.7,10)
        self.central_axes.GetYAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
        self.central_axes.GetZAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
            #(vtk.vtkTextActor.TEXT_SCALE_MODE_NONE)
        self.renderer.AddActor(self.central_axes)
        #
        self.iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        self.qvtkinteract.GetRenderWindow().AddRenderer(self.renderer)

        # Add axes here success!
        # Add axes
        axes_actor = vtk.vtkAnnotatedCubeActor()
        axes_actor.SetFaceTextScale(0.2)
        axes_actor.SetXPlusFaceText('Left')
        axes_actor.SetXMinusFaceText('Right')
        axes_actor.SetYMinusFaceText('Back')
        axes_actor.SetYPlusFaceText('Front')
        axes_actor.SetZMinusFaceText('Bottom')
        axes_actor.SetZPlusFaceText('Top')
        axes_actor.GetTextEdgesProperty().SetColor(colors.GetColor3d("Green"))
        axes_actor.GetTextEdgesProperty().SetLineWidth(1)
        axes_actor.GetCubeProperty().SetColor(colors.GetColor3d("Blue"))
        # # this bug happened when widget defines not in 'self.' type
        #  maybe when function finished ,the widget released.
        self.axes = vtk.vtkOrientationMarkerWidget()
        self.axes.SetOrientationMarker(axes_actor)
        self.axes.SetInteractor(self.iren)
        self.axes.EnabledOn()
        self.axes.InteractiveOn()

        # camera
        self.renderer.ResetCamera()

        self.qvtkinteract.Initialize()

    def initSock(self):
        self.mysock = MySock(self)

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

    # Debug
    # Add Points----------------------------------
    def Debug_initPoints(self):
        self.D_APBtn = QtWidgets.QPushButton("Add Point")
        self.left_panel.addWidget(self.D_APBtn)
        self.D_APBtn.clicked.connect(self.Debug_addPoints)
        for kkkk in range(1000):
            point = 20 * (f_rand(3) - 0.5)
            self.pointCloud.addPoint(point)
        for kkkk in range(10):
            self.pointCloud.addPoint(0.2 * (f_rand(3) - 0.5))

    def Debug_addPoints(self):
        point = 20 * (f_rand(3) - 0.5)
        self.pointCloud.addPoint(point)
        self.qvtkinteract.GetRenderWindow().Render()

    # Round Scan Mode-------------------------------------------
    def Debug_initRoundMode(self):
        self.RoundModeBtn = QtWidgets.QPushButton("Round Scan")
        self.left_panel.addWidget(self.RoundModeBtn)
        self.RoundModeBtn.clicked.connect(
            lambda: self.mysock.round_read(Debug_Round_Period, Debug_Round_Gap))

        self.angle_change_btn = QtWidgets.QPushButton("Change Angle Interval")
        self.left_panel.addWidget(self.angle_change_btn)
        self.angle_change_btn.clicked.connect(
            lambda: self.mysock.angle_interval(Debug_Round_anglemin, Debug_Round_anglemax))

    # save point cloud-------------------------------------
    def savePointCloud(self):
        # import os
        # cwd = os.getcwd()
        # filename = QtWidgets.QFileDialog.getSaveFileName(self,directory=)
        filename_long, f_type = QtWidgets.QFileDialog.getSaveFileName(self,
                               caption="保存点云", filter="PLY Files (*.ply);;STL Files (*.stl)")
        filename = filename_long.split('/')[-1]
        print(filename, f_type, type(f_type))
        if filename :
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
        try :
            filename_long, f_type = QtWidgets.QFileDialog.getOpenFileName(self,
                                                                     caption="读取点云", filter="PLY Files (*.ply)")
            filename = filename_long.split('/')[-1]
            if filename:
                try:
                    self.pointCloud.clearPoints()
                    reader = vtk.vtkPLYReader()
                    reader.SetFileName(filename)
                    reader.Update()
                    polydata = reader.GetOutput()
                    self.pointCloud.setOutPoly(polydata)
                    self.refresh()
                except Exception as e:
                    print(e)

            else:
                print('no file loaded')
        except Exception as e:
            print(e)

    # Refresh Screen-----------------------------------------
    def refresh(self):
        self.refresh_signal.emit()

    def refresh_fun(self):
        self.qvtkinteract.GetRenderWindow().Render()
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


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()

    # Debug
    if DebugFlag_initPoints == True:
        window.Debug_initPoints()

    if DebugFlag_RoundMode == True:
        window.Debug_initRoundMode()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()


