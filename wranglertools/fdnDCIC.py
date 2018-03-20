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

    def set_award(self, lab, dontPrompt=True):
        '''Sets the award for the connection for use in import_data
           if dontPrompt is False will ask the User to choose if there
           are more than one award for the connection.lab otherwise
           the first award for the lab will be used
        '''
        lab_url = self.server + lab + '?frame=embedded'
        lab_resp = requests.get(lab_url, auth=self.auth)
        try:
            labjson = lab_resp.json()
            if labjson.get('awards') is not None:
                awards = labjson.get('awards')
                if dontPrompt:
                    self.award = awards[0]['@id']
                    return
                else:
                    if len(awards) == 1:
                        self.award = awards[0]['@id']
                        return
                    else:
                        achoices = []
                        print("Multiple awards for {labname}:".format(labname=lab))
                        for i, awd in enumerate(awards):
                            ch = str(i + 1)
                            achoices.append(ch)
                            print("  ({choice}) {awdname}".format(choice=ch, awdname=awd['@id']))
                        awd_resp = str(input("Select the award for this session {choices}: ".format(choices=achoices)))
                        if awd_resp not in achoices:
                            print("Not a valid choice - using {default}".format(default=awards[0]['@id']))
                            return
                        else:
                            self.award = awards[int(awd_resp) - 1]['@id']
                            return
            else:
                self.award = None
        except:
            if not self.award:  # only reset if not already set
                self.award = None

    def __init__(self, key):
        self.headers = {'content-type': 'application/json', 'accept': 'application/json'}
        self.server = key.server
        if (key.authid, key.authpw) == ("", ""):
            self.auth = ()
        else:
            self.auth = (key.authid, key.authpw)
        self.check = False
        # check connection and find user uuid
        me_page = self.server + 'me' + '?frame=embedded'
        r = requests.get(me_page, auth=self.auth)
        if r.status_code == 307:
            self.check = True
            res = r.json()
            self.user = res['@id']
            self.email = res['email']

            if res.get('submits_for') is not None:
                # get all the labs that the user making the connection submits_for
                self.labs = [l['link_id'].replace("~", "/") for l in res['submits_for']]
                # take the first one as default value for the connection - reset in
                # import_data if needed by calling set_lab_award
                self.lab = self.labs[0]
                self.set_award(self.lab)  # set as default first
            else:
                self.labs = None
                self.lab = None
                self.award = None

    def prompt_for_lab_award(self):
        '''Check to see if user submits_for multiple labs or the lab
            has multiple awards and if so prompts for the one to set
            for the connection
        '''
        if self.labs:
            if len(self.labs) > 1:
                lchoices = []
                print("Submitting for multiple labs:")
                for i, lab in enumerate(self.labs):
                    ch = str(i + 1)
                    lchoices.append(ch)
                    print("  ({choice}) {labname}".format(choice=ch, labname=lab))
                lab_resp = str(input("Select the lab for this connection {choices}: ".format(choices=lchoices)))
                if lab_resp not in lchoices:
                    print("Not a valid choice - using {default}".format(default=self.lab))
                    return
                else:
                    self.lab = self.labs[int(lab_resp) - 1]

        self.set_award(self.lab, False)


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
    elif url_addon is not None:  # pragma: no cover
        return connection.server + url_addon


def format_to_json(input_data):
    json_payload = {}
    if isinstance(input_data, dict):
        json_payload = json.dumps(input_data)
    elif isinstance(input_data, str):
        json_payload = input_data
    else:  # pragma: no cover
        print('Datatype is not string or dict. (format_to_json)')
    return json_payload


def get_FDN(obj_id, connection, frame="object", url_addon=None):
    '''GET an FDN object, collection or search result as JSON and
        return as dict or list of dicts for objects, and collection
        or search, respectively.
        Since we check if an object exists with this method, the logging is disabled for 404.
    '''
    if obj_id is not None:
        url = FDN_url(obj_id, connection, frame)
    elif url_addon is not None:
        url = FDN_url(None, connection, None, url_addon)
    response = requests.get(url, auth=connection.auth, headers=connection.headers)
    if response.status_code not in [200, 404]:  # pragma: no cover
        try:
            logging.warning('%s' % (response.json().get("notification")))
        except:
            logging.warning('%s' % (response.text))
    if url_addon and response.json().get('@graph'):  # pragma: no cover
        return response.json()['@graph']
    return response.json()


