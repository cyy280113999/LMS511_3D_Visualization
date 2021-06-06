import sys
from PyQt5 import (QtWidgets, QtCore)
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

class SimpleView(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__()
        self.setWindowTitle("vtk_qt")
        self.resize(603, 553)
        self.gridlayout = QtWidgets.QGridLayout(self)
        self.vtkWidget = QVTKRenderWindowInteractor(self)
        self.gridlayout.addWidget(self.vtkWidget, 0, 0, 1, 1)



        self.ren = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()

        # Create source
        source = vtk.vtkCubeSource()
        source.SetCenter(0, 0, 0)

        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(source.GetOutputPort())

        # Create an actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        self.ren.AddActor(actor)


        self.iren.Initialize()  # Need this line to actually show the render inside Qt


        self.show()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = SimpleView()

    sys.exit(app.exec_())
