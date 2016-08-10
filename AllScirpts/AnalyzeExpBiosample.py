"""Track items throgh Experiment and Print Histogram for Biosamples in Lib.

For embedded objects open the related dictionary and find objects
One example is library which is only excessible through replicates
"""

import pickle
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np


def ReturnLib(Obj):
    """Return the pickled dictionary."""
    Fname = "EncodeMeta/All{}.p".format(Obj)
    return pickle.load(open(Fname, "r"))


def GetKeys(Dictionary, Query=''):
    """Find all the keys including nested ones."""
    DictKeys = Dictionary["@graph"][0].keys()
    return [i for i in DictKeys if Query.lower() in i.lower()]


def GetItem(Major, Minor):
    """Return unique minor items from major object."""
    DicTemp = ReturnLib(Major)
    AllTemp = DicTemp['@graph']
    Accumulate = []
    NoKey = 0
    for i in AllTemp:
        try:
            if isinstance(i[Minor], (list, tuple)):
                Accumulate.extend(i[Minor])
            else:
                Accumulate.append(i[Minor])
        except:
            NoKey = NoKey + 1
    print len(Accumulate), ' instances'
    print len(list(set(Accumulate))), ' unique instances'
    print NoKey, ' elements does not have the key ', Minor
    return list(set(Accumulate))


def GetItemComp(Major, Minor, Compare):
    """Return unique minor items for Major objects in list Compare."""
    DicTemp = ReturnLib(Major)
    AllTemp = DicTemp['@graph']
    Accumulate = []
    NoKey = 0
    for i in AllTemp:
        if i['@id'] in Compare:
            try:
                if isinstance(i[Minor], (list, tuple)):
                    Accumulate.extend(i[Minor])
                else:
                    Accumulate.append(i[Minor])
            except:
                NoKey = NoKey + 1
    print len(Accumulate), ' instances'
    print len(list(set(Accumulate))), ' unique instances'
    print NoKey, ' elements does not have the key ', Minor
    return list(set(Accumulate)), Accumulate


# Get all replicates from experiments
ExRep = GetItem('Experiment', 'replicates')

# Get all libraries from replicates
RepLib, RepLibAll = GetItemComp('Replicate', 'library', ExRep)

# Get all biosample from library
LibBio, LibBioAll = GetItemComp('Library', 'biosample', RepLib)


# Get a list of occurances sorted for all Biosamples in Library
# If the list was ['a', 'a', 'b', 'c '','d','c','c', 'e',]
# The result would be [3,2,1,1,1]
LabOccN = Counter(LibBioAll)
LabOccO = []
for key, value in LabOccN.iteritems():
    LabOccO.append(value)
LabOccO.sort()

# Now I plot the histogram for number of occurances of occurances
# Taking the list above it would be "1":3, "2":1, "3":1, "4":0...
# This step can be done also with Counter function but I want custom ranges
Val = []
Label = []
for V in range(1, 21, 1):
    Val.append(sum(i == V for i in LabOccO))
    Label.append(str(V))
Val.append(sum(50 > i > 20 for i in LabOccO))
Val.append(sum(100 > i > 49 for i in LabOccO))
Val.append(sum(i > 99 for i in LabOccO))
Label.extend(['>20', '>49', '>99'])

indexes = np.arange(len(Label))
width = 1
plt.bar(indexes, Val, width)
plt.xticks(indexes + width * 0.5, Label)
plt.savefig('Figures/ExperimentBiosampleHist.ps')
