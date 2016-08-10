def GetAllKeys(DICT, Query=''):
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
