#!/usr/bin/env python3
# -*- coding: latin-1 -*-
"""Cell culture details must be added when used for all experiments"""

import xlrd
from collections import Counter

input_file = '/Users/koray/Github/4DNWranglerTools/Data_Files/Rao_et_al_2014/fieldsRao.xls'


def xls2list(filename, remove, sheetname=None):
    """Take named sheet and turn into list."""
    book = xlrd.open_workbook(filename)
    sheet_list = []
    sheet = book.sheet_by_name(sheetname)
    rm = []
    for index in range(sheet.nrows):
        key = ''
        data_row = [cell.value for cell in sheet.row(index)]
        # index columns to remove and aliases
        if index == 0:
            try:
                for rem in remove:
                    rm.append(data_row.index(rem))
            except:
                pass
            key_ind = data_row.index('aliases')
        # remove 3 comment rows
        if index in [1, 2, 3]:
            continue
        # remove the values and get the key
        rm.sort(reverse=True)
        key = data_row[key_ind]
        for r in rm:
            del data_row[r]
        data_row.remove(key)
        sheet_list.append([key, data_row])
    return sheet_list


# Remove fields that are item specific and does not effect replicate classification
Biosample_Remove = ['#Field Name:',
                    'description',
                    'biosample_relation.biosample',
                    'biosample_relation.relationship_type',
                    'dbxrefs',
                    'alternate_accessions',
                    ]
# Remove fields that are item specific and does not effect replicate classification
ExperimentHiC_Remove = ['#Field Name:',
                        'description',
                        'experiment_relation.experiment',
                        'experiment_relation.relationship_type',
                        'experiment_sets|0',
                        'experiment_sets|1',
                        'experiment_sets|2',
                        'experiment_sets|3',
                        'files',
                        'filesets',
                        'dbxrefs',
                        'alternate_accessions',
                        'average_fragment_size',
                        'fragment_size_range'
                        ]


Biosample = xls2list(input_file, Biosample_Remove, sheetname="Biosample")
HiC = xls2list(input_file, ExperimentHiC_Remove, sheetname="ExperimentHiC")
biosample_index = HiC[0][1].index('*biosample')
del HiC[0]

# Create a list that has [exp alias, exp details, biosample alias, biosample details]
for exp in HiC[:]:
    a, b = exp[0], exp[1]
    Bio = b[biosample_index]
    del b[biosample_index]
    exp.append(Bio)
    for c, d in Biosample:
        if Bio == c:
            exp.append(d)
            break

# First check if the biosample details are the same
# Second check if the experiment details are the same
# if 1 or 2 not the same not replicates
# Third check if the biosample alias is the same
# if not it is biological replicates
# if the same, technical replicates
Replicates = []
Skip = []
Biorep = 0
for exp in HiC[:]:
    Group = []
    exp_al = exp[0]
    exp_det = exp[1]
    bio_al = exp[2]
    bio_det = exp[3]
    if exp_al in Skip:
        continue
    for exp2 in HiC:
            exp_al2 = exp2[0]
            exp_det2 = exp2[1]
            bio_al2 = exp2[2]
            bio_det2 = exp2[3]
            if exp_det == exp_det2:
                if bio_det == bio_det2:
                    Group.append([exp_al2, bio_al2])
    # if thee are multiple items in the group assign them a biological replicate number
    if len(Group) > 1:
        Biorep = Biorep+1
        for gr in Group:
            gr.append('dciclab:repbio'+'0'*(3-len(str(Biorep)))+str(Biorep))
        add_skip = [i[0] for i in Group]
        Skip.extend(add_skip)
    else:
        for gr in Group:
            gr.append('')
    Tecrep = 0
    bio_all = [i[1] for i in Group]
    bio_count = Counter(bio_all)
    Tecreplist =[]
    for gr in Group:
        if gr[1] in Tecreplist:
            gr.append('dciclab:reptec'+'0'*(3-len(str(Biorep)))+str(Biorep)+'_'+'0'*(3-len(str(Tecrep)))+str(Tecrep))
        elif bio_count[gr[1]] > 1:
            Tecrep = Tecrep + 1
            gr.append('dciclab:reptec'+'0'*(3-len(str(Biorep)))+str(Biorep)+'_'+'0'*(3-len(str(Tecrep)))+str(Tecrep))
            Tecreplist.append(gr[1])
        else:
            gr.append('')
    Replicates.extend(Group)

Replicates.sort()
for i in Replicates:
    print('\t'.join(i))
print('###################')
print('###################')
print('###################')
AllBio = [i[2] for i in Replicates if i != '']
AllBio = list(set(AllBio))
AllBio = sorted(AllBio)
for i in AllBio:
    print(i)
print('###################')
print('###################')
print('###################')
AllTec = [i[3] for i in Replicates if i != '']
AllTec = list(set(AllTec))
AllTec = sorted(AllTec)
for i in AllTec:
    print(i)














