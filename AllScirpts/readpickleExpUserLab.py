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
DicLab = ReturnLib("Experiment")
Keys = GetKeys(DicLab, '')

# Make list of dicts of labs
LabList = DicLab['@graph']
LabUL = [i['lab'][6:-1]+'___'+i['submitted_by'] for i in LabList]
print len(LabUL)
LabULunique=list(set(LabUL))
print len(LabULunique)

UniqueSubmitters=[i.split('___')[0] for i in LabULunique]





LabOcc = Counter(UniqueSubmitters)
print LabOcc
print len(LabOcc)
LabOccL = LabOcc.most_common()
LabOccM = [str(ix[1]) for ix in LabOccL]
LabOccN = Counter(LabOccM)

print LabOccN


LabOccO = []

for key, value in LabOccN.iteritems():
    temp = [int(key), value]
    LabOccO.append(temp)
print LabOccO

# Fill the gaps
for i in range(1, 22, 1):
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
plt.savefig('Figures/ExperimentUserLab.ps')



'''
LabOcc = Counter([i['lab'][6:-1] for i in LabList])
LabOccL = LabOcc.most_common()
Total = sum([float(v[1]) for v in LabOccL])
Total8 = sum([float(v[1]) for v in LabOccL[:8]])

print Total8/Total*100, "percent by top 8 of the groups"
print len(LabOccL), "is the total number of labs"

Colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue']*10

plt.pie([float(v[1]) for v in LabOccL],
        labels=[k[0] if int(k[1]) > 79 else '' for k in LabOccL],
        colors=Colors[:len(LabOccL)], autopct='%1.0f%%')
plt.savefig('Figures/ExperimentLab.ps')



'''
