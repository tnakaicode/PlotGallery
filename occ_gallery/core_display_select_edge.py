from OCC.Display.SimpleGui import init_display
display, start_display, add_menu, add_function_to_menu = init_display()


list_edge = []  # list of edge


def line_clicked(shp, *kwargs):
    """ This function is called whenever a line is selected
    """
    for shape in shp:  # this should be a TopoDS_Edge
        print("Edge selected: ", shape)
        e = topods_Edge(shape)
        list_edge.append(e)
        if len(list_edge) == 2:  # control edge number
            pass
            am = AIS_AngleDimension(list_edge[0], list_edge[1])
            display.Context.Display(am, True)
            list_edge.clear()


context.Display(ais_shape, True)
context.SetTransparency(ais_shape, 0, True)
owner = ais_shape.GetOwner()
display.register_select_callback(line_clicked)


start_display()


context.Display(ais_shape, True)
context.SetTransparency(ais_shape, 0, True)
owner = ais_shape.GetOwner()
display.SetSelectionModeEdge()  # switch to edge selection mode
display.register_select_callback(line_clicked)


start_display()
