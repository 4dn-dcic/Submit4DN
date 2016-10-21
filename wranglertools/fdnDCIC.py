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


def get_FDN(obj_id, connection, frame="object"):
    '''GET an FDN object as JSON and return as dict'''
    if frame is None:
        if '?' in obj_id:
            url = connection.server + obj_id+'&limit=all'
        else:
            url = connection.server + obj_id+'?limit=all'
    elif '?' in obj_id:
        url = connection.server + obj_id+'&limit=all&frame='+frame
    else:
        url = connection.server + obj_id+'?limit=all&frame='+frame
    logging.debug('GET %s' % (url))
    response = requests.get(url, auth=connection.auth, headers=connection.headers)
    logging.debug('GET RESPONSE code %s' % (response.status_code))
    try:
        if response.json():
            logging.debug('GET RESPONSE JSON: %s' %
                          (json.dumps(response.json(), indent=4, separators=(',', ': '))))
    except:
        logging.debug('GET RESPONSE text %s' % (response.text))
    if not response.status_code == 200:
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
    else:
        print('Datatype to PATCH is not string or dict.')
    url = connection.server + obj_id
    logging.debug('PATCH URL : %s' % (url))
    logging.debug('PATCH data: %s' % (json_payload))
    response = requests.patch(url, auth=connection.auth, data=json_payload,
                              headers=connection.headers)
    logging.debug('PATCH RESPONSE: %s' % (json.dumps(response.json(), indent=4,
                                                     separators=(',', ': '))))
    if not response.status_code == 200:
        logging.warning('PATCH failure.  Response = %s' % (response.text))
    return response.json()


def new_FDN(connection, collection_name, post_input):
    '''POST an FDN object as JSON and return the response JSON
    '''
    if isinstance(post_input, dict):
        json_payload = json.dumps(post_input)
    elif isinstance(post_input, str):
        json_payload = post_input
    else:
        print('Datatype to POST is not string or dict.')
    url = connection.server + collection_name
    logging.debug("POST URL : %s" % (url))
    logging.debug("POST data: %s" % (json.dumps(post_input,
                                     sort_keys=True, indent=4,
                                     separators=(',', ': '))))
    response = requests.post(url, auth=connection.auth,
                             headers=connection.headers, data=json_payload)
    logging.debug("POST RESPONSE: %s" % (json.dumps(response.json(),
                                         indent=4, separators=(',', ': '))))
    if not response.status_code == 201:
        logging.warning('POST failure. Response = %s' % (response.text))
    logging.debug("Return object: %s" % (json.dumps(response.json(),
                                         sort_keys=True, indent=4,
                                         separators=(',', ': '))))
    return response.json()


def md5(path):
    md5sum = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            md5sum.update(chunk)
    return md5sum.hexdigest()


sheet_order = [
    "User",
    "Award",
    "Lab",
    "Document",
    "Protocol",
    "Publication",
    "Organism",
    "IndividualMouse",
    "IndividualHuman",
    "Vendor",
    "Biosource",
    "Construct",
    "TreatmentRnai",
    "TreatmentChemical",
    "GenomicRegion",
    "Target",
    "Modification",
    "Image",
    "BiosampleCellCulture",
    "Biosample",
    "Enzyme",
    "FileSet",
    "FileFastq",
    "FileFasta",
    "ExperimentSet",
    "ExperimentHiC",
    "ExperimentCaptureC"
]


def order_FDN(input_xls):
    """Order and filter created xls file."""

    do_not_use = [
        "submitted_by",
        "date_created",
        "organism",
        "schema_version",
        "accession",
        "uuid",
        "status",
        "quality_metric_flags",
        "notes",
        "restricted",
        "file_size",
        "filename",
        "alternate_accessions",
        "content_md5sum",
        "md5sum",
        "quality_metric",
        "files_in_set",
        "experiments",
        "experiments_in_set"
    ]

    move_frond = [
        'award',
        '*award',
        'lab',
        '*lab',
        'description',
        'title',
        '*title',
        'name',
        '*name',
        'aliases',
        '#Field Name:'
    ]

    move_end = [
        'documents',
        'references',
        'url',
        'dbxrefs'
    ]

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
        ['Experiment', 'experiment_relation.experiment', 'documents'],
        ['Experiment', 'experiment_sets|0', 'documents'],
        ['Experiment', 'experiment_sets|1', 'documents'],
        ['Experiment', 'experiment_sets|2', 'documents'],
        ['Experiment', 'experiment_sets|3', 'documents'],

    ]

    ReadFile = input_xls
    OutputFile = input_xls[:-4]+'_ordered.xls'
    bookread = xlrd.open_workbook(ReadFile)
    book_w = xlwt.Workbook()
    Sheets_read = bookread.sheet_names()
    Sheets = []
    # reorder sheets based on sheet_order list and report if there are missing one from this list
    for sh in sheet_order:
        if sh in Sheets_read:
            Sheets.append(sh)
            Sheets_read.remove(sh)
    if Sheets_read:
        print(Sheets_read, "not in sheet_order list, please update")
        Sheets.extend(Sheets_read)

    for sheet in Sheets:
        useful = []
        active_sheet = bookread.sheet_by_name(sheet)
        first_row_values = active_sheet.row_values(rowx=0)
        for field in first_row_values:
            if field in do_not_use:
                pass
            else:
                useful.append(field)
        useful = sorted(useful)
        # move selected to front
        for frond in move_frond:
            try:
                useful.remove(frond)
                useful.insert(0, frond)
            except:
                pass
        # move selected to end
        for end in move_end:
            try:
                useful.pop(useful.index(end))
                useful.append(end)
            except:
                pass
        # reorder some items based on reorder list
        for sort_case in reorder:
            if sort_case[0] in sheet:
                try:
                    useful.remove(sort_case[1])
                    useful.insert(useful.index(sort_case[2]), sort_case[1])
                except:
                    pass
        # create a new sheet and write the data
        new_sheet = book_w.add_sheet(sheet)
        for write_row_index, write_item in enumerate(useful):
            read_col_ind = first_row_values.index(write_item)
            column_val = active_sheet.col_values(read_col_ind)
            # column_val.pop(2)
            for write_column_index, cell_value in enumerate(column_val):
                new_sheet.write(write_column_index, write_row_index, cell_value)
    book_w.save(OutputFile)
