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
        self.error = False
        # is the keyfile a dictionary
        if isinstance(keyfile, dict):
            keys = keyfile
        # is the keyfile a file (the expected case)
        elif os.path.isfile(str(keyfile)):
            keys_f = open(keyfile, 'r')
            keys_json_string = keys_f.read()
            keys_f.close()
            keys = json.loads(keys_json_string)
        # if both fail, the file does not exist
        else:
            print("\nThe keyfile does not exist, check the --keyfile path or add 'keypairs.json' to your home folder\n")
            self.error = True
            return
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
        # check connection and find user uuid
        me_page = self.server + 'me' + '?frame=embedded'
        r = requests.get(me_page, auth=self.auth)
        self.check = False
        if r.status_code == 307:  # pragma: no cover
            self.check = True
            res = r.json()
            self.user = res['@id']
            self.email = res['email']
            try:
                self.lab = res['submits_for'][0]['link_id'].replace("~", "/")
                lab_url = self.server + self.lab + '?frame=embedded'
                r_lab = requests.get(lab_url, auth=self.auth)
                res_lab = r_lab.json()
                self.award = res_lab['awards'][0]['link_id'].replace("~", "/")
            except:
                # to catch possible gaps in the code
                self.lab = None
                self.award = None


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


def FDN_url(obj_id, connection, frame, url_addon=None):
    '''Generate a URL from connection info for a specific item by using an
        object id (accession, uuid or unique_key) or for a collection of items
        using the collection name (eg. biosamples or experiments-hi-c) or a
        search by providing a search suffix addon (eg. search/?type=OntologyTerm).
    '''
    if obj_id is not None:
        if frame is None:
            if '?' in obj_id:
                url = connection.server + obj_id + '&limit=all'
            else:
                url = connection.server + obj_id + '?limit=all'
        elif '?' in obj_id:
            url = connection.server + obj_id + '&limit=all&frame=' + frame
        else:
            url = connection.server + obj_id + '?limit=all&frame=' + frame
        return url
    elif url_addon is not None:
        return connection.server + url_addon


def get_FDN(obj_id, connection, frame="object", url_addon=None):
    '''GET an FDN object, collection or search result as JSON and
        return as dict or list of dicts for objects, and collection
        or search, respectively.
    '''
    if obj_id is not None:
        url = FDN_url(obj_id, connection, frame)
    elif url_addon is not None:
        url = FDN_url(None, connection, None, url_addon)
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
    if url_addon is not None and response.json().get('@graph'):
        return response.json()['@graph']
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
    "FileFastq", "FileFasta", "FileProcessed", "FileReference", "FileSet", "ExperimentHiC", "ExperimentCaptureC",
    "ExperimentRepliseq", "ExperimentSet", "ExperimentSetReplicate"]

# Most fields are covered by "exclude_from:submit4dn" tag for removal
# do_not_use list can be populated if there are additional fields that nneds to be taken out
do_not_use = ["filesets", "status"]


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

move_front = ['experiment_set', '*tec_rep_no', '*bio_rep_no', '*replicate_set',
              'description', 'title', '*title', 'name', '*name', 'aliases', '#Field Name:']


def move_to_front(list_names):
    """Move names front"""
    for front in move_front:
        try:
            list_names.remove(front)
            list_names.insert(0, front)
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
    "Document": "document", "Protocol": "protocol", "Enzyme": "enzyme", "Biosource": "biosource",
    "Publication": "publication", "Vendor": "vendor"}


def sort_item_list(item_list, item_id, field):
    """Sort all items in list alphabetically based on values in the given field and bring item_id to beginning."""
    # sort all items based on the key
    sorted_list = sorted(item_list, key=lambda k: ("" if k.get(field) is None else k.get(field)))
    # move the item_id ones to the front
    move_list = [i for i in sorted_list if i.get(field) == item_id]
    move_list.reverse()
    for move_item in move_list:
        try:
            sorted_list.remove(move_item)
            sorted_list.insert(0, move_item)
        except:
            pass
    return sorted_list


def fetch_all_items(sheet, field_list, connection):
    """For a given sheet, get all released items"""
    all_items = []
    if sheet in fetch_items.keys():
        # Search all items, get uuids, get them one by one
        obj_id = "search/?type=" + fetch_items[sheet]
        resp = get_FDN(obj_id, connection)
        items_uuids = [i["uuid"] for i in resp['@graph']]
        items_list = []
        for item_uuid in items_uuids:
            items_list.append(get_FDN(item_uuid, connection))
        # order items with lab and user (Lab (1-user_lab 2-dcic_lab), User
        # the date ordering is already in place through search result (resp)
        items_list = sort_item_list(items_list, '/lab/dcic-lab/', 'lab')
        items_list = sort_item_list(items_list, connection.lab, 'lab')
        items_list = sort_item_list(items_list, connection.user, 'submitted_by')
        # filter for fields that exist on the excel sheet
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
        useful = move_to_front(useful)
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
