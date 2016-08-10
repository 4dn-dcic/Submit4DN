"""There are more unique awards in experiments than there are
awards in the awards json."""
import pickle


def ReturnLib(Obj):
    """Return the pickled dictionary."""
    Fname = "EncodeMeta/All{}.p".format(Obj)
    return pickle.load(open(Fname, "r"))


ListAwards = ReturnLib('award')['@graph']
AwardUnique = []
for i in ListAwards:
    AwardUnique.append(i['@id'])
UniqueAwards = list(set(AwardUnique))
print len(UniqueAwards), ' unique items in awards'

DicExp = ReturnLib('Experiment')
AllExp = DicExp['@graph']

Counter = []
for exp in AllExp:
    Counter.append(exp['award'])
UniqueCounter = list(set(Counter))
print len(UniqueCounter), ' unique items in awards'

UniqueInExp = list(set(UniqueCounter)-set(UniqueAwards))
for i in UniqueInExp:
    print 'https://www.encodeproject.org'+i
UniqueInAward = list(set(UniqueAwards)-set(UniqueCounter))
print '\n\n\n'
for i in UniqueInAward:
    print 'https://www.encodeproject.org'+i

Union = list(set(UniqueAwards) & set(UniqueCounter))
Sum = list(set(UniqueAwards) | set(UniqueCounter))
TotalDiff = list(set(Sum) - set(Union))
TotalDiff2 = list(set(UniqueInExp) | set(UniqueInAward))
