from sklearn.preprocessing import Normalizer
from collections import Counter, defaultdict
from sklearn.externals import joblib
from multiprocessing import Pool
from tqdm import tqdm
import glob, pdb, os
import numpy as np
import scipy as sp


# INPUT DATA
SPLIT_DATA = os.path.abspath(__file__ + '/../../data/vector/split/stream_split')


##########
# OUTPUT #
##########

# OUTPUT DATA
OUTPUT = os.path.abspath(__file__ + '/../../data/vector/hcdm_vectors.csv')
NORMALIZER_PATH = os.path.abspath(__file__ + '/../../src/normalizer.save')

# SQL SCRIPT OUTPUTS
VECTOR_SCRIPT = os.path.abspath(__file__ + '/../../data/vector/hcdm_vector_table.sql')
EVENT_SCRIPT = os.path.abspath(__file__ + '/../../data/vector/event_table.sql')
API_SCRIPT = os.path.abspath(__file__ + '/../data.py')


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


class data_feature_extractor():

    def __init__(self, X):
        self.columns = [ 'min', 'median', 'mean', 'max', 'std', 'skewness', 'kurtosis', 'entropy', 'mode', 'slope' ]
        self.functions = [ 'getF_2019_Pandey_single', 'getF_2019_Pandey_split' ]
        self.X = np.asarray(X)


    def getF_2019_Pandey(self, X):
        N, D = X.shape
        dim = 10 
        F = np.zeros([N, dim])

        F[:, 0] = np.min(X, 1)
        F[:, 1] = np.median(X, 1)
        F[:, 2] = np.mean(X, 1)
        F[:, 3] = np.max(X, 1)
        F[:, 4] = np.std(X, 1)
        F[:, 5] = sp.stats.skew(X, 1)
        F[:, 6] = sp.stats.kurtosis(X, 1)
        
        # digitize the data for the calculation of entropy if it only contains less than 100 discreate values
        XX = np.zeros(X.shape)
        bins = 100

        for i in range(X.shape[0]):
            if len(np.unique(X[i,:])) < bins:
                XX[i,:] = X[i,:]
            else:
                XX[i,:] = np.digitize(X[i,:], np.linspace(min(X[i,:]), max(X[i,:]), num=bins))        

        F[:, 7] = sp.stats.entropy(XX.T)
        F[:, 8] = sp.stats.mode(X[1], axis=None)
        F[:, 9] = np.polyfit(X[0], X[1], 1)[0]

        # check illegal features nan/inf
        F[np.isnan(F)] = 0
        F[np.isinf(F)] = 0

        return F


    def getF_2019_Pandey_single(self):
        return self.getF_2019_Pandey(self.X)


    def getF_2019_Pandey_split(self, division):
        split = np.array_split(self.X, division, axis=1)
        self.columns = self.columns * division

        transformed = []
        for item in split:
            transformed.append(self.getF_2019_Pandey(item))

        vector = np.hstack(transformed)
        return vector


