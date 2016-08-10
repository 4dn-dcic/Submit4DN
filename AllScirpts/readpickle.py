"""A script to unfold the structures of downloaded object dictionaries."""
import pickle


def ReturnLib(Obj):
    """Return the pickled dictionary."""
    Fname = "EncodeMeta/All{}.p".format(Obj)
    return pickle.load(open(Fname, "r"))


def GetKeys(Dictionary, Query=''):
    """Find all the keys including nested ones."""
    DictKeys = Dictionary["@graph"][0].keys()
    return [i for i in DictKeys if Query.lower() in i.lower()]

DicLab = ReturnLib("Experiment")
print DicLab['@graph'][1]
Keys = GetKeys(DicLab, 'lab')
print Keys
print DicLab['lab']


# for Key in Keys:
#     if isinstance(ValExp[0][Key], dict):
#         print "{} is dictionary with keys{}".format(Key, ValExp[0][Key].keys())
#     else:
#         print Key, (20-len(Key))*' ', ValExp[0][Key]
# print ValExp[0]
