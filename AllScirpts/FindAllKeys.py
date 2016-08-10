import pickle
import pandas

OBJlist = ['Lab', 'User', 'Experiment', 'Award', 'Reference',
           'Document', 'Replicate', 'AntibodyLot', 'Source', 'Donor',
           'Treatment', 'Library', 'Biosample', 'Organism']

AllObjKeylist = pickle.load(open('EncodeMetaAll/ObjectKeyList.p', 'r'))
print len(AllObjKeylist), ' object keys pairs'

Query = 'pipeline'
Result = []
for o, k in AllObjKeylist:
    if Query.lower() in o.lower():
        print o.upper()
        print "=================="
        for i in k:
            print i
        Result.append([o, ['Key has Query']])
    Found = []
    Found = [i for i in k if Query.lower() in i.lower()]
    if len(Found) > 0:
        Result.append([o, Found])




print len(Result)
for a, b in Result:
    print a, '\t', ' & '.join(b)
