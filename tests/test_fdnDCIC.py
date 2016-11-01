import pytest
import wranglertools.fdnDCIC as fdnDCIC

# test data is in conftest.py

keypairs = {
            "default":
            {"server": "https://test.FDN.org",
             "key": "keystring",
             "secret": "secretstring"
             }
            }


def test_nothing():
    assert(1)


def test_key():
    key = fdnDCIC.FDN_Key(keypairs, "default")
    assert(key)
    assert(type(key.server) is str)
    assert(type(key.authpw) is str)
    assert(type(key.authid) is str)


def test_key_file():
    key = fdnDCIC.FDN_Key('./tests/data_files/keypairs.json', "default")
    assert(key)
    assert(type(key.server) is str)
    assert(type(key.authpw) is str)
    assert(type(key.authid) is str)


@pytest.mark.connection
def test_connection():
    key = fdnDCIC.FDN_Key(keypairs, "default")
    connection = fdnDCIC.FDN_Connection(key)
    assert(connection)
    assert(connection.auth)
    assert(connection.server)


def test_FDN_url():
    key = fdnDCIC.FDN_Key(keypairs, "default")
    connection = fdnDCIC.FDN_Connection(key)
    test_objid_frame = [["trial", None],
                        ["trial?some", None],
                        ["trial", "object"],
                        ["trial?some", "object"]
                        ]
    expected_url = ["https://test.FDN.org/trial?limit=all",
                    "https://test.FDN.org/trial?some&limit=all",
                    "https://test.FDN.org/trial?limit=all&frame=object",
                    "https://test.FDN.org/trial?some&limit=all&frame=object"
                    ]
    for n, case in enumerate(test_objid_frame):
        t_url = fdnDCIC.FDN_url(case[0], connection, case[1])
        assert t_url == expected_url[n]


# content of test_module.py
# import os.path
# def getssh(): # pseudo application code
#     return os.path.join(os.path.expanduser("~admin"), '.ssh')
#
# def test_mytest(monkeypatch):
#     def mockreturn(path):
#         return '/abc'
#     monkeypatch.setattr(os.path, 'expanduser', mockreturn)
#     x = getssh()
#     assert x == '/abc/.ssh'

# @pytest.mark.get
# def test_get():
#     key = fdnDCIC.FDN_Key(keypairs, "default")
#     connection = fdnDCIC.FDN_Connection(key)
#     result = fdnDCIC.get_FDN("/profiles/", connection)
#     assert(type(result) is dict)


def test_filter_and_sort():
    test_list = ["submitted_by", "date_created", "organism", "schema_version", "accession", "uuid", "status",
                 "quality_metric_flags", "notes", "restricted", "file_size", "filename", "alternate_accessions",
                 "content_md5sum", "md5sum", "quality_metric", "files_in_set", "experiments", "experiments_in_set",
                 'dbxrefs', 'references', 'url', 'documents', 'award', '*award', 'lab', '*lab', 'description',
                 'title', '*title', 'name', '*name', 'aliases', '#Field Name:']
    result_list = ['#Field Name:', '*award', '*lab', '*name', '*title', 'aliases', 'award', 'dbxrefs',
                   'description', 'documents', 'lab', 'name', 'references', 'title', 'url']
    assert result_list == fdnDCIC.filter_and_sort(test_list)


def test_move_to_frond():
    test_list = ['#Field Name:', '*award', '*lab', '*name', '*title', 'aliases', 'award', 'dbxrefs',
                 'description', 'documents', 'lab', 'name', 'references', 'title', 'url']
    result_list = ['#Field Name:', 'aliases', '*name', 'name', '*title', 'title', 'description',
                   '*lab', 'lab', '*award', 'award', 'dbxrefs', 'documents', 'references', 'url']
    assert result_list == fdnDCIC.move_to_frond(test_list)


def test_move_to_end():
    test_list = ['#Field Name:', 'aliases', '*name', 'name', '*title', 'title', 'description',
                 '*lab', 'lab', '*award', 'award', 'dbxrefs', 'documents', 'references', 'url']
    result_list = ['#Field Name:', 'aliases', '*name', 'name', '*title', 'title', 'description',
                   '*lab', 'lab', '*award', 'award', 'documents', 'references', 'url', 'dbxrefs']
    assert result_list == fdnDCIC.move_to_end(test_list)


