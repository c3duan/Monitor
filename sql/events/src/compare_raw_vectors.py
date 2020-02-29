from scipy.stats.stats import pearsonr
import mysql.connector
from data import data
from tqdm import tqdm
import pandas as pd
import numpy as np
import scipy, sys, os


DATA_OUTPUT = os.path.abspath(__file__ + '/../../data/vector/raw/raw_event_vectors.csv')
SCRIPT_OUTPUT = os.path.abspath(__file__ +  '/../../data/vector/raw/raw_event_vectors.sql')


def main():

    scipy.seterr(all='ignore')

    #################################################
    ########## CALCULATE RAW EVENT VECTORS ##########
    #################################################

    db = mysql.connector.connect(
        host="localhost",
        user="root",
        database="monitor_db",
        passwd="D@1syKn0ws"
    )

    # LOAD RAW VECTORS 
    query = "SELECT name, start, end FROM raw_vectors"
    cursor = db.cursor(buffered=True)
    cursor.execute(query)

    raw_vectors = []
    for row in cursor:
        raw_vectors.append({
            'stream_name': row[0],
            'start': row[1],
            'end': row[2]
        })

    for raw_vector in tqdm(raw_vectors, desc='Creating Raw Vectors'):

        stream_name, start, end = raw_vector['stream_name'], raw_vector['start'], raw_vector['end']
        query = "SELECT timestamp, value FROM stream_data WHERE name='%s' and timestamp>=%s and timestamp<=%s ORDER BY timestamp ASC;" % (stream_name, start, end)
        cursor.execute(query)

        vector = []
        for row in cursor:
            vector.append(row[1])

        vector = np.asarray(vector)
        raw_vector['vector'] = vector

    # LOAD EVENTS
    query = "SELECT event, stream, timeStart, timeEnd FROM event"
    cursor = db.cursor()
    cursor.execute(query)

    events = []
    for row in cursor: 
        events.append({
            'event_name': row[0],
            'stream_name': row[1],
            'start': row[2],
            'end': row[3]
        })

    all_corr_data = []
    for event in tqdm(events, desc='Comparing Events'):

        event_name, stream_name, start, end = event['event_name'], event['stream_name'], event['start'], event['end']

        query = "SELECT name, timestamp, value FROM stream_data WHERE name='%s' and timestamp >= '%s' and timestamp <= '%s' ORDER BY timestamp ASC;"  % (stream_name, start, end)
        cursor.execute(query)

        event_vector = []
        for index, row in enumerate(cursor): 
            event_vector.append(row[2])

        event_vector = np.asarray(event_vector)

        corr_data = [] 
        for raw_vector_data in tqdm(raw_vectors, desc='Comparing to Event %s' % event_name):

            rstream_name, rstart, rend, rvector = raw_vector_data['stream_name'], raw_vector_data['start'], raw_vector_data['end'], raw_vector_data['vector']

            if rvector.shape[0] > event_vector.shape[0]:
                rvector = rvector[:event_vector.shape[0]]

            if rvector.shape[0] == event_vector.shape[0]:
                corr = pearsonr(event_vector, rvector)[0]
                corr_data.append([event_name, rstream_name, rstart, rend, corr])

        corr_data = pd.DataFrame(corr_data)
        corr_data = corr_data.rename(columns={0: 'event', 1: 'stream', 2: 'start', 3: 'end', 4:'corr'})
        corr_data = corr_data.dropna(subset=['corr'])
        corr_data = corr_data.sort_values('corr', ascending=False).reset_index(drop=True)
        corr_data['rank'] = corr_data.index + 1
        corr_data = corr_data[['event', 'rank', 'stream', 'start', 'end', 'corr']]
        all_corr_data.append(corr_data.iloc[:99, ])

    all_corr_data = pd.concat(all_corr_data)
    all_corr_data.to_csv(DATA_OUTPUT, index=False, header=False)

    #######################################
    ########## CREATE SQL SCRIPT ##########
    #######################################

    sqlstr = 'USE monitor_db;\n\n'
    sqlstr += 'DROP TABLE IF EXISTS raw_event_vectors;\n\n'

    sqlstr += 'CREATE TABLE raw_event_vectors(\n'
    sqlstr += '\tevent VARCHAR(100),\n'
    sqlstr += '\trank INTEGER,\n'
    sqlstr += '\tstream VARCHAR(100),\n'
    sqlstr += '\ttimeStart INTEGER,\n'
    sqlstr += '\ttimeEnd INTEGER,\n'
    sqlstr += '\tcorrelation FLOAT\n'
    sqlstr += ');\n\n'

    sqlstr += f'LOAD DATA LOCAL INFILE "{DATA_OUTPUT}" INTO TABLE raw_event_vectors FIELDS TERMINATED BY ",";\n\n'

    with open(SCRIPT_OUTPUT, 'w') as w: w.write(sqlstr)

if __name__ == '__main__':
    main()
