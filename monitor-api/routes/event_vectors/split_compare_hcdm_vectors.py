from multiprocessing import Manager, Process
from data import data
import numpy as np
import time, sys
from db import db


def csim(a, b): 
   
    return np.abs(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def compare(vector, table, result_list):

    query = "SELECT "
    for col in data['cols'][:-1]: 
        query += "%s, " % col
    
    query += "%s " % data['cols'][-1]
    query += "FROM %s" % table
    
    cursor = db.cursor()
    cursor.execute(query)
    results = [] 
    for row in cursor:
        mvector = np.asarray(row[3:])
        sim = csim(vector, mvector)
        results.append((row[0], row[1], row[2], sim))

    result_list.append(results)


def main():

    event = sys.argv[1]

    # Get event vector
    query = "SELECT * FROM event WHERE event='%s'" % event
    cursor = db.cursor()
    cursor.execute(query)

    vector, stream, start, end = None, None, None, None
    for row in cursor: 
        event, stream, start, end = row[0], row[1], row[2], row[3]
        vector = np.asarray(row[4:])

    manager = Manager()
    result_list = manager.list()

    jobs = []
    for table in data['tables']:
        p = Process(target=compare, args=(vector, table, result_list))
        jobs.append(p)
        p.start()

    for job in jobs: 
        job.join()

    complete = []
    for result in result_list:
        for group in result:
            complete.append(group)

    complete = sorted(complete, key=lambda x: x[-1], reverse=True) 
    final = {}

    for item in complete:
        nstream, nstart, nend = item[0], item[1], item[2]

        if nstream not in final and nstream != stream:
            final[nstream] = (nstart, nend, item[3])

    final = sorted(final.items(), key=lambda x: x[1][2], reverse=True)
    #houses = set([str(i) for i in range(1, 23)] + ['house1', 'house4', 'house6'] + ['House' + str(i) for i in range(1, 22)])
    print('%s,%s,%s' % (stream, start, end))
    for item in final[:100]: 
        #if item[0] in houses:
        print('%s,%s,%s,%s' % (item[0], item[1][0], item[1][1], item[1][2]))
    sys.stdout.flush()


if __name__ == '__main__':
    main()
