"""Print tab delimited key value pair for encode object."""

import pickle
from operator import itemgetter
import numpy as np
import matplotlib.pyplot as plt

OBJlist = ['Lab', 'User', 'Experiment', 'Award', 'Reference',
           'Document', 'Replicate', 'AntibodyLot', 'Source', 'Donor',
           'Treatment', 'Library', 'Biosample', 'Organism']

for Obj in OBJlist:
    # Restrict to the following list?
    Restrict = 0  # 0 for NO, 1 for YES
    RestrictP = "EncodeMeta/BiosampleInRepUniqueXXX.p"

    # Return the pickled dictionary
    Fname = "EncodeMeta/All{}.p".format(Obj)
    DICT = pickle.load(open(Fname, "r"))
    if Restrict == 0:
        AllItems = [i for i in DICT['@graph']]
    if Restrict == 1:
        ExpObjList = pickle.load(open(RestrictP, "r"))
        AllItems = [i for i in DICT['@graph'] if i['@id'] in ExpObjList]

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

    # Draw stacked bar chart
    missing = 100-len(Result)
    Val1 = [i[1] for i in Result]+missing*[0]
    Val2 = [i[2] for i in Result]+missing*[0]
    Val3 = [i[3] for i in Result]+missing*[0]
    Val4 = [i[1]+i[2] for i in Result]+missing*[0]
    Val5 = [i[1]+i[2]+i[3] for i in Result]+missing*[0]

    Legend = [i[0] for i in Result]+missing*['']
    ind = 3*(np.arange(100))+1
    width = 1.8

    plt.figure(figsize=(20, 10))
    p4 = plt.bar(ind, Val5, width, color='w', lw=3)
    p1 = plt.bar(ind, Val1, width, color='#178500', lw=0)
    p2 = plt.bar(ind, Val2, width, color='#c96100', bottom=Val1, lw=0)
    p3 = plt.bar(ind, Val3, width, color='#9e3131', bottom=Val4, lw=0)

    plt.yticks(np.arange(0, 100, 10))
    plt.ylabel('no of elements')
    plt.title('Usage of Keys in Objects')

    plt.xticks(ind + width/2.0, Legend, rotation='vertical')

    # plt.legend((p1[0], p2[0], p3[0]), ('Used', 'Not Used', 'DNE'), loc=4)
    # plt.tight_layout()
    plt.savefig('Figures/Keys'+Obj+str(Restrict)+'.pdf')
    # plt.show()
