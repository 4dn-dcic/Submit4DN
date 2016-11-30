#!/usr/bin/env python3
# -*- coding: latin-1 -*-

import requests
import json
import logging
import os.path
import hashlib
import xlrd
import xlwt


class FDN_Key:
    def __init__(self, keyfile, keyname):
        if os.path.isfile(str(keyfile)):
            keys_f = open(keyfile, 'r')
            keys_json_string = keys_f.read()
            keys_f.close()
            keys = json.loads(keys_json_string)
        else:
            keys = keyfile
        key_dict = keys[keyname]
        self.authid = key_dict['key']
        self.authpw = key_dict['secret']
        self.server = key_dict['server']
        if not self.server.endswith("/"):
            self.server += "/"


class FDN_Connection(object):
    def __init__(self, key):
        self.headers = {'content-type': 'application/json', 'accept': 'application/json'}
        self.server = key.server
        if (key.authid, key.authpw) == ("", ""):
            self.auth = ()
        else:
            self.auth = (key.authid, key.authpw)


class FDN_Schema(object):
    def __init__(self, connection, uri):
        self.uri = uri
        self.connection = connection
        self.server = connection.server
        response = get_FDN(uri, connection)
        self.properties = response['properties']
        self.required = None
        if 'required' in response:
            self.required = response['required']


def FDN_url(obj_id, connection, frame):
    if frame is None:
        if '?' in obj_id:
            url = connection.server + obj_id+'&limit=all'
        else:
            url = connection.server + obj_id+'?limit=all'
    elif '?' in obj_id:
        url = connection.server + obj_id+'&limit=all&frame='+frame
    else:
        url = connection.server + obj_id+'?limit=all&frame='+frame
    return url


def get_FDN(obj_id, connection, frame="object"):
    '''GET an FDN object as JSON and return as dict'''
    url = FDN_url(obj_id, connection, frame)
    logging.debug('GET %s' % (url))
    response = requests.get(url, auth=connection.auth, headers=connection.headers)
    logging.debug('GET RESPONSE code %s' % (response.status_code))
    try:
        if response.json():
            logging.debug('GET RESPONSE JSON: %s' %
                          (json.dumps(response.json(), indent=4, separators=(',', ': '))))
    except:  # pragma: no cover
        logging.debug('GET RESPONSE text %s' % (response.text))
    if not response.status_code == 200:  # pragma: no cover
        if response.json().get("notification"):
            logging.warning('%s' % (response.json().get("notification")))
        else:
            # logging.warning('GET failure.  Response code = %s' % (response.text))
            pass
    return response.json()


def patch_FDN(obj_id, connection, patch_input):
    '''PATCH an existing FDN object and return the response JSON
    '''
    if isinstance(patch_input, dict):
        json_payload = json.dumps(patch_input)
    elif isinstance(patch_input, str):
        json_payload = patch_input
    else:  # pragma: no cover
        print('Datatype to PATCH is not string or dict.')
    url = connection.server + obj_id
    logging.debug('PATCH URL : %s' % (url))
    logging.debug('PATCH data: %s' % (json_payload))
    response = requests.patch(url, auth=connection.auth, data=json_payload, headers=connection.headers)
    logging.debug('PATCH RESPONSE: %s' % (json.dumps(response.json(), indent=4, separators=(',', ': '))))
    if not response.status_code == 200:  # pragma: no cover
        logging.warning('PATCH failure.  Response = %s' % (response.text))
    return response.json()


def new_FDN(connection, collection_name, post_input):
    '''POST an FDN object as JSON and return the response JSON
    '''
    if isinstance(post_input, dict):
        json_payload = json.dumps(post_input)
    elif isinstance(post_input, str):
        json_payload = post_input
    else:  # pragma: no cover
        print('Datatype to POST is not string or dict.')
    url = connection.server + collection_name
    logging.debug("POST URL : %s" % (url))
    logging.debug("POST data: %s" % (json.dumps(post_input, sort_keys=True, indent=4,
                                     separators=(',', ': '))))
    response = requests.post(url, auth=connection.auth, headers=connection.headers, data=json_payload)
    logging.debug("POST RESPONSE: %s" % (json.dumps(response.json(), indent=4, separators=(',', ': '))))
    if not response.status_code == 201:  # pragma: no cover
        logging.warning('POST failure. Response = %s' % (response.text))
    logging.debug("Return object: %s" % (json.dumps(response.json(), sort_keys=True, indent=4,
                                         separators=(',', ': '))))
    return response.json()