def main():

    streams = [p for p in os.listdir(SPLIT_DATA) if not p.startswith('.')]

    ####################################
    ########## CREATE VECTORS ##########
    ####################################

    vectors, names, columns = [], [], None
    for stream in tqdm(streams):

        filename = '%s/%s' % (SPLIT_DATA, stream)
        streamname = stream.split('.csv')[0]
        
        data = open(filename).readlines()
        data = np.asarray([(float(line.strip().split(',')[0]), float(line.strip().split(',')[1])) for line in open(filename).readlines()])

        subsets = create_subsets(data, 500, 100)
        columns = None

        try:

            if subsets:

                for subset in subsets:

                    start, end = subset[:, 0][0], subset[:, 0][-1]
                    timeseries_helper = data_feature_extractor(np.transpose(subset))

                    # # GROUPING 1
                    groups = [
                        timeseries_helper.getF_2019_Pandey_single()[1],
                    ]

                    # # GROUPING 2
                    # # groups = [
                    # #     timeseries_helper.getF_2019_Pandey_single()[1],
                    # #     timeseries_helper.getF_2019_Pandey_split(10)[1]
                    # # ]

                    # # GROUPING 3
                    # # groups = [
                    # #     timeseries_helper.getF_2019_Pandey_single()[1],
                    # #     timeseries_helper.getF_2019_Pandey_split(25)[1]
                    # # ]

                    # GROUPING 4
                    # groups = [
                    #     timeseries_helper.getF_2019_Pandey_single()[1],
                    #     timeseries_helper.getF_2019_Pandey_split(5)[1],
                    #     timeseries_helper.getF_2019_Pandey_split(25)[1]
                    # ]

                    if not columns: 
                        columns = timeseries_helper.columns
                    vectors.append([value for features in groups for value in features])
                    names.append([streamname, start, end])


        except Exception as e:

            print(e)


    # A: NORMALIZE ALL BUT SLOPE
    # vectors, columns = np.asarray(vectors), np.asarray(columns)
    # normal = vectors[:, np.where(columns != 'slope')[0]]
    # nonnormal = vectors[:, np.where(columns == 'slope')[0]]

    # normalizer = Normalizer().fit(normal)
    # joblib.dump(normalizer, NORMALIZER_PATH)
    # normal = normalizer.transform(normal)
    # vectors = np.concatenate((normal, nonnormal), axis=1)

    # A: NORMALIZE ALL
    # GROUPING 1
    vectors, columns = np.asarray(vectors), np.asarray(columns)
    normalizer = Normalizer().fit(vectors)
    joblib.dump(normalizer, NORMALIZER_PATH)
    vectors = normalizer.transform(vectors)

    with open(OUTPUT, 'w') as w:
    
        for i in range(len(vectors)):
            name, vector = names[i], vectors[i]
            streamname = name[0]

            w.write('%s,' % name[0])
            for value in name[1:]: w.write('%.10f,' % value)
            for value in vector[:-1]: w.write('%.10f,' % value)
            w.write('%.10f\n' % vector[-1])

    # #######################################
    # ########## CREATE SQL SCRIPT ##########
    # #######################################

    filename = '%s/%s' % (SPLIT_DATA, streams[0])
    data = open(filename).readlines()
    data = np.asarray([(float(line.strip().split(',')[0]), float(line.strip().split(',')[1])) for line in open(filename).readlines()])

    start, end = data[:, 0][0], data[:, 0][-1]
    timeseries_helper = data_feature_extractor(np.transpose(data))

    groups = [
        timeseries_helper.getF_2019_Pandey_single()[1],
        timeseries_helper.getF_2019_Pandey_split(10)[1]
    ]

    cols = [ 'STREAM', 'START', 'END' ]
    vector_length = len([value for features in groups for value in features])

    for i in range(vector_length): 
        cols += ['F%s' % (str(i + 1))]

    sqlstr = 'USE monitor_db;\n\n'
    sqlstr += 'DROP TABLE IF EXISTS hcdm_vectors_start;\n\n'
    sqlstr += 'CREATE TABLE hcdm_vectors_start (\n'
    sqlstr += '\t%s VARCHAR(100),\n' % cols[0]
    for col in cols[1:3]: sqlstr += '\t%s INTEGER,\n' % col
    for col in cols[3:-1]: sqlstr += '\t%s DOUBLE,\n' % col
    sqlstr += '\t%s DOUBLE\n' % cols[-1]
    sqlstr += ');\n\n';

    sqlstr += 'LOAD DATA LOCAL INFILE "' + os.path.abspath(__file__ + '/../../data/vector/hcdm_vectors.csv') + '" INTO TABLE hcdm_vectors_start FIELDS TERMINATED BY ",";\n\n'

    sqlstr += 'DROP TABLE IF EXISTS hcdm_vectors;\n\n'

    sqlstr += 'CREATE TABLE hcdm_vectors (\n'
    sqlstr += '\tSELECT '
    for col in cols[:-1]: sqlstr += '%s, ' % col
    sqlstr += '%s\n' % cols[-1]
    sqlstr += '\tFROM hcdm_vectors_start as a, (SELECT DISTINCT name FROM stream_data) AS b \n\tWHERE a.stream = b.name\n);\n\n'

    sqlstr += 'DROP TABLE hcdm_vectors_start;'

    with open(VECTOR_SCRIPT, 'w') as w:
        w.write(sqlstr)

    sqlstr = 'USE monitor_db;\n\n'
    sqlstr += 'DROP TABLE IF EXISTS event;\n\n'
    sqlstr += 'CREATE TABLE event (\n'
    sqlstr += '\tevent VARCHAR(100),\n'
    sqlstr += '\tstream VARCHAR(100),\n'
    sqlstr += '\ttimeStart INTEGER,\n'
    sqlstr += '\ttimeEnd INTEGER,\n'
    for col in cols[3:-1]: sqlstr += '\t%s DOUBLE,\n' % col
    sqlstr += '\t%s DOUBLE\n' % cols[-1]
    sqlstr += ');\n\n';

    with open(EVENT_SCRIPT, 'w') as w:
        w.write(sqlstr)

    datastr = "data = {\n"
    datastr += "\t'num_coeff': 2,\n"
    datastr += "\t'cols': ["
    for col in cols[:-1]: datastr += "'%s', " % col
    datastr += "'%s' ]\n" % cols[-1]
    datastr += "}"

    with open(API_SCRIPT, 'w') as w:
        w.write(datastr)


if __name__ == '__main__':
    main()
