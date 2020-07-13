import numpy as np
from db import db
from tqdm import tqdm
import os

DATA = os.path.abspath('../../../sql/sample_data/data.csv')
EVENTS = os.path.abspath('events.npy')
STREAMS_DIR = os.path.abspath('streams')
QUERIES_DIR = os.path.abspath('queries')

events = np.load(EVENTS, allow_pickle=True)
query = "SELECT DISTINCT name FROM stream_data;"
cursor = db.cursor()
cursor.execute(query)

streams = []
for row in cursor: 
    streams.append(row[0])

streams = set(streams)

meta_data_dict = {}
with open(DATA, 'r') as f:
    for line in tqdm(f.readlines()):
        tokens = line.rstrip().split(',')
        stream, timestamp, value = tokens[0], int(tokens[1]), float(tokens[2])
        if stream in streams:
            if stream not in meta_data_dict:
                meta_data_dict[stream] = []
            meta_data_dict[stream].append((timestamp, value))

for i, stream in enumerate(tqdm(meta_data_dict)):
    meta_data_dict[stream].sort(key=lambda x: x[0])
    with open(f"{STREAMS_DIR}/{stream}.txt", "w") as f:
        for v in meta_data_dict[stream]:
            f.write(f"{v[1]}\n")
    meta_data_dict[stream] = np.array(meta_data_dict[stream])

for i, event in enumerate(tqdm(events)):
    with open(f"{QUERIES_DIR}/Query{i}.txt", "w") as f:
        for v in event:
            f.write(f"{v}\n")

np.save('data_dict.npy', meta_data_dict)