def search_FDN(sheet, field, value, connection):
    '''When there is a conflict in a field that should be unique, pass
    sheet, field, unique value, and find the already exisint object.
    '''
    obj_id = "search/?type={sheet}&{field}={value}".format(sheet=sheet, field=field, value=value)
    url = FDN_url(obj_id, connection, frame="object")
    response = requests.get(url, auth=connection.auth, headers=connection.headers)
    if not response.status_code == 200:  # pragma: no cover
        try:
            logging.warning('%s' % (response.json().get("notification")))
        except:
            logging.warning('%s' % (response.text))
    if response.json().get('@graph'):
        return response.json()['@graph']
    return response.json()


def patch_FDN(obj_id, connection, patch_input):
    '''PATCH an existing FDN object and return the response JSON
    '''
    json_payload = format_to_json(patch_input)
    url = connection.server + obj_id
    response = requests.patch(url, auth=connection.auth, data=json_payload, headers=connection.headers)
    if not response.status_code == 200:  # pragma: no cover
        try:
            logging.debug('%s' % (response.json().get("notification")))
        except:
            logging.debug('%s' % (response.text))
    return response.json()


def put_FDN(obj_id, connection, put_input):
    '''PUT an existing FDN object and return the response JSON'''
    json_payload = format_to_json(put_input)
    url = connection.server + obj_id
    response = requests.put(url, auth=connection.auth, data=json_payload, headers=connection.headers)
    if not response.status_code == 200:  # pragma: no cover
        try:
            logging.debug('%s' % (response.json().get("notification")))
        except:
            logging.debug('%s' % (response.text))
    return response.json()


def new_FDN(connection, collection_name, post_input):
    '''POST an FDN object as JSON and return the response JSON'''
    json_payload = format_to_json(post_input)
    url = connection.server + collection_name
    response = requests.post(url, auth=connection.auth, headers=connection.headers, data=json_payload)
    if not response.status_code == 201:  # pragma: no cover
        try:
            logging.debug('%s' % (response.json().get("notification")))
        except:
            logging.debug('%s' % (response.text))
    return response.json()


def new_FDN_check(connection, collection_name, post_input):
    '''Test POST an FDN object as JSON and return the response JSON'''
    json_payload = format_to_json(post_input)
    url = connection.server + collection_name + "/?check_only=True"
    response = requests.post(url, auth=connection.auth, headers=connection.headers, data=json_payload)
    return response.json()


def patch_FDN_check(obj_id, connection, patch_input):
    '''Test PATCH an existing FDN object and return the response JSON'''
    json_payload = format_to_json(patch_input)
    url = connection.server + obj_id + "/?check_only=True"
    response = requests.patch(url, auth=connection.auth, data=json_payload, headers=connection.headers)
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
    "GenomicRegion", "Target", "Antibody", "Modification", "Image", "BiosampleCellCulture", "Biosample",
    "FileFastq", "FileFasta", "FileProcessed", "FileReference", "FileCalibration",
    "FileSet", "FileSetCalibration", "MicroscopeSettingD1", "MicroscopeSettingD2",
    "MicroscopeSettingA1", "MicroscopeSettingA2", "FileMicroscopy", "FileSetMicroscopeQc",
    "ImagingPath", "ExperimentMic", "ExperimentMic_Path",
    "ExperimentHiC", "ExperimentCaptureC", "ExperimentRepliseq", "ExperimentAtacseq", "ExperimentChiapet",
    "ExperimentDamid", "ExperimentSeq", "ExperimentSet", "ExperimentSetReplicate", 'WorkflowRunSbg',
    'WorkflowRunAwsem',
    ]

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
    ['Enzyme', 'catalog_number', 'documents'],
    ['Enzyme', 'recognition_sequence', 'documents'],
    ['Enzyme', 'site_length', 'documents'],
    ['Enzyme', 'cut_position', 'documents'],
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
    "Document": "document",
    "Protocol": "protocol",
    "Enzyme": "enzyme",
    "Biosource": "biosource",
    "Publication": "publication",
    "Vendor": "vendor"
    }


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
        except:  # pragma: no cover
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

        # order items with lab and user
        # the date ordering is already in place through search result (resp)
        # 1) order by dcic lab
        items_list = sort_item_list(items_list, '/lab/dcic-lab/', 'lab')
        # 2) sort by submitters lab
        items_list = sort_item_list(items_list, connection.lab, 'lab')
        # 3) sort by submitters user
        items_list = sort_item_list(items_list, connection.user, 'submitted_by')
        # 4) If biosurce, also sort by tier
        if sheet == "Biosource":
            items_list = sort_item_list(items_list, 'Tier 1', 'cell_line_tier')

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
