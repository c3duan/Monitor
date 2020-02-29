from tqdm import trange, tqdm
import numpy as np
import os


COMPLETE = os.path.abspath(__file__ + '/../../data/vector/hcdm_vectors_reduced.csv')
OUTPUT = os.path.abspath(__file__ + '/../../data/vector/split/hcdm_split')
VECTOR_SCRIPT = os.path.abspath(__file__ + '/../../data/vector/split/split_hcdm_vector_table.sql')
API_SCRIPT = os.path.abspath(__file__ + '/../data.py')
NUM_SPLITS = 25


def main():

    data = np.asarray(open(COMPLETE, 'r').readlines())
    data = np.array_split(data, NUM_SPLITS)
    sample = str(data[0][0]).strip().split(',')

    cols = [ 'STREAM', 'START', 'END' ]
    for i in range(len(sample) - 3): 
        cols.append('F%s' % str(i+1))

    ################################
    ########## SPLIT DATA ##########
    ################################

    for i in trange(NUM_SPLITS):
        filename, table = '%s/hcdm_vectors_split_%s.csv' % (OUTPUT, str(i+1)), data[i]

        with open(filename, 'w') as w:
            for line in table: w.write(line)

    #######################################
    ########## CREATE SQL SCRIPT ##########
    #######################################

    sqlstr = 'USE monitor_db;\n\n'
    
    for i in trange(NUM_SPLITS):

        tablename = 'hcdm_vectors_split_%s' % str(i+1)
        filename = '%s/hcdm_vectors_split_%s.csv' % (OUTPUT, str(i+1))

        sqlstr += 'DROP TABLE IF EXISTS %s;\n\n' % tablename
        sqlstr += 'CREATE TABLE %s (\n' % tablename
        sqlstr += '\t%s VARCHAR(100),\n' % cols[0]
        for col in cols[1:3]: 
            sqlstr += '\t%s INTEGER,\n' % col
        for col in cols[3:-1]: 
            sqlstr += '\t%s DOUBLE,\n' % col
        sqlstr += '\t%s DOUBLE\n' % cols[-1]
        sqlstr += ');\n\n';

        sqlstr += 'LOAD DATA LOCAL INFILE "%s" INTO TABLE %s FIELDS TERMINATED BY "," IGNORE 1 LINES;\n\n' % (filename, tablename)

    with open(VECTOR_SCRIPT, 'w') as w:
        w.write(sqlstr)

    datastr = "data = {\n"
    datastr += "\t'num_coeff': 2,\n"
    datastr += "\t'cols': ["
    for col in cols[:-1]: datastr += "'%s', " % col
    datastr += "'%s' ],\n" % cols[-1]
    datastr += "\t'tables': ["
    for i in range(NUM_SPLITS-1): datastr += "'hcdm_vectors_split_%s', " % str(i+1)
    datastr += "'hcdm_vectors_split_%s' ]\n" % str(NUM_SPLITS)
    datastr += "}"

    with open(API_SCRIPT, 'w') as w:
        w.write(datastr)


if __name__ == '__main__':
    main()
