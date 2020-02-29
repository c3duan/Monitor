import re

filepath = '/home/monitor_db/sample_data/stream_attributes.csv'

def main():

    data = [line.strip().split('|') for line in open(filepath).readlines()]

    for line in data:
        name, atts = line[0], [att.strip() for att in line[1].split(',')]
        atts = [(att.split(':')[0], att.split(':')[1]) for att in atts]

        for pair in atts:
            att_name, att_val = pair[0], pair[1]
            print('%s|%s|%s' % (att_name, name, att_val))


if __name__ == '__main__':
    main()
