import os
#import xmltodict
from OCC.Display.SimpleGui import init_display
from OCC.Core.BRepTools import breptools

# https://github.com/tpaviot/pythonocc-core/issues/1395


#display, start_display, add_menu, add_function_to_menu = init_display()
#script_dir = os.path.dirname(os.path.abspath(__file__))
#file_path = os.path.join(script_dir, 'test.xml')
#with open(file_path, 'r') as file:
#    xml_content = file.read()
#xml_dict = xmltodict.parse(xml_content[3:])
#shape_data = (xml_dict['root']['model']['shape']).replace('\r','').replace('\n','')
##readResult=breptools.Read(shape,shape_data,builder)
#shape=breptools.ReadFromString(shape_data)
#display.DisplayShape(shape, update=True)
#display.FitAll()
#display.Repaint()
#start_display()
#print('Done..')


from OCC.Core.TopTools import TopTools_FormatVersion_VERSION_1
from OCC.Core.Message import Message_ProgressRange
breptools.Write(
            my_shape,
            "the_brep_file.brep",
            True,  # export triangles
            True, # export normals
            TopTools_FormatVersion_VERSION_1,  # choss VERSION_2 or VERSION_3
            Message_ProgressRange(), # required to fit the method signature
        )