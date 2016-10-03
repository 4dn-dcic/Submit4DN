input_file = '/Users/koray/Github/4DNWranglerTools/Data_Files/Rao_et_al_2014/RaoRep.txt'
input_handle = open(input_file)
Allexps = [i.split('\t') for i in input_handle.read().split('\n')]
Allexps.pop(0)
biono = 0
tecno = 0

replicates = []

print(len(Allexps))
for i in Allexps:
    Name = ""
    Check = []
    Name = i[0]
    CheckTec = i[2:]
    CheckBio = i[3:]
    Allexps.remove(i)
    Found = 0
    Bio = 0
    Tec = 0

    for ix in Allexps:
            NameF = ""
            CheckF = []
            NameF = ix[0]
            CheckTec2 = ix[2:]
            CheckBio2 = ix[3:]

            if CheckBio == CheckTec:
                Found = 1
                CheckTecF = CheckF[1:]
                if CheckTec == CheckTecF:
                    both tech and biological
                else:
                    only biological
                Allexps.remove(ix)

    if Found = 0:
        continue
    else:
        replicates.
    break


print(len(Allexps))