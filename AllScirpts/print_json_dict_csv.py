import json
import pandas
import glob
import os


INSERTS = glob.glob('/Users/koray/Github/encode/src/encoded/tests/data/inserts/*.json')
print len(INSERTS)
for Insert in INSERTS:
    fpath, fname = os.path.split(Insert)
    NAME = fname[:-5]
    print NAME
    DATA = json.load(open(Insert))
    df = pandas.DataFrame.from_records(DATA)
    writeN = ''
    writeN = '/Users/koray/Desktop/Tasks/Scripts/TDF/{}.txt'.format(NAME)
    CSV = df.to_csv(writeN, sep='\t', index=False)
