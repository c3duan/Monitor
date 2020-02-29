from nltk.corpus import wordnet as wn

filepath = '/home/monitor_db/data_creation/attribute_data_raw.csv'

def main():


    final = {}
    data = [line.strip() for line in open(filepath).readlines()]

    for line in data:

        start = line.split('|')[0]
        tokens = line.split('|')[0]
        all_syns = []

        tokens = tokens.split()

        new_tokens = []
        for token in tokens:
            if 'vav' in token:
                new_tokens += ['variable', 'air', 'volume', token]
            elif 'ahu' in token:
                new_tokens += ['air', 'handling', 'unit', token]
            elif 'temp' in token:
                new_tokens += ['temperature', token]
            elif 'avg' in token:
                new_tokens += ['average', token]
            elif '/' in token:
                words = token.split('/')
                new_tokens += words + [token]
            elif token == 'comp':
                new_tokens += ['compressor', token]
            else:
                new_tokens += [token]

        tokens = new_tokens
        
        for token in tokens:

            # redone = [token]

            syns = list(set([syn.lemmas()[0].name() for syn in wn.synsets(token)]))
            redone = []

            for item in syns:
                if '_' in item:
                    items = item.split('_')
                    for s_item in items: redone.append(s_item)
                else:
                    redone.append(item)

            all_syns += redone

        all_syns = list(set(all_syns))

        if start in final:
            for syn in all_syns:
                if syn not in final[start]: final[start].append(syn)
        else:
            final[start] = all_syns

    starts = list(final.keys())
    for start in starts:
        print('%s|%s' % (start, ' '.join(final[start])))


if __name__ == '__main__':
    main()
