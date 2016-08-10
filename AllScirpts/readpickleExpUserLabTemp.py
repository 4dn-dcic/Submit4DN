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


LabUL = [i['lab'][6:-1]+'\t'+i['submitted_by'] for i in LabList]
no = 0
for i in LabUL:
    no = no+1
print no
