import subprocess, os
import numpy as np
from tqdm import tqdm

DATA_DICT_PATH = os.path.abspath(__file__ + "/../data_dict.npy")
EVENTS = os.path.abspath("events.npy")
UCR_DTW = os.path.abspath("trillion/Source Code/UCR_DTW")
DATA_DIR = os.path.abspath("streams")
QUERIES_DIR = os.path.abspath("queries")
R = 0.05
TOP = 5

data_dict = np.load(DATA_DICT_PATH, allow_pickle=True).item()
events = np.load(EVENTS, allow_pickle=True)
with open("DTW_validation_data.csv", "w+") as f:
        f.write("value,rank,group\n")

for query in tqdm(sorted(os.listdir(QUERIES_DIR))):
    if not query.startswith("."):
        distances = []
        group = int(query.split(".")[0][5:])
        for data in os.listdir(DATA_DIR):
            if not data.startswith("."):
                datafile = f"{DATA_DIR}/{data}"
                queryfile = f"{QUERIES_DIR}/{query}"
                M = len(events[group])
                
                stdout = subprocess.check_output([UCR_DTW, datafile, queryfile, str(M), str(R)]).decode("utf-8")
                
                lines = stdout.split("\n")
                stream = data[:-4]
                index = int(lines[1].split(" : ")[1])
                distance = float(lines[2].split(" : ")[1])
                distances.append((distance, stream, index, M))

        distances.sort(key=lambda x: x[0])
        orignal = events[group]
        with open("DTW_validation_data.csv", "a+") as f:
            for v in orignal:
                f.write(f"{v},0,{group}\n")

            for rank in range(TOP):
                distance, stream, index, M = distances[rank]
                vector = data_dict[stream][index:index+M, 1]
                for v in vector:
                    f.write(f"{v},{rank+1},{group}\n")
                