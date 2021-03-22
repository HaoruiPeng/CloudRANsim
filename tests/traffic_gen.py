import os
import numpy as np
import pandas as pd

deadlines = np.random.uniform(1,10,100)
ids  = np.random.randint(0,20,100)
counts = []
counter = dict.fromkeys(np.unique(ids), 0)
for i in ids:
    counter[i] += 1
    print("{}:{}".format(i, counter[i]))
    counts.append(counter[i])
arrivals = np.sort(np.random.uniform(0,11,100))
deads = arrivals + deadlines
packets = pd.DataFrame(
    {'id': ids,
     'counter': counts,
     'arrival': arrivals,
     'deadline': deadlines,
    }).to_pickle("packets.pkl")

new_packets = pd.read_pickle("packets.pkl")
print(new_packets)
