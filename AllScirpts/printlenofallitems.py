"""print # of item in each stored category and also corresponding item
in Experiment or another object"""
import pickle


def ReturnLib(Obj):
    """Return the pickled dictionary."""
    Fname = "EncodeMeta/All{}.p".format(Obj)
    return pickle.load(open(Fname, "r"))


def GetKeys(Dictionary, Query=''):
    """Find all the keys including nested ones."""
    DictKeys = Dictionary["@graph"][0].keys()
    return [i for i in DictKeys if Query.lower() in i.lower()]


OBJlist = ['Lab', 'User', 'Experiment', 'Award', 'Reference',
           'Document', 'Replicate', 'AntibodyLot', 'Source', 'Donor',
           'Treatment', 'Library', 'Biosample', 'Organism']

for i in OBJlist:
    DicEle = {}
    DicEle = ReturnLib(i)
    print i, '\t', len(DicEle['@graph'])


DicExp = ReturnLib('Experiment')
AllExp = DicExp['@graph']


OBJlist = ['Lab', 'Submitted_by', 'Experiment', 'Award', 'Reference',
           'Document', 'Replicate', 'AntibodyLot', 'Source', 'Donor',
           'Treatment', 'Library', 'Biosample', 'Organism']

for i in OBJlist:
    Counter = []
    for exp in AllExp:
        try:
            Counter.append(exp[i.lower()])
        except:
            # print i, ' is not a key'
            break
    if i == 'Award':
        print list(set(Counter))
    print i, '\t', str(len(list(set(Counter))))