def test_switch_fields():
    cases = [
            [['cell_line_tier', 'cell_line', 'SOP_cell_line'], 'Biosource'],
            [['start_coordinate', 'start_location', 'location_description',
              'end_location', 'end_coordinate'], "GenomicRegion"],
            [['experiment_relation.relationship_type', 'experiment_sets|3', 'files', 'average_fragment_size',
              'experiment_sets|1', 'fragment_size_range', 'documents', 'experiment_relation.experiment',
              'experiment_sets|2', 'filesets', 'experiment_sets|0'], "Experiment"]
            ]
    result_list = [['cell_line', 'cell_line_tier', 'SOP_cell_line'],
                   ['location_description', 'start_location', 'end_location', 'start_coordinate', 'end_coordinate'],
                   ['average_fragment_size', 'fragment_size_range', 'files', 'filesets',
                    'experiment_relation.relationship_type', 'experiment_relation.experiment', 'experiment_sets|0',
                    'experiment_sets|1', 'experiment_sets|2', 'experiment_sets|3', 'documents']]
    for n, (a, b) in enumerate(cases):
        assert result_list[n] == fdnDCIC.switch_fields(a, b)





# def fetch_all_items(sheet, field_list, connection):
#     """For a given sheet, get all released items"""
#     all_items = []
#     if sheet in fetch_items.keys():
#         obj_id = "search/?type=" + fetch_items[sheet]
#         get_FDN(obj_id, connection)
#         items_list = get_FDN(obj_id, connection)['@graph']
#         for item in items_list:
#             item_info = []
#             for field in field_list:
#                 if field == "#Field Name:":
#                     item_info.append("#")
#                 else:
#                     item_info.append(item.get(field, ''))
#             all_items.append(item_info)
#         return all_items
#     else:
#         return
#
#
# def order_FDN(input_xls, connection):
#     """Order and filter created xls file."""
#     ReadFile = input_xls
#     OutputFile = input_xls[:-4]+'_ordered.xls'
#     bookread = xlrd.open_workbook(ReadFile)
#     book_w = xlwt.Workbook()
#     Sheets_read = bookread.sheet_names()
#     Sheets = []
#     # text styling for all columns
#     style = xlwt.XFStyle()
#     style.num_format_str = "@"
#     # reorder sheets based on sheet_order list and report if there are missing one from this list
#     for sh in sheet_order:
#         if sh in Sheets_read:
#             Sheets.append(sh)
#             Sheets_read.remove(sh)
#     if Sheets_read:
#         print(Sheets_read, "not in sheet_order list, please update")
#         Sheets.extend(Sheets_read)
#     for sheet in Sheets:
#         useful = []
#         active_sheet = bookread.sheet_by_name(sheet)
#         first_row_values = active_sheet.row_values(rowx=0)
#         # remove items from fields in xls
#         useful = filter_and_sort(first_row_values)
#         # move selected to front
#         useful = move_to_frond(useful)
#         # move selected to end
#         useful = move_to_end(useful)
#         # reorder some items based on reorder list
#         useful = switch_fields(useful, sheet)
#         # fetch all items for common objects
#         all_items = fetch_all_items(sheet, useful, connection)
#         # create a new sheet and write the data
#         new_sheet = book_w.add_sheet(sheet)
#         for write_row_index, write_item in enumerate(useful):
#             read_col_ind = first_row_values.index(write_item)
#             column_val = active_sheet.col_values(read_col_ind)
#             for write_column_index, cell_value in enumerate(column_val):
#                 new_sheet.write(write_column_index, write_row_index, cell_value, style)
#         # write common objects
#         if all_items:
#             for i, item in enumerate(all_items):
#                 for ix in range(len(useful)):
#                     write_column_index_II = write_column_index+1+i
#                     new_sheet.write(write_column_index_II, ix, item[ix], style)
#         else:
#             write_column_index_II = write_column_index
#         # write 50 empty lines with text formatting
#         for i in range(100):
#             for ix in range(len(useful)):
#                 write_column_index_III = write_column_index_II+1+i
#                 new_sheet.write(write_column_index_III, ix, '', style)
#     book_w.save(OutputFile)