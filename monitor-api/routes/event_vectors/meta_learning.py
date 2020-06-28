from multiprocessing import Manager, Process
from data import data
import numpy as np
import time, sys, os, math
from db import db
import torch
from SiameseNet import model

DATA_DICT_PATH = os.path.abspath(__file__ + '/../data_dict.npy')
MODEL_PATH = os.path.abspath(__file__ + '/../rnn-siamese-model.pt')

model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device("cpu")))
torch.set_num_threads(8)

def split(data_dict, split_size):
    data = []
    timestamps = []
    streams = []
    for stream in data_dict:
        chunk = [x[1] for x in data_dict[stream]]
        time = [x[0] for x in data_dict[stream]]
        
        length = len(chunk)
        new_length = (math.ceil(length / split_size) * split_size)
        pad_size = new_length - length
        new_chunk = chunk + [0] * pad_size
        new_time = time + [0] * pad_size
        time_end = time[-1]
        
        new_chunk = np.array(new_chunk).reshape(new_length // split_size, split_size)
        
        new_time = np.array(new_time).reshape(new_length // split_size, split_size)
        time_ranges = [(t[0], t[-1]) if i != new_time.shape[0] - 1 else (t[0], time_end) \
                       for i, t in enumerate(new_time)]

        data.extend(new_chunk.tolist())
        timestamps.extend(time_ranges)
        streams.extend([stream] * (new_length // split_size))
        
    return np.array(data), np.array(timestamps), np.array(streams)

def euclidean_dist(a, b):
    return np.linalg.norm(a-b)

def csim(a, b):    
    return np.abs(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def meta_validate(o_vec, o_stream, data, time_ranges, streams):
    with torch.no_grad():
        o_output = model.forward_once(torch.FloatTensor(o_vec).view(1, -1))
        outputs =  model.forward_once(torch.FloatTensor(data))
        distances = np.array([csim(o_output, x) for x in outputs.numpy()])
        ranking = np.argsort(distances)[::-1][:200]
        
        stream_set = set([o_stream])
        results = []
        for rank in ranking:

            if streams[rank] in stream_set:
                continue

            stream_set.add(streams[rank])
            results.append(streams[rank], *time_ranges[rank], distances[rank])
            
        return results


def main():

    event = sys.argv[1]

    # Get event vector
    query = "SELECT stream, timeStart, timeEnd FROM event WHERE event='%s'" % event
    cursor = db.cursor()
    cursor.execute(query)

    for row in cursor:
        stream, start, end = row
    
    query = "SELECT timestamp, value FROM stream_data WHERE name='%s' AND TIMESTAMP >= %s AND TIMESTAMP <= %s ORDER BY TIMESTAMP DESC" % (stream, start, end)
    cursor = db.cursor()
    cursor.execute(query)

    vector = []
    for pair in cursor: 
        vector.append(pair[1])

    vector = np.array(vector)
    data_dict = np.load(DATA_DICT_PATH, allow_pickle=True).item()
    data, time_ranges, streams = split(data_dict, vector.shape[0])
    
    results = meta_validate(vector, stream, data, time_ranges, streams)
    print('%s,%s,%s' % (stream, start, end))
    for stream_name, s, e, dis in results:
        print('%s,%s,%s,%s' % (stream_name, int(s), int(e), dis))
    sys.stdout.flush()


if __name__ == '__main__':
    main()
