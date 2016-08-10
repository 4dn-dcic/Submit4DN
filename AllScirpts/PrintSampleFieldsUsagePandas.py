"""Print tab delimited key value pair for encode object."""

import pickle
from operator import itemgetter
import matplotlib.pyplot as plt
import pandas as pd

OBJlist = ['Biosample', 'Lab', 'User', 'Experiment', 'Award', 'Reference',
           'Document', 'Replicate', 'AntibodyLot', 'Source', 'Donor',
           'Treatment', 'Library', 'Organism']

for Obj in OBJlist:

    # Return the pickled dictionary
    Fname = "EncodeMeta/All{}.p".format(Obj)
    DICT = pickle.load(open(Fname, "r"))
    AllItems = [i for i in DICT['@graph']]

    # Find all the keys including nested ones.
    AllPossibleKeys = []
    for Item in AllItems:
        Key = []
        Key = Item.keys()
        AllPossibleKeys.extend(Key)
    KEYS = list(set(AllPossibleKeys))

    Result = []
    for key in KEYS:
        DoesNotExist = 0
        Empty = 0
        Exists = 0
        for Item in AllItems:
            try:
                Item[key]
            except:
                DoesNotExist += 1
                continue
            if Item[key]:
                Exists += 1
            else:
                Empty += 1
        Total = float(DoesNotExist+Empty+Exists)/100
        Result.append([key, float(Exists)/Total, float(Empty)/Total,
                      float(DoesNotExist)/Total])
    Result.sort(key=itemgetter(1))

    df = pd.DataFrame(Result, index=[i[0] for i in Result],
                      columns=['Keys', 'Used', 'Not Used', 'DNE'])

    ax1 = plt.subplot2grid((1, 5), (0, 1), colspan=4)
    df.plot(ax=ax1, kind='barh', stacked=True, legend=False,
            figsize=(7, len(Result)/4.0), xlim=(0, 100),
            color=['#00d542', '#dbb800', '#e40000'])
    plt.savefig('Figures/Keys/Keys'+Obj+'.pdf')
