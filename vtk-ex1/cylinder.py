import vtk

# create cylinder
cylinder = vtk.vtkCylinderSource()
cylinder.SetRadius(2.5)
cylinder.SetHeight(5.0)
cylinder.SetResolution(20)

# mapper
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(cylinder.GetOutputPort())

# actor
actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.RotateX(30.0)
actor.RotateY(-45.0)

# create a rendering window and renderer
ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)

# create a renderwindowinteractor
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

# assign actor to the renderer
ren.AddActor(actor)
ren.SetBackground(0.2, 0.2, 0.5)
renWin.SetSize(500, 500)

# enable user interface interactor
iren.Initialize()
renWin.Render()
iren.Start()
