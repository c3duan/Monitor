from tqdm import tqdm
import pandas as pd
import numpy as np
import os


SPLIT_DATA = os.path.abspath(__file__ + '/../../data/vector/split/stream_split')
DATA_OUTPUT = os.path.abspath(__file__ + '/../../data/vector/raw/raw_vectors.csv')
SCRIPT_OUTPUT = os.path.abspath(__file__ + '/../../data/vector/raw/raw_vectors.sql')


def create_subsets(data, subset_length, step_size):

    if data.shape[0] >= subset_length:

        data = data[int(data.shape[0] - np.floor(data.shape[0]/subset_length)*subset_length):]
        start_index, end_index = 0, subset_length

        subsets = []
        while end_index <= data.shape[0]:
            subsets.append(data[start_index:end_index])
            start_index += step_size
            end_index += step_size

        return subsets

    else:

        return None


def main():

    streams = [p for p in os.listdir(SPLIT_DATA) if not p.startswith('.')]

    ####################################
    ########## CREATE VECTORS ##########
    ####################################

    subset_data = []
    for stream in tqdm(streams):

        filename = '%s/%s' % (SPLIT_DATA, stream)
        streamname = stream.split('.csv')[0]
        
        data = open(filename).readlines()
        data = np.asarray([(float(line.strip().split(',')[0]), float(line.strip().split(',')[1])) for line in open(filename).readlines()])

        subsets = create_subsets(data, 500, 100)

        if subsets:
            for index, subset in enumerate(subsets):
                start, end = subset[:, 0][0], subset[:, 0][-1]
                subset_data.append([streamname, start, end])
    

    subset_data = pd.DataFrame(subset_data)
    subset_data = subset_data.rename(columns={0: 'name', 1: 'start', 2: 'end'})
    subset_data[['start', 'end']] = subset_data[['start', 'end']].astype(int)
    subset_data.to_csv(DATA_OUTPUT, index=False, header=False)

    #######################################
    ########## CREATE SQL SCRIPT ##########
    #######################################

    sqlstr = 'USE monitor_db;\n\n'
    sqlstr += 'DROP TABLE IF EXISTS raw_vectors;\n\n'

    sqlstr += 'CREATE TABLE raw_vectors(\n'
    sqlstr += '\tname VARCHAR(100),\n'
    sqlstr += '\tstart INTEGER,\n'
    sqlstr += '\tend INTEGER\n'
    sqlstr += ');\n\n'

    sqlstr += 'LOAD DATA LOCAL INFILE "' + os.path.abspath(__file__ + '/../../data/vector/raw_vectors.csv') + '" INTO TABLE raw_vectors FIELDS TERMINATED BY ",";\n\n'

    with open(SCRIPT_OUTPUT, 'w') as w: w.write(sqlstr)


if __name__ == '__main__':
    main()
