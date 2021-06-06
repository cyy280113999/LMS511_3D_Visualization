
import vtk
from vtk import vtkInteractorStyleTrackball

def main():
    colors = vtk.vtkNamedColors()
    # print(colors.GetColorNames())
    ren = vtk.vtkRenderer()
    ren_win = vtk.vtkRenderWindow()
    ren_win.AddRenderer(ren)
    ren_win.SetWindowName('OrientationMarkerWidget')
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(ren_win)
    ren.SetBackground(colors.GetColor3d('black'))

    _read = vtk.vtkPLYReader()
    _read.SetFileName("teapot.ply")
    _read.Update()
    _poly_data = _read.GetOutput()
    _mapper = vtk.vtkPolyDataMapper()
    _filter = vtk.vtkVertexGlyphFilter()
    _filter.AddInputData(_poly_data)
    _mapper.SetInputConnection(_filter.GetOutputPort())

    _vtkActor = vtk.vtkActor()
    _vtkActor.GetProperty().SetPointSize(3)
    _vtkActor.SetMapper(_mapper)
    ren.AddActor(_vtkActor)



    axes_actor = vtk.vtkAnnotatedCubeActor()
    axes_actor.SetFaceTextScale(0.2)
    axes_actor.SetXPlusFaceText('Left')
    axes_actor.SetXMinusFaceText('Right')
    axes_actor.SetYMinusFaceText('Back')
    axes_actor.SetYPlusFaceText('Front')
    axes_actor.SetZMinusFaceText('Botton')
    axes_actor.SetZPlusFaceText('Top')
    axes_actor.GetTextEdgesProperty().SetColor(colors.GetColor3d("Green"))
    axes_actor.GetTextEdgesProperty().SetLineWidth(1)
    axes_actor.GetCubeProperty().SetColor(colors.GetColor3d("Blue"))
    axes = vtk.vtkOrientationMarkerWidget()
    axes.SetOrientationMarker(axes_actor)
    axes.SetInteractor(iren)
    axes.On()

    ren.ResetCamera()
    iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    iren.Initialize()
    iren.Start()


if __name__ == '__main__':
    main()