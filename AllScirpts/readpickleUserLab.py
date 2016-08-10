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

# Get the lab metadata and get the keys for the lab object
DicLab = ReturnLib("User")
Keys = GetKeys(DicLab, '')

# Make list of dicts of labs
LabList = DicLab['@graph']

UserLabs = []
for i in LabList:
    try:
        laba = i['lab'][6:-1]
    except:
        laba = 'nolab'
    UserLabs.append(laba)

LabOcc = Counter(UserLabs)
print LabOcc
print len(LabOcc)
LabOccL = LabOcc.most_common()
LabOccM = [str(ix[1]) for ix in LabOccL]
LabOccN = Counter(LabOccM)
LabOccO = []

for key, value in LabOccN.iteritems():
    temp = [int(key), value]
    LabOccO.append(temp)
for i in range(1, 21, 1):
    found = 0
    for a, b in LabOccO:
        if a == i:
            found = 1
    if found == 0:
        LabOccO.append([i, 0])

LabOccO.sort(key=itemgetter(0))


labels = [i[0] for i in LabOccO]
values = [i[1] for i in LabOccO]
indexes = np.arange(len(LabOccO))

width = 1
plt.bar(indexes, values, width)
plt.xticks(indexes + width * 0.5, labels)
plt.savefig('Figures/UserLab.ps')
