import pickle
import pandas

OBJlist = ['Lab', 'User', 'Experiment', 'Award', 'Reference',
           'Document', 'Replicate', 'AntibodyLot', 'Source', 'Donor',
           'Treatment', 'Library', 'Biosample', 'Organism']

AllObjKeylist = pickle.load(open('EncodeMetaAll/ObjectKeyList.p', 'r'))
print len(AllObjKeylist), ' object keys pairs'

OBJ = 'human'
for o, k in AllObjKeylist:
    if OBJ.lower() in o.lower():
        print o
        for key in k:
            print '\t', key
        print ''
        print ''
