import skrf as rf
import matplotlib.pyplot as plt

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

cir.plot_graph(network_labels=True, network_fontsize=15,
               port_labels=True, port_fontsize=15,
               edge_labels=True, edge_fontsize=10)


# getting the resulting Network from the 'network' parameter:
ntw = cir.network
print(ntw)


# piece of transmission line and series impedance
trans_line = tline_media.line(theta, unit='deg', name='trans_line')
load = tline_media.resistor(Z_L, name='delay_load')
# ground network (short)
ground = rf.Circuit.Ground(freq, name='ground')

# connexion list
cnx = [
    [(port1, 0), (trans_line, 0)],
    [(trans_line, 1), (load, 0)],
    [(load, 1), (ground, 0)]
]
# building the circuit
cir = rf.Circuit(cnx)

cir.plot_graph(network_labels=True, network_fontsize=15,
               port_labels=True, port_fontsize=15,
               edge_labels=True, edge_fontsize=10)


# the result if the same :
ntw = cir.network
print(ntw)
print(cir.network.s[0])


freq = rf.Frequency(start=0.1, stop=10, unit='GHz', npoints=1001)
tl_media = rf.DefinedGammaZ0(freq, z0=50, gamma=1j * freq.w / rf.c)
C1 = tl_media.capacitor(3.222e-12, name='C1')
C2 = tl_media.capacitor(82.25e-15, name='C2')
C3 = tl_media.capacitor(3.222e-12, name='C3')
L2 = tl_media.inductor(8.893e-9, name='L2')
RL = tl_media.resistor(50, name='RL')
gnd = rf.Circuit.Ground(freq, name='gnd')
port1 = rf.Circuit.Port(freq, name='port1', z0=50)
port2 = rf.Circuit.Port(freq, name='port2', z0=50)

cnx = [
    [(port1, 0), (C1, 0), (L2, 0), (C2, 0)],
    [(L2, 1), (C2, 1), (C3, 0), (port2, 0)],
    [(gnd, 0), (C1, 1), (C3, 1)],
]
cir = rf.Circuit(cnx)
ntw = cir.network

cir.plot_graph(network_labels=True, network_fontsize=15,
               port_labels=True, port_fontsize=15,
               edge_labels=True, edge_fontsize=10)
plt.figure()
ntw.plot_s_db(m=0, n=0, lw=2, logx=True)
ntw.plot_s_db(m=1, n=0, lw=2, logx=True)

print(ntw)
print(cir.network.s[0])
plt.show()
