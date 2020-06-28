import numpy as np
from db import db

filename = '../../../sql/sample_data/data.csv'

query = "SELECT DISTINCT name FROM stream_data;"
cursor = db.cursor()
cursor.execute(query)

streams = []
for row in cursor: 
    streams.append(row[0])

streams = set(streams)

meta_data_dict = {}
with open(filename, 'r') as f:
    for line in f.readlines():
        tokens = line.rstrip().split(',')
        stream, timestamp, value = tokens[0], int(tokens[1]), float(tokens[2])
        if stream in streams:
            if stream not in meta_data_dict:
                meta_data_dict[stream] = []
            meta_data_dict[stream].append((timestamp, value))

for stream in meta_data_dict:
    meta_data_dict[stream].sort(key=lambda x: x[0])
    meta_data_dict[stream] = np.array(meta_data_dict[stream])

np.save('data_dict.npy', meta_data_dict)