def md5(path):
    md5sum = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            md5sum.update(chunk)
    return md5sum.hexdigest()


############################################################
############################################################
# following part is for ordering fields in the created excel
# and also populating it with the existing fields for common
# items.
# use the following order to process the sheets
# if name is not here, will not be processed during ordering
############################################################
############################################################
sheet_order = [
    "User", "Award", "Lab", "Document", "Protocol", "Publication", "Organism", "IndividualMouse", "IndividualHuman",
    "Vendor", "Enzyme", "Biosource", "Construct", "TreatmentRnai", "TreatmentChemical",
    "GenomicRegion", "Target", "Modification", "Image", "BiosampleCellCulture", "Biosample",
    "FileFastq", "FileFasta", "FileSet", "ExperimentHiC", "ExperimentCaptureC",
    "ExperimentSet", "ExperimentSetReplicate"]

do_not_use = [
    "submitted_by", "date_created", "organism", "schema_version", "accession", "uuid", "status",
    "quality_metric_flags", "notes", "restricted", "file_size", "filename", "alternate_accessions",
    "content_md5sum", "md5sum", "quality_metric", "files_in_set", "experiments", "experiments_in_set"]


def filter_and_sort(list_names):
    """Filter and sort fields"""
    useful = []
    for field in list_names:
        if field in do_not_use:
            pass
        else:
            useful.append(field)
    # sort alphabetically
    useful = sorted(useful)
    return useful

move_frond = ['experiment_set', '*tec_rep_no', '*bio_rep_no', '*replicate_set',
              'award', '*award', 'lab', '*lab', 'description',
              'title', '*title', 'name', '*name', 'aliases', '#Field Name:']


def move_to_frond(list_names):
    """Move names frond"""
    for frond in move_frond:
        try:
            list_names.remove(frond)
            list_names.insert(0, frond)
        except:  # pragma: no cover
            pass
    return list_names

move_end = ['documents', 'references', 'url', 'dbxrefs']


def move_to_end(list_names):
    """Move names to end"""
    for end in move_end:
        try:
            list_names.pop(list_names.index(end))
            list_names.append(end)
        except:  # pragma: no cover
            pass
    return list_names

# reorder individual items in sheets, [SHEET, MOVE_ITEM, MOVE_BEFORE]
reorder = [
    ['Biosource', 'cell_line', 'SOP_cell_line'],
    ['Biosource', 'cell_line_tier', 'SOP_cell_line'],
    ['GenomicRegion', 'start_coordinate', 'end_coordinate'],
    ['GenomicRegion', 'start_location', 'end_location'],
    ['GenomicRegion', 'location_description', 'start_location'],
    ['BiosampleCellCulture', 'protocol_documents', 'protocol_SOP_deviations'],
    ['Biosample', 'biosample_relation.relationship_type', 'biosample_relation.biosample'],
    ['Enzyme', 'catalog_number', 'attachment'],
    ['Enzyme', 'recognition_sequence', 'attachment'],
    ['Enzyme', 'site_length', 'attachment'],
    ['Enzyme', 'cut_position', 'attachment'],
    ['File', 'related_files.relationship_type', 'related_files.file'],
    ['Experiment', 'average_fragment_size', 'fragment_size_range'],
    ['Experiment', 'files', 'documents'],
    ['Experiment', 'filesets', 'documents'],
    ['Experiment', 'experiment_relation.relationship_type', 'documents'],
    ['Experiment', 'experiment_relation.experiment', 'documents']
]


