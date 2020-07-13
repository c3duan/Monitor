from db import db
from tqdm import tqdm
from SiameseNet import model
import numpy as np
import os, math
import torch

DATA_DICT_PATH = os.path.abspath(__file__ + '/../data_dict.npy')
data_dict = np.load(DATA_DICT_PATH, allow_pickle=True).item()

MODEL_PATH = os.path.abspath(__file__ + '/../rnn-siamese-model.pt')
cos = torch.nn.CosineSimilarity(dim=0)
model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device("cuda")))

def slide_window(data_dict, window_size):
    data = []
    for stream in data_dict:
        chunk = data_dict[stream]
        for i in range(0, chunk.shape[0] - window_size, math.floor(window_size / 3)):
            datum = chunk[i:i+window_size, 1]
            data.append(datum)
                
    return np.array(data)

def save_validation(o_vec, data, group, top=5):
    with torch.no_grad():
        model.eval()
        o_output = model.embed(torch.FloatTensor(o_vec).view(1, -1))
        outputs =  model.embed(torch.FloatTensor(data))
        distances = np.array([torch.dist(o_output, x, p=2).cpu().numpy() for x in outputs])
        ranking = np.argsort(distances)
        
        with open("validation_data_v3.csv", "a+") as f:
            for v in o_vec:
                f.write(f"{v},0,{group}\n")

            for i in range(top):
                rank = ranking[i]
                vector = data[rank]
                for v in vector:
                    f.write(f"{v},{i+1},{group}\n")
            
            
            
# Get event vector
query = "SELECT stream, timeStart, timeEnd FROM event"
cursor = db.cursor()
cursor.execute(query)

with open("validation_data_v3.csv", "w+") as f:
    f.write('value,rank,group\n')

for i, row in enumerate(tqdm(cursor)):
    stream, start, end = row
    vector = np.array([x[1] for x in data_dict[stream] if x[0] >= start and x[0] <= end])

    data = slide_window(data_dict, vector.shape[0])
    sample = np.array([i for i, x in enumerate(data) if x.std() > 1])
    data = data[sample]

    save_validation(vector, data, i)
