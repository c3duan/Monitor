from data import data
import numpy as np
import sys
from db import db


def csim(a, b): 
   
    return np.abs(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def main():

    event = sys.argv[1]
    query = "SELECT * FROM event WHERE event='%s'" % event
    cursor = db.cursor()
    cursor.execute(query)

    for row in cursor: 
        event, stream, start, end = row[0], row[1], row[2], row[3]
        vector = np.asarray(row[4:])

    query = "SELECT "
    for col in data['cols'][:-1]: 
        query += "%s, " % col
    query += "%s " % data['cols'][-1]
    query += "FROM hcdm_vectors"
    
    cursor = db.cursor()
    cursor.execute(query)

    results = {}
    for row in cursor:
        key = (row[0], row[1], row[2])
        mvector = np.asarray(row[3:])
        sim = csim(vector, mvector)
        results[key] = sim

    results = sorted(results.items(), key=lambda x: x[1], reverse=True)
    final = {} 

    for item in results:
        nstream, nstart, nend = item[0][0], item[0][1], item[0][2]

        if nstream not in final and nstream != stream:
            final[nstream] = (nstart, nend, item[1])

    final = sorted(final.items(), key=lambda x: x[1][2], reverse=True)
    print('%s,%s,%s' % (stream, start, end))
    for i in range(len(final)): 
        print('%s,%s,%s,%s' % (final[i][0], final[i][1][0], final[i][1][1], final[i][1][2]))
    sys.stdout.flush()


if __name__ == '__main__':
    main()
