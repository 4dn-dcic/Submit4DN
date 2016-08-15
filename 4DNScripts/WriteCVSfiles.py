#!/usr/bin/env python3
# -*- coding: latin-1 -*-
"""GET the results of a search from an ENCODE server."""
import os
import glob
import csv
import xlwt

# List of objects to be imported from the website
# The order is the same with loadxl.py incase we need
# the order of loading
OBJlist = [
    'User', 'Award', 'Lab',
    'Organism', 'Publication', 'Document',
    'Vendor', 'Protocol', 'ProtocolsCellCulture',
    'Biosource', 'Enzyme', 'Construct',
    'TreatmentRnai', 'Modification', 'Biosample',
    'File', 'FileSet',
    'ExperimentHiC', 'ExperimentSet'
    ]
scriptpath = os.path.dirname(os.path.realpath(__file__))
os.chdir(scriptpath)

for OBJ in OBJlist:
    command = "python3 ENCODE_get_fields.py --collection "+OBJ+" --allfields --listfull >TSV/"+OBJ+".txt"
    os.system(command)

wb = xlwt.Workbook()
for filename in glob.glob("/Users/koray/Github/4DNWranglerTools/4DNScripts/TSV/*.txt"):
    (f_path, f_name) = os.path.split(filename)
    (f_short_name, f_extension) = os.path.splitext(f_name)
    ws = wb.add_sheet(f_short_name)
    sheetreader = csv.reader(open(filename, 'r'), delimiter='\t')
    for rowx, row in enumerate(sheetreader):
        for colx, value in enumerate(row):
            ws.write(rowx, colx, value)
wb.save("/Users/koray/Github/4DNWranglerTools/4DNScripts/SubmitData.xls")
