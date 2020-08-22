"""
================================================================================
Schedule tasks
================================================================================

Schedule task at different time interval.

"""

import matplotlib.pyplot as plt
import freshkiss3d as fk

def run(scheduler, text):
    global yplot
    simutime = fk.SimuTime(final_time=5.)
    simutime.time_delta = 5./35.
    plt.plot([simutime.time,], [yplot,], 'bx')
    if scheduler.now(simutime):
        plt.plot([simutime.time], [yplot], 'ro')
    while not simutime.is_finished:
        simutime.increment()
        plt.plot([simutime.time,], [yplot,], 'bx')
        if scheduler.now(simutime):
            plt.plot([simutime.time], [yplot], 'ro')
    plt.text(0., yplot+0.25, text)
    yplot -= 1

yplot = 6

run(fk.schedules(time_delta=1.5), 'Every 1.5 seconds')
run(fk.schedules(iteration_delta=5), 'Every 5 time iterations')
run(fk.schedules(times=[0.5, 1., 4.5, 5.]), 'At given times')
run(fk.schedules(iterations=[10, 12, 14, 16]), 'At given time iterations')
run(fk.schedules(count=4), '4 equaly time-separated')
run(fk.schedules(never=True), 'Never')
run(fk.schedules(always=True), 'Always')

plt.xlim(-0.5, 5.5)
plt.ylim(-0.5, 7)
plt.grid()
plt.show()
