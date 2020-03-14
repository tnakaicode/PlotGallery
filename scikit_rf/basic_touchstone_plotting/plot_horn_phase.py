import pylab
import skrf as rf

horn = rf.Network('horn antenna.s1p')

pylab.figure(1)
pylab.title('WR-10 Horn Antenna, Phase')
horn.plot_s_deg(m=0, n=0, color='r', marker='o', markevery=5)

pylab.figure(2)
pylab.title('WR-10 Horn Antenna, Phase-Unwrap')
horn.plot_s_deg_unwrap(m=0, n=0, color='r', marker='o', markevery=5)

pylab.show()
