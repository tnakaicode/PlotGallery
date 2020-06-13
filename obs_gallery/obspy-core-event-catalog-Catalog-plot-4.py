from obspy import read_inventory, read_events
inv = read_inventory()
cat = read_events()
fig = inv.plot(show=False)
cat.plot(fig=fig)