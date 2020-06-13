from obspy import read_events
cat = read_events()
cat.plot(projection="local")