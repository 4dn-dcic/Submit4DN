"""A script to unfold the structures of downloaded object dictionaries."""
import pickle
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
from operator import itemgetter


def ReturnLib(Obj):
    """Return the pickled dictionary."""
    Fname = "EncodeMeta/All{}.p".format(Obj)
    return pickle.load(open(Fname, "r"))


def GetKeys(Dictionary, Query=''):
    """Find all the keys including nested ones."""
    DictKeys = Dictionary["@graph"][0].keys()
    return [i for i in DictKeys if Query.lower() in i.lower()]

Large = 'Biosample'
Small = 'Library'


# Get the lab metadata and get the keys for the lab object
DicEle = ReturnLib(Small)
Keys = GetKeys(DicEle, '')

# Make list of dicts of labs
EleList = DicEle['@graph']
# print EleList[0]['biosample'][12:-1]

# Catch items without the upper shell
UniqueItems = []
for i in EleList:
    try:
        laba = i[Large.lower()][12:-1]
    except:
        laba = 'no'+Large
    UniqueItems.append(laba)
print len(UniqueItems)

EleOcc = Counter(UniqueItems)
print len(EleOcc)
print EleOcc

'''
EleOccL = EleOcc.most_common()
EleOccM = [str(ix[1]) for ix in EleOccL]
EleOccN = Counter(EleOccM)
EleOccO = []

for key, value in EleOccN.iteritems():
    temp = [int(key), value]
    EleOccO.append(temp)
for i in range(1, 21, 1):
    found = 0
    for a, b in EleOccO:
        if a == i:
            found = 1
    if found == 0:
        EleOccO.append([i, 0])

EleOccO.sort(key=itemgetter(0))


labels = [i[0] for i in EleOccO]
values = [i[1] for i in EleOccO]
indexes = np.arange(len(EleOccO))

width = 1
plt.bar(indexes, values, width)
plt.xticks(indexes + width * 0.5, labels)
plt.savefig('Figures/'+Large+'_'+Small+'.ps')
'''
