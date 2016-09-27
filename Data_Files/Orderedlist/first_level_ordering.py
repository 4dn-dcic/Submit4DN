#!/usr/bin/env python3
# -*- coding: latin-1 -*-
import xlrd
import xlwt

InputFile = "/Users/koray/Github/4DNWranglerTools/Data_Files/Orderedlist/AllItems.xls"
OutputFile = "/Users/koray/Github/4DNWranglerTools/Data_Files/Orderedlist/reference_fields.xls"
book = xlrd.open_workbook(InputFile)
book_w = xlwt.Workbook()
Sheets = book.sheet_names()


sheet_order = [
    "IndividualMouse",
    "IndividualHuman",
    "Vendor",
    "Biosource",
    "Construct",
    "TreatmentRnai",
    "TreatmentChemical",
    "Target",
    "GenomicRegion",
    "Modification",
    "Enzyme",
    "Biosample",
    "Document",
    "Image",
    "ProtocolsCellCulture",
    "Protocol",
    "FileSet",
    "File",
    "ExperimentSet",
    "ExperimentHiC",
    "ExperimentCaptureC",
    "Publication"
]

do_not_use = [
    "submitted_by",
    "date_created",
    "organism",
    "schema_version",
    "accession",
    "uuid",
    "status",
    "quality_metric_flags:array",
    "notes",
    "restricted:boolean",
    "file_size:integer",
    "filename"

]

move_frond = [
    'award',
    'lab',
    'description',
    'title',
    'name',
    'aliases:array',
    '#Field Name:'
]

move_end = [
    'documents:array',
    'references:array',
    'url',
    'dbxrefs:array',
    'alternate_accessions:array'
]

for sheet in sheet_order:
    useful = []
    not_used = []
    write_list = []
    active_sheet = book.sheet_by_name(sheet)
    first_row_values = active_sheet.row_values(rowx=0)
    for field in first_row_values:
        if field in do_not_use:
            not_used.append(field)
        else:
            useful.append(field)
    useful = sorted(useful)
    not_used = sorted(not_used)

    for frond in move_frond:
        try:
            useful.insert(0, useful.pop(useful.index(frond)))
        except:
            print(sheet, "does not have", frond)

    for end in move_end:
        try:
            useful.pop(useful.index(end))
            useful.append(end)
        except:
            print(sheet, "does not have", end)
    new_sheet = book_w.add_sheet(sheet)
    for write_row_index, write_item in enumerate(useful):
        read_col_ind = first_row_values.index(write_item)
        column_val = active_sheet.col_values(read_col_ind)
        column_val.pop(2)
        for write_column_index, cell_value in enumerate(column_val):
            new_sheet.write(write_column_index, write_row_index, cell_value)
book_w.save(OutputFile)
