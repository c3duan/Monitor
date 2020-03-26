from tqdm import tqdm
import os
import sys

STREAM_DATA = os.path.abspath(__file__ + '/../../../sample_data/data.csv')
OUTPUT_DIR = os.path.abspath(__file__ + '/../../data/vector/split/stream_split')


def main(args):
    if len(args) > 0:
        STREAM_DATA = os.path.abspath(__file__ + args[0])
        OUTPUT_DIR = os.path.abspath(__file__ + args[1])

    with open(STREAM_DATA) as f:
        parsed = {}
        for line in tqdm(f):
            line = line.strip().split(',')
            stream, timestamp, value, event = line[0], float(line[1]), float(line[2]), float(line[3])

            if stream in parsed:
                parsed[stream]['x'].append(timestamp)
                parsed[stream]['y'].append(value)

            else:
                parsed[stream] = { 'x': [], 'y': [] }
                parsed[stream]['x'].append(timestamp)
                parsed[stream]['y'].append(value)


    streams = list(parsed.keys())
    for stream in tqdm(streams):
        filename = OUTPUT_DIR + "/" + stream.replace(' ', '_') + ".csv"

        with open(filename, 'w') as w:
            for i in range(len(parsed[stream]['x'])):
                w.write('%s,%s\n' % (parsed[stream]['x'][i], parsed[stream]['y'][i]))


if __name__ == '__main__':
    main(sys.argv[1:])

