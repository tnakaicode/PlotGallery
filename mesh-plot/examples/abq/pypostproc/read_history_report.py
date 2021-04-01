import argiope as ag

class Step:
    """
    dummy step class.
    """
    duration = 1.

steps = [Step(), Step()]
         
path613 = "data/hist_abq613.hrpt"
data613 = ag.abq.pypostproc.read_history_report(path613, steps = steps, x_name = "t")


steps = [Step(), Step(), Step()]
path2018 = "data/hist_abq2018.hrpt"
data2018 = ag.abq.pypostproc.read_history_report(path2018, steps = steps, x_name = "t")

