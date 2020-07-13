from data import data
import numpy as np
import time, sys, os, math, subprocess
from db import db

DATA_DICT_PATH = os.path.abspath(__file__ + "/../data_dict.npy")
UCR_DTW = os.path.abspath(__file__ + "/../trillion/Source Code/UCR_DTW")
DATA_DIR = os.path.abspath(__file__ + "/../streams")
QUERY_FILE = os.path.abspath(__file__ + "/../queries/Query.txt")
R = 0.05
TOP = 100

def main():

    event = sys.argv[1]

    # Get event vector
    query = "SELECT stream, timeStart, timeEnd FROM event WHERE event='%s'" % event
    cursor = db.cursor()
    cursor.execute(query)

    event_stream, start, end = None, None, None
    for row in cursor:
        event_stream, start, end = row

    data_dict = np.load(DATA_DICT_PATH, allow_pickle=True).item()
    original = np.array([x[1] for x in data_dict[event_stream] if x[0] >= start and x[0] <= end])

    with open(QUERY_FILE, "w+") as f:
        for v in original:
            f.write(f"{v}\n")

    distances = []
    for data in os.listdir(DATA_DIR):
        if not data.startswith("."):
            datafile = f"{DATA_DIR}/{data}"
            M = len(original)
            
            stdout = subprocess.check_output([UCR_DTW, datafile, QUERY_FILE, str(M), str(R)]).decode("utf-8")
            
            lines = stdout.split("\n")
            stream = data[:-4]
            index = int(lines[1].split(" : ")[1])
            distance = float(lines[2].split(" : ")[1])
            distances.append((distance, stream, index, M))

    distances.sort(key=lambda x: x[0])

    print('%s,%s,%s' % (event_stream, start, end))
    for i in range(1, TOP+1):
        distance, stream, index, M = distances[i]
        max_len = len(data_dict[stream])
        end_index = min(max_len, index+M)
        time_start, time_end = data_dict[stream][index, 0], data_dict[stream][end_index, 0]
        print('%s,%s,%s,%s' % (stream, int(time_start), int(time_end), distance))
    sys.stdout.flush()


if __name__ == '__main__':
    main()
