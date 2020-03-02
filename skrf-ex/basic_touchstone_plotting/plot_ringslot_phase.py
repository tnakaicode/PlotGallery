import pylab
import skrf as rf

ring_slot = rf.Network('ring slot array measured.s1p')

pylab.figure(1)
pylab.title('WR-10 Ringslot Array, Phase')
ring_slot.plot_s_deg(m=0, n=0, color='r', markevery=5, marker='o')

pylab.figure(2)
pylab.title('WR-10 Ringslot Array, Phase-Unwrap')
ring_slot.plot_s_deg_unwrap(m=0, n=0, color='r', markevery=5, marker='o')

pylab.show()
