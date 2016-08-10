"""A script to unfold the structures of downloaded object dictionaries."""
import pickle
from collections import Counter
import matplotlib.pyplot as plt


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





# for Key in Keys:
#     if isinstance(ValExp[0][Key], dict):
#         print "{} is dictionary with keys{}".format(Key, ValExp[0][Key].keys())
#     else:
#         print Key, (20-len(Key))*' ', ValExp[0][Key]
# print ValExp[0]
