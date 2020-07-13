from multiprocessing import Manager, Process
from data import data
import numpy as np
import time, sys, os, math
from db import db
import torch
from SiameseNet import model

DATA_DICT_PATH = os.path.abspath(__file__ + '/../data_dict.npy')
MODEL_PATH = os.path.abspath(__file__ + '/../rnn-siamese-model-v2.pt')

cos = torch.nn.CosineSimilarity(dim=0)
model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device("cuda")))


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

def meta_validate(o_vec, o_stream, data, time_ranges, streams):
    with torch.no_grad():
        model.eval()
        o_output = model.embed(torch.FloatTensor(o_vec).view(1, -1))
        outputs =  model.embed(torch.FloatTensor(data))
        distances = np.array([torch.dist(o_output, x, p=2).cpu().numpy() for x in outputs])
        ranking = np.argsort(distances)
        
        stream_set = set([o_stream])
        results = []
        for rank in ranking[:1000]:

            if streams[rank] in stream_set:
                continue

            stream_set.add(streams[rank])
            results.append((streams[rank], *time_ranges[rank], distances[rank]))
            
        return results


def main():

    event = sys.argv[1]

    # Get event vector
    query = "SELECT stream, timeStart, timeEnd FROM event WHERE event='%s'" % event
    cursor = db.cursor()
    cursor.execute(query)

    for row in cursor:
        stream, start, end = row

    data_dict = np.load(DATA_DICT_PATH, allow_pickle=True).item()
    vector = np.array([x[1] for x in data_dict[stream] if x[0] >= start and x[0] <= end])
    data, time_ranges, streams = split(data_dict, vector.shape[0])
    sample = np.array([i for i, x in enumerate(data) if x.std() > 1])
    data = data[sample]
    time_ranges = time_ranges[sample]
    streams = streams[sample]

    results = meta_validate(vector, stream, data, time_ranges, streams)
    print('%s,%s,%s' % (stream, start, end))
    for stream_name, s, e, dis in results:
        print('%s,%s,%s,%s' % (stream_name, int(s), int(e), dis))
    sys.stdout.flush()


if __name__ == '__main__':
    main()
