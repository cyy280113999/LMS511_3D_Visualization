
# Contributed by Eric E Monson

import vtk


def main():
    colors = vtk.vtkNamedColors()

    # colors.SetColor('bkg', [0.2, 0.3, 0.7, 1.0])

    # create a rendering window and renderer
    ren = vtk.vtkRenderer()
    ren_win = vtk.vtkRenderWindow()
    ren_win.AddRenderer(ren)
    ren_win.SetWindowName('OrientationMarkerWidget')

    # create a renderwindowinteractor
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(ren_win)

    # cube = vtk.vtkCubeSource()
    # cube.SetXLength(200)
    # cube.SetYLength(200)
    # cube.SetZLength(200)
    # cube.Update()
    # cm = vtk.vtkPolyDataMapper()
    # cm.SetInputConnection(cube.GetOutputPort())
    # ca = vtk.vtkActor()
    # ca.SetMapper(cm)
    # ca.GetProperty().SetColor(colors.GetColor3d("BurlyWood"))
    # ca.GetProperty().EdgeVisibilityOn()
    # ca.GetProperty().SetEdgeColor(colors.GetColor3d("Red"))

    _read = vtk.vtkPLYReader()
    _read.SetFileName("teapot.ply")
    _read.Update()
    _poly_data = _read.GetOutput()
    _mapper = vtk.vtkPolyDataMapper()

    # remove color , white points
    # this change place which the mapper point to
    _filter = vtk.vtkVertexGlyphFilter()
    _filter.AddInputData(_poly_data)
    _mapper.SetInputConnection(_filter.GetOutputPort())

    # _mapper.SetInputData(_poly_data)
    _vtkActor = vtk.vtkActor()
    _vtkActor.GetProperty().SetPointSize(5)
    _vtkActor.SetMapper(_mapper)
    ren.AddActor(_vtkActor)
    # assign actor to the renderer
    # ren.AddActor(ca)
    ren.SetBackground(colors.GetColor3d('CornflowerBlue'))


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
    # use either
    axes.On()
    #axes.EnabledOn()
    #axes.InteractiveOn()


    ren.ResetCamera()


    # enable user interface interactor
    iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    iren.Initialize()
    ren_win.Render()
    #ren.GetActiveCamera().Azimuth(45)
    #ren.GetActiveCamera().Elevation(30)
    ren_win.Render()

    iren.Start()


if __name__ == '__main__':
    main()