import skrf as rf

# connexions = [
#     [(port1, 0), (network1, 0), (network4, 0)],
#     [(network1, 1), (network2, 0), (network5, 0)],
#     [(network1, 2), (network3, 0)],
#     [(network2, 1), (network3, 1)],
#     [(network2, 2), (port2, 0)],
#     [(network5, 1), (ground1, 0)],
#     [(network5, 2), (open1, 0)]
# ]
#
Z_0 = 50
Z_L = 75
theta = 0

# the necessary Frequency description
freq = rf.Frequency(start=1, stop=2, unit='GHz', npoints=3)

# The combination of a transmission line + a load can be created
# using the convenience delay_load method
# important: all the Network must have the parameter "name" defined
tline_media = rf.DefinedGammaZ0(freq, z0=Z_0)
delay_load = tline_media.delay_load(rf.zl_2_Gamma0(
    Z_0, Z_L), theta, unit='deg', name='delay_load')

# the input port of the circuit is defined with the Circuit.Port method
port1 = rf.Circuit.Port(freq, 'port1', z0=Z_0)

# connexion list
cnx = [
    [(port1, 0), (delay_load, 0)]
]
# building the circuit
cir = rf.Circuit(cnx)

# getting the resulting Network from the 'network' parameter:
ntw = cir.network
print(ntw)

cir.plot_graph()

import matplotlib.pyplot as plt
plt.show()
