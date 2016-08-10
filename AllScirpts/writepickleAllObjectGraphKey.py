import pickle

OBJlist = ['Lab']

AllOBJlist = pickle.load(open('EncodeMetaAll/ObjectList.p', 'r'))


def ReturnLib(Obj):
    """Return the pickled dictionary."""
    Fname = "EncodeMetaAll/All_{}.p".format(Obj)
    return pickle.load(open(Fname, "r"))


def GetAllKeys(Obj, Query=''):
    """Return unique minor items from major object."""
    DicTemp = ReturnLib(Obj)
    AllTemp = DicTemp['@graph']
    Accumulate = []
    for i in AllTemp:
        Accumulate = Accumulate + i.keys()
        Accumulate = list(set(Accumulate))
    return [ix for ix in Accumulate if Query.lower() in ix.lower()]


Found = []
for i in AllOBJlist:
    AllKeys = []
    AllKeys = GetAllKeys(i)
    Found.append([i, AllKeys])
    print i
print len(Found)

pickle.dump(Found, open('EncodeMetaAll/ObjectKeyList.p', "wb"))
