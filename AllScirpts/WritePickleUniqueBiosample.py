"""Write pickle for @id of all and unique Biosamples used in Exp&Rep."""

import pickle


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
    """Return unique & all minor items for Major objects in list Compare."""
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

pickle.dump(LibBio, open('EncodeMeta/BiosampleInRepUnique.p', "wb"))
print '{} Unique objects were dumped in file'.format(len(LibBio))
pickle.dump(LibBioAll, open('EncodeMeta/BiosampleInRepAll.p', "wb"))
print '{} objects were dumped in file'.format(len(LibBioAll))
