from tqdm import tqdm
import os

EVAL_DATA_DIR = os.path.abspath(__file__ + '/../../../Aniyama_groundtruth')
OUTPUT_DIR = os.path.abspath(__file__ + '/../../data/vector/aniyama')
OUTPUT_FILE = '%s/aniyama_data.csv' % (OUTPUT_DIR)


def main():
    types = [p for p in os.listdir(EVAL_DATA_DIR) if not p.startswith('.')]
    data = ''
    for t in types:
        for file in os.listdir(EVAL_DATA_DIR + '/' + t):
            stream = file.split('.')[0]
            with open(EVAL_DATA_DIR + '/' + t + '/' + file, 'r') as f:
                for i, line in enumerate(f.readlines()):
                    if i == 0:
                        continue
                    line = stream + ',' + line.strip() + ',' + t + '\n'
                    data += line

        with open(OUTPUT_FILE, 'w') as w:
            w.write(data)


if __name__ == '__main__':
    main()

