# -*- coding: mbcs -*-
# Do not delete the following import lines
from abaqus import *
from abaqusConstants import *
import __main__

def Macro1():
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    leaf = dgo.LeafFromPartInstance(partInstanceName=('I_SAMPLE', ))
    session.viewports['Viewport: 1'].odbDisplay.displayGroup.intersect(leaf=leaf)
    leaf = dgo.LeafFromPartInstance(partInstanceName=('I_SAMPLE', ))
    session.viewports['Viewport: 1'].odbDisplay.displayGroup.replace(leaf=leaf)
    leaf = dgo.LeafFromPartInstance(partInstanceName=('I_INDENTER', ))
    session.viewports['Viewport: 1'].odbDisplay.displayGroup.replace(leaf=leaf)
    leaf = dgo.LeafFromPartInstance(partInstanceName=('I_SAMPLE', ))
    session.viewports['Viewport: 1'].odbDisplay.displayGroup.replace(leaf=leaf)


def Macro2():
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    odb = session.odbs['/home/lcharleux/Documents/Programmation/Python/Modules/argiope/doc/abq/abqpostproc/workdir/indentation_demo.odb']
    xy_result = session.XYDataFromHistory(name='XYData-1', odb=odb, 
        outputVariableName='Coordinates: COOR2 PI: I_SAMPLE Node 74 in NSET SURFACE', 
        steps=('LOADING1', 'LOADING2', ), )
    c1 = session.Curve(xyData=xy_result)
    xyp = session.XYPlot('XYPlot-1')
    chartName = xyp.charts.keys()[0]
    chart = xyp.charts[chartName]
    chart.setValues(curvesToPlot=(c1, ), )
    session.viewports['Viewport: 1'].setValues(displayedObject=xyp)
    x0 = session.xyDataObjects['XYData-1']
    session.writeXYReport(fileName='abaqus.rpt', xyData=(x0, ))


def Macro3():
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    leaf = dgo.LeafFromPartInstance(partInstanceName=('I_INDENTER', ))
    session.viewports['Viewport: 1'].odbDisplay.displayGroup.add(leaf=leaf)
    odb = session.odbs['/home/lcharleux/Documents/Programmation/Python/Modules/argiope/doc/abq/abqpostproc/workdir/indentation_demo.odb']
    session.XYDataFromHistory(name='XYData-2', odb=odb, 
        outputVariableName='External work: ALLWK for Whole Model', steps=(
        'LOADING1', 'LOADING2', ), )
    session.XYDataFromHistory(name='XYData-3', odb=odb, 
        outputVariableName='Frictional dissipation: ALLFD for Whole Model', 
        steps=('LOADING1', 'LOADING2', ), )
    session.XYDataFromHistory(name='XYData-4', odb=odb, 
        outputVariableName='Plastic dissipation: ALLPD PI: I_SAMPLE in ELSET ALL_ELEMENTS', 
        steps=('LOADING1', 'LOADING2', ), )
    session.XYDataFromHistory(name='XYData-5', odb=odb, 
        outputVariableName='Reaction force: RF2 PI: I_INDENTER Node 296 in NSET REF_NODE', 
        steps=('LOADING1', 'LOADING2', ), )
    session.XYDataFromHistory(name='XYData-6', odb=odb, 
        outputVariableName='Spatial displacement: U2 PI: I_INDENTER Node 73 in NSET TIP_NODE', 
        steps=('LOADING1', 'LOADING2', ), )
    session.XYDataFromHistory(name='XYData-7', odb=odb, 
        outputVariableName='Spatial displacement: U2 PI: I_INDENTER Node 296 in NSET REF_NODE', 
        steps=('LOADING1', 'LOADING2', ), )
    session.XYDataFromHistory(name='XYData-8', odb=odb, 
        outputVariableName='Strain energy: ALLSE PI: I_INDENTER in ELSET ALL_ELEMENTS', 
        steps=('LOADING1', 'LOADING2', ), )
    session.XYDataFromHistory(name='XYData-9', odb=odb, 
        outputVariableName='Strain energy: ALLSE PI: I_SAMPLE in ELSET ALL_ELEMENTS', 
        steps=('LOADING1', 'LOADING2', ), )


def Macro4():
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    pass


def Macro5():
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    odb = session.odbs['/home/lcharleux/Documents/Programmation/Python/Modules/argiope/doc/abq/abqpostproc/workdir/indentation_demo.odb']
    session.XYDataFromHistory(name='XYData-1', odb=odb, 
        outputVariableName='External work: ALLWK for Whole Model', steps=(
        'LOADING1', 'LOADING2', ), useStepTime=True, )
    session.XYDataFromHistory(name='XYData-2', odb=odb, 
        outputVariableName='Frictional dissipation: ALLFD for Whole Model', 
        steps=('LOADING1', 'LOADING2', ), useStepTime=True, )
    session.XYDataFromHistory(name='XYData-3', odb=odb, 
        outputVariableName='Plastic dissipation: ALLPD PI: I_SAMPLE in ELSET ALL_ELEMENTS', 
        steps=('LOADING1', 'LOADING2', ), useStepTime=True, )
    session.XYDataFromHistory(name='XYData-4', odb=odb, 
        outputVariableName='Reaction force: RF2 PI: I_INDENTER Node 296 in NSET REF_NODE', 
        steps=('LOADING1', 'LOADING2', ), useStepTime=True, )
    session.XYDataFromHistory(name='XYData-5', odb=odb, 
        outputVariableName='Spatial displacement: U2 PI: I_INDENTER Node 73 in NSET TIP_NODE', 
        steps=('LOADING1', 'LOADING2', ), useStepTime=True, )
    session.XYDataFromHistory(name='XYData-6', odb=odb, 
        outputVariableName='Spatial displacement: U2 PI: I_INDENTER Node 296 in NSET REF_NODE', 
        steps=('LOADING1', 'LOADING2', ), useStepTime=True, )
    session.XYDataFromHistory(name='XYData-7', odb=odb, 
        outputVariableName='Strain energy: ALLSE PI: I_INDENTER in ELSET ALL_ELEMENTS', 
        steps=('LOADING1', 'LOADING2', ), useStepTime=True, )
    session.XYDataFromHistory(name='XYData-8', odb=odb, 
        outputVariableName='Strain energy: ALLSE PI: I_SAMPLE in ELSET ALL_ELEMENTS', 
        steps=('LOADING1', 'LOADING2', ), useStepTime=True, )
    x0 = session.xyDataObjects['XYData-2']
    x1 = session.xyDataObjects['XYData-3']
    x2 = session.xyDataObjects['XYData-4']
    x3 = session.xyDataObjects['XYData-5']
    x4 = session.xyDataObjects['XYData-6']
    x5 = session.xyDataObjects['XYData-7']
    x6 = session.xyDataObjects['XYData-8']
    session.writeXYReport(fileName='abaqus.rpt', xyData=(x0, x1, x2, x3, x4, x5, 
        x6))


