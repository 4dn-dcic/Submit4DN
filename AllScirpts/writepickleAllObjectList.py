import pickle
import glob
import os

AllFiles = glob.glob('/Users/koray/Desktop/Tasks/Scripts/EncodeMetaAll/All*.p')
AllOBJ=[]
for i in AllFiles:
    fpath, fname = os.path.split(i)
    OBJ = fname[4:-2]
    AllOBJ.append(OBJ)
print len(AllOBJ)

pickle.dump(AllOBJ, open('EncodeMetaAll/ObjectList.p', "wb"))
