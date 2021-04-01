# -*- coding: mbcs -*-
# Do not delete the following import lines
from abaqus import *
from abaqusConstants import *
import visualization
import xyPlot
import displayGroupOdbToolset as dgo
import __main__
from argiope.abq.abqpostproc import write_xy_report, write_field_report

path = 'indentation_demo.odb'
o1 = session.openOdb(name = path)
session.viewports['Viewport: 1'].setValues(displayedObject=o1)
odb = session.odbs[path]

# XY DATA
write_xy_report(odb, "history.rpt", tags = (
    'Contact pressure: CPRESS   ASSEMBLY_I_SAMPLE_SURFACE/ASSEMBLY_I_INDENTER_SURFACE_FACES PI: I_SAMPLE Node 1',
    'Contact pressure: CPRESS   ASSEMBLY_I_SAMPLE_SURFACE/ASSEMBLY_I_INDENTER_SURFACE_FACES PI: I_SAMPLE Node 4'),
    columns = ("CPRESS_n1", "CPRESS_n4"),
    steps = ('LOADING1', 'LOADING2'))

variable = (('S', INTEGRATION_POINT, ((COMPONENT, 
        'S11'), (COMPONENT, 'S22'), (COMPONENT, 'S33'), (COMPONENT, 'S12'), )), )

write_field_report(odb, 
                   path = "S.rpt", 
                   variable = variable,
                   instance = 'I_SAMPLE', 
                   output_position = NODAL, 
                   step = -1 , 
                   frame = -1)

