import vtk

# test for teapot
# correct
def main():
    colors = vtk.vtkNamedColors()

    filename = "teapot.ply"

    reader = vtk.vtkPLYReader()
    reader.SetFileName(filename)
    reader.Update()

    polydata = reader.GetOutput()

    f = vtk.vtkVertexGlyphFilter()

    f.AddInputData(polydata)

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(f.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    renderer = vtk.vtkRenderer()
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)

    renderer.AddActor(actor)
    renderer.SetBackground(colors.GetColor3d('cobalt_green'))

    renderWindow.Render()
    renderWindowInteractor.Start()


if __name__ == '__main__':
    main()