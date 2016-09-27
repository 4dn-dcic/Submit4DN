#!/usr/bin/env python3
# -*- coding: latin-1 -*-
import xlrd
import xlwt
import os

folder = os.path.dirname(os.path.abspath(__file__))
ReadFile = "fieldsRao.xls"
RefFile = "Submission_first_round.xls"
OutputFile = "Rao_ordered_test.xls"

bookref = xlrd.open_workbook(folder+'/'+RefFile)
bookread = xlrd.open_workbook(folder+'/'+ReadFile)
book_w = xlwt.Workbook()
Sheets = bookread.sheet_names()

for sheet in Sheets:
    active_sheet_read = bookread.sheet_by_name(sheet)
    active_sheet_ref = bookref.sheet_by_name(sheet)
    first_row_values_read = active_sheet_read.row_values(rowx=0)
    first_row_values_ref = active_sheet_ref.row_values(rowx=0)

    new_sheet = book_w.add_sheet(sheet)
    for write_row_index, write_item in enumerate(first_row_values_ref):
        try:
            read_col_ind = first_row_values_read.index(write_item)
        except:
            new_sheet.write(0, write_row_index, write_item)
            continue
        column_val = active_sheet_read.col_values(read_col_ind)
        for write_column_index, cell_value in enumerate(column_val):
            new_sheet.write(write_column_index, write_row_index, cell_value)
book_w.save(folder+'/'+OutputFile)