def switch_fields(list_names, sheet):
    for sort_case in reorder:
        # to look for all experiments with "Experiment" name, it will also get ExperimentSet
        # there are no conflicting field names
        if sort_case[0] in sheet:
            try:
                # tihs is working more consistently then the pop item method
                list_names.remove(sort_case[1])
                list_names.insert(list_names.index(sort_case[2]), sort_case[1])
            except:  # pragma: no cover
                pass
    return list_names

# if object name is in the following list, fetch all current/released items and add to xls
# if experiment is ever added to this list, experiment set related fields might cause some problems
fetch_items = {
    "Document": "document", "Protocol": "protocol", "Enzymes": "enzyme", "Biosource": "biosource",
    "Publication": "publication", "Vendor": "vendor"}


def fetch_all_items(sheet, field_list, connection):
    """For a given sheet, get all released items"""
    all_items = []
    if sheet in fetch_items.keys():
        obj_id = "search/?type=" + fetch_items[sheet]
        resp = get_FDN(obj_id, connection)
        items_list = resp['@graph']
        for item in items_list:
            item_info = []
            for field in field_list:
                # required fields will have a star
                field = field.strip('*')
                # add # to skip existing items during submission
                if field == "#Field Name:":
                    item_info.append("#")
                # the attachment field returns a dictionary
                elif field == "attachment":
                    try:
                        item_info.append(item.get(field)['download'])
                    except:
                        item_info.append("")
                else:
                    # when writing values, check for the lists and turn them into string
                    write_value = item.get(field, '')
                    if isinstance(write_value, list):
                        write_value = ','.join(write_value)
                    item_info.append(write_value)
            all_items.append(item_info)
        return all_items
    else:  # pragma: no cover
        return


def order_FDN(input_xls, connection):
    """Order and filter created xls file."""
    ReadFile = input_xls
    OutputFile = input_xls[:-4]+'_ordered.xls'
    bookread = xlrd.open_workbook(ReadFile)
    book_w = xlwt.Workbook()
    Sheets_read = bookread.sheet_names()
    Sheets = []
    # text styling for all columns
    style = xlwt.XFStyle()
    style.num_format_str = "@"
    # reorder sheets based on sheet_order list and report if there are missing one from this list
    for sh in sheet_order:
        if sh in Sheets_read:
            Sheets.append(sh)
            Sheets_read.remove(sh)
    if Sheets_read:  # pragma: no cover
        print(Sheets_read, "not in sheet_order list, please update")
        Sheets.extend(Sheets_read)
    for sheet in Sheets:
        useful = []
        active_sheet = bookread.sheet_by_name(sheet)
        first_row_values = active_sheet.row_values(rowx=0)
        # remove items from fields in xls
        useful = filter_and_sort(first_row_values)
        # move selected to front
        useful = move_to_frond(useful)
        # move selected to end
        useful = move_to_end(useful)
        # reorder some items based on reorder list
        useful = switch_fields(useful, sheet)
        # fetch all items for common objects
        all_items = fetch_all_items(sheet, useful, connection)
        # create a new sheet and write the data
        new_sheet = book_w.add_sheet(sheet)
        for write_row_index, write_item in enumerate(useful):
            read_col_ind = first_row_values.index(write_item)
            column_val = active_sheet.col_values(read_col_ind)
            for write_column_index, cell_value in enumerate(column_val):
                new_sheet.write(write_column_index, write_row_index, cell_value, style)
        # write common objects
        if all_items:
            for i, item in enumerate(all_items):
                for ix in range(len(useful)):
                    write_column_index_II = write_column_index+1+i
                    new_sheet.write(write_column_index_II, ix, str(item[ix]), style)
        else:
            write_column_index_II = write_column_index
        # write 50 empty lines with text formatting
        for i in range(100):
            for ix in range(len(useful)):
                write_column_index_III = write_column_index_II+1+i
                new_sheet.write(write_column_index_III, ix, '', style)
    book_w.save(OutputFile)
############################################################
############################################################
############################################################
############################################################
