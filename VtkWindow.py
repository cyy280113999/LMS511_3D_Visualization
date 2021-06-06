import numpy as np

import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PyQt5.QtWidgets import QLayout


class VtkWindow(QVTKRenderWindowInteractor):
    def __init__(self, master: QLayout):
        # QVTKRenderWindowInteractor consists of renderer renderWindow Interactor
        # self is a QVTKRenderWindowInteractor
        super().__init__()
        self.embed(master)
        # window and interactor are created from start
        self.renwin = self.GetRenderWindow()
        self.iren = self.renwin.GetInteractor()
        # you should create a render by youself
        self.renderer = vtk.vtkRenderer()
        colors = vtk.vtkNamedColors()
        self.renderer.SetBackground(colors.GetColor3d('Black'))
        self.renwin.AddRenderer(self.renderer)

        # add central central_axes
        self.central_axes = vtk.vtkAxesActor()
        transform = vtk.vtkTransform()
        transform.Translate(0.0, 0.0, 0.0)
        self.central_axes.SetUserTransform(transform)
        self.central_axes.GetXAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
        # self.central_axes.GetXAxisCaptionActor2D().GetTextActor().SetNonLinearFontScale(0.7,10)
        self.central_axes.GetYAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
        self.central_axes.GetZAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
        # (vtk.vtkTextActor.TEXT_SCALE_MODE_NONE)
        self.renderer.AddActor(self.central_axes)

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

        self.iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        self.camera = self.renderer.GetActiveCamera()
        self.iren.AddObserver("KeyPressEvent", self.keypress)
        self.renderer.ResetCamera()
        self.Initialize()

    def addActor(self, a):
        self.renderer.AddActor(a)

    def embed(self, widget: QLayout):
        widget.addWidget(self)

    def refresh(self):
        self.renwin.Render()

    def setColor(self, color):
        colors = vtk.vtkNamedColors()
        if isinstance(color, str):
            self.renderer.SetBackground(colors.GetColor3d(color))
        else:
            print("Wrong color to change!")

    # key event for w a s d movement ---------------------------
    def keypress(self, obj, event):
        # self.camera = vtk.vtkCamera()
        key = obj.GetKeySym()
        CmrPosition = self.camera.GetPosition()
        CmrFPosition = self.camera.GetFocalPoint()
        CmrDistance = self.camera.GetDistance()
        CmrDirection3 = self.camera.GetDirectionOfProjection()

        eps = 1e-10
        if CmrDirection3[1] < eps and CmrDirection3[1] > -eps \
                or CmrDirection3[0] < eps and CmrDirection3[0] > -eps:
            return
        theta = np.arctan2(CmrDirection3[1], CmrDirection3[0])

        (delta_x, delta_y) = (np.cos(theta), np.sin(theta))

        speed = 0.03 * CmrDistance

        if key == "c":
            self.camera.SetPosition((CmrPosition[0],
                                     CmrPosition[1],
                                     CmrPosition[2] - speed))
            self.camera.SetFocalPoint((CmrFPosition[0],
                                       CmrFPosition[1],
                                       CmrFPosition[2] - speed))
            self.refresh()
        elif key == "space":
            self.camera.SetPosition((CmrPosition[0],
                                     CmrPosition[1],
                                     CmrPosition[2] + speed))
            self.camera.SetFocalPoint((CmrFPosition[0],
                                       CmrFPosition[1],
                                       CmrFPosition[2] + speed))
            self.refresh()
        elif key == "w":
            self.camera.SetPosition((CmrPosition[0] + speed * delta_x,
                                     CmrPosition[1] + speed * delta_y,
                                     CmrPosition[2]))
            self.camera.SetFocalPoint((CmrFPosition[0] + speed * delta_x,
                                       CmrFPosition[1] + speed * delta_y,
                                       CmrFPosition[2]))
            self.refresh()
        elif key == "s":
            self.camera.SetPosition((CmrPosition[0] - speed * delta_x,
                                     CmrPosition[1] - speed * delta_y,
                                     CmrPosition[2]))
            self.camera.SetFocalPoint((CmrFPosition[0] - speed * delta_x,
                                       CmrFPosition[1] - speed * delta_y,
                                       CmrFPosition[2]))
            self.refresh()
        elif key == "a":
            self.camera.SetPosition((CmrPosition[0] - speed * delta_y,
                                     CmrPosition[1] + speed * delta_x,
                                     CmrPosition[2]))
            self.camera.SetFocalPoint((CmrFPosition[0] - speed * delta_y,
                                       CmrFPosition[1] + speed * delta_x,
                                       CmrFPosition[2]))
            self.refresh()
        elif key == "d":
            self.camera.SetPosition((CmrPosition[0] + speed * delta_y,
                                     CmrPosition[1] - speed * delta_x,
                                     CmrPosition[2]))
            self.camera.SetFocalPoint((CmrFPosition[0] + speed * delta_y,
                                       CmrFPosition[1] - speed * delta_x,
                                       CmrFPosition[2]))
            self.refresh()
