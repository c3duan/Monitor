from collections import Counter, defaultdict
from sklearn.externals import joblib
from multiprocessing import Pool
import glob, pdb, sys, os
from scipy import stats
from tqdm import tqdm
from data import data
import numpy as np
from db import db


NORMALIZER_PATH = os.path.abspath(__file__ + '/../normalizer.save')


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
        F[:, 5] = stats.skew(X, 1)
        F[:, 6] = stats.kurtosis(X, 1)
        
        # digitize the data for the calculation of entropy if it only contains less than 100 discreate values
        XX = np.zeros(X.shape)
        bins = 100

        for i in range(X.shape[0]):
            if len(np.unique(X[i,:])) < bins:
                XX[i,:] = X[i,:]
            else:
                XX[i,:] = np.digitize(X[i,:], np.linspace(min(X[i,:]), max(X[i,:]), num=bins))        

        F[:, 7] = stats.entropy(XX.T)
        F[:, 8] = stats.mode(X[1], axis=None)
        F[:, 9] = np.polyfit(X[0], X[1], 1)[0]

        # check illegal features nan/inf
        F[np.isnan(F)] = 0
        F[np.isinf(F)] = 0

        return F


    def getF_2019_Pandey_single(self):

        return self.getF_2019_Pandey(self.X)


    def getF_2019_Pandey_split(self, division):

        split = np.array_split(self.X, division, axis=1)
        self.columns = self.columns * (division + 1)

        transformed = []
        for item in split:
            transformed.append(self.getF_2019_Pandey(item))

        vector = np.hstack(transformed)
        return vector


def main():

    event, stream, start, end = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    num_coeff, cols = data['num_coeff'], ['EVENT'] + data['cols']

    query = "SELECT timestamp, value FROM stream_data WHERE name='%s' AND TIMESTAMP >= '%s' AND TIMESTAMP <= '%s' ORDER BY TIMESTAMP DESC" % (stream, start, end)
    cursor = db.cursor()
    cursor.execute(query)

    x, y = [], []
    for pair in cursor: 
        x.append(pair[0])
        y.append(pair[1])

    x, y = np.asarray(x), np.asarray(y)
    raw = np.transpose(np.asarray([x, y]))
    timeseries_helper = data_feature_extractor(np.transpose(raw))

    groups = [
        timeseries_helper.getF_2019_Pandey_single()[1],
        timeseries_helper.getF_2019_Pandey_split(10)[1]
    ]

    columns = np.asarray(timeseries_helper.columns)
    normalizer = joblib.load(NORMALIZER_PATH)

    vector = np.asarray([value for features in groups for value in features])
    normal = vector[np.where(columns != 'slope')[0]]
    nonnormal = vector[np.where(columns == 'slope')[0]]

    normal = normalizer.transform([normal])[0]
    vector = np.concatenate((normal, nonnormal))
    vector = np.asarray([event, stream] + [start, end] + ['%.10f' % item for item in vector])

    for item in vector: print('%s,' % item)
    sys.stdout.flush()


if __name__ == '__main__':
    main()
