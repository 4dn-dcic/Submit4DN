"""Print tab delimited key value pair for encode object."""

import pickle
from collections import Counter

Obj = 'reference'

# Return the pickled dictionary
Fname = "/Users/koray/Desktop/Tasks/Scripts/EncodeMetaAll/All_{}.p".format(Obj)
DICT = pickle.load(open(Fname, "r"))

# Find all the keys including nested ones.
ALAC = []
used = 0
for i in DICT["@graph"]:
    print i
    used = used+1
    KEYS = i.keys()
    try:
        AC = i["reference_type"]
    except:
        continue
    if AC != []:
        ALAC.append(AC)
print len(ALAC)
print ALAC
print Counter(ALAC)
print used
