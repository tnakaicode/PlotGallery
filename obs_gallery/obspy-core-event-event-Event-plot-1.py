from obspy import read_events
event = read_events("/path/to/CMTSOLUTION")[0]
event.plot()