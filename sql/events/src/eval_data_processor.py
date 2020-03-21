from tqdm import tqdm
import os

EVAL_DATA_DIR = os.path.abspath(__file__ + '/../../../Aniyama_groundtruth')
OUTPUT_DIR = os.path.abspath(__file__ + '/../../data/vector/eval')


def main():
    tables = [p for p in os.listdir(EVAL_DATA_DIR) if not p.startswith('.')]

    for table in tables:
        filename = '%s/%s.csv' % (OUTPUT_DIR, table)
        table_data = ''
        for file in os.listdir(EVAL_DATA_DIR + '/' + table):
            stream = file.split('.')[0]
            with open(EVAL_DATA_DIR + '/' + table + '/' + file, 'r') as f:
                for i, line in enumerate(f.readlines()):
                    if i == 0:
                        continue
                    table_data += (stream + ',' + line)

        with open(filename, 'w') as w:
            w.write(table_data)


if __name__ == '__main__':
    main()

