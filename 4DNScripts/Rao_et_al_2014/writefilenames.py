filein = '/Users/koray/Desktop/Tasks/Rao_et_al_2014/fileftpaddress.txt'

textinfile = open(filein,'r').read()
alllines = textinfile.split('\n')
t=0
for i in alllines:
    t = t+1
    items = []
    tag = []
    items = i.split('\t')
    tag = items[0]
    try:
        for ix in items[1].split(';'):
            filename = ix.split("/")[-1]
            print(ix+'\t'+tag+"_"+filename)
    except:
        pass
