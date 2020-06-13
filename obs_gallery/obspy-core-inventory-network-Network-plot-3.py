from obspy import read_inventory
net = read_inventory()[0]
net.plot(projection="local")
