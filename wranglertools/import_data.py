#!/usr/bin/env python3
# -*- coding: latin-1 -*-
"""See the epilog for detailed information."""
import json
import argparse
import os.path
from wranglertools import fdnDCIC
from wranglertools.fdnDCIC import md5
from wranglertools.fdnDCIC import sheet_order
import xlrd
import datetime
import sys
import mimetypes
import requests
from PIL import Image
from base64 import b64encode
import magic  # install me with 'pip install python-magic'
# https://github.com/ahupp/python-magic
# this is the site for python-magic in case we need it
import attr
import os
import time
import subprocess

EPILOG = '''
This script takes in an Excel file with the data
This is a dryrun-default script, run with --update, --patchall or both (--update --patchall) to work

By DEFAULT:
If there is a uuid, @id, accession, or previously submitted alias in the document:
it will ask if you want to PATCH that object
Use '--patchall' if you want to patch ALL objects in your document and ignore that message

If you want to upload new items(no object identifiers are found), in the document you need to use '--update'
for POSTing to occur

Defining Object type:
    Each "sheet" of the excel file is named after the object type you are uploading,
    with the format used on http://data.4dnucleome.org//profiles/
Ex: ExperimentHiC, Biosample, Document, Target

If there is a single sheet that needs to be posted or patched, you can name the single sheet
with the object name and use the '--type' argument
Ex: %(prog)s mydata.xsls --type ExperimentHiC

The header of each sheet should be the names of the fields.
Ex: award, lab, target, etc.

To upload objects with attachments, use the column titled "attachment"
containing the full path to the file you wish to attach

For more details:
please see README.rst

'''


def getArgs():  # pragma: no cover
    parser = argparse.ArgumentParser(
        description=__doc__, epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument('infile',
                        help="the datafile containing object data to import")
    parser.add_argument('--type',
                        help="the type of the objects to import")
    parser.add_argument('--key',
                        default='default',
                        help="The keypair identifier from the keyfile.  \
                        Default is --key=default")
    parser.add_argument('--keyfile',
                        default=os.path.expanduser("~/keypairs.json"),
                        help="The keypair file.  Default is --keyfile=%s" %
                             (os.path.expanduser("~/keypairs.json")))
    parser.add_argument('--debug',
                        default=False,
                        action='store_true',
                        help="Print debug messages.  Default is False.")
    parser.add_argument('--update',
                        default=False,
                        action='store_true',
                        help="Let the script PATCH the data.  Default is False"),
    parser.add_argument('--patchall',
                        default=False,
                        action='store_true',
                        help="PATCH existing objects.  Default is False \
                        and will only PATCH with user override"),
    parser.add_argument('--remote',
                        default=False,
                        action='store_true',
                        help="will skip attribution prompt \
                        needed for automated submissions")
    args = parser.parse_args()
    return args

# list of [sheet, [fields]] that need to be patched as a second step
# should be in sync with loadxl.py in fourfront
list_of_loadxl_fields = [
    ['Document', ['references']],
    ['User', ['lab', 'submits_for']],
    ['ExperimentHiC', ['experiment_relation']],
    ['ExperimentCaptureC', ['experiment_relation']],
    ['FileFastq', ['related_files']],
    ['FileFasta', ['related_files']],
    ['Publication', ['exp_sets_prod_in_pub', 'exp_sets_used_in_pub']]
]


def attachment(path):
    """Create an attachment upload object from a filename and embed the attachment as a data url."""
    if not os.path.isfile(path):
        # if the path does not exist, check if it works as a URL
        try:
            r = requests.get(path)
        except requests.exceptions.MissingSchema:
            print("\nERROR : The 'attachment' field contains INVALID FILE PATH or URL ({})\n".format(path))
            sys.exit(1)
        # if it works as a URL, but does not return 200
        if r.status_code is not 200:
            print("\nERROR : The 'attachment' field contains INVALID URL ({})\n".format(path))
            sys.exit(1)
        # parse response
        path = path.split("/")[-1]
        with open(path, "wb") as outfile:
            outfile.write(r.content)
    filename = os.path.basename(path)
    mime_type, encoding = mimetypes.guess_type(path)
    major, minor = mime_type.split('/')
    detected_type = magic.from_file(path, mime=True)
    # XXX This validation logic should move server-side.
    if not (detected_type == mime_type or
            detected_type == 'text/plain' and major == 'text'):
        raise ValueError('Wrong extension for %s: %s' % (detected_type, filename))
    with open(path, 'rb') as stream:
        attach = {
            'download': filename,
            'type': mime_type,
            'href': 'data:%s;base64,%s' % (mime_type, b64encode(stream.read()).decode('ascii'))}
        if mime_type in ('application/pdf', 'text/plain', 'text/tab-separated-values', 'text/html'):
            # XXX Should use chardet to detect charset for text files here.
            return attach
        if major == 'image' and minor in ('png', 'jpeg', 'gif', 'tiff'):
            # XXX we should just convert our tiffs to pngs
            stream.seek(0, 0)
            im = Image.open(stream)
            im.verify()
            if im.format != minor.upper():  # pragma: no cover
                msg = "Image file format %r does not match extension for %s"
                raise ValueError(msg % (im.format, filename))
            attach['width'], attach['height'] = im.size
            return attach
    raise ValueError("Unknown file type for %s" % filename)


def reader(filename, sheetname=None):
    """Read named sheet or first and only sheet from xlsx file."""
    book = xlrd.open_workbook(filename)
    if sheetname is None:
        sheet, = book.sheets()
    else:
        try:
            sheet = book.sheet_by_name(sheetname)
        except xlrd.XLRDError:
            return
    datemode = sheet.book.datemode
    for index in range(sheet.nrows):
        yield [cell_value(cell, datemode) for cell in sheet.row(index)]


def cell_value(cell, datemode):
    """Get cell value from excel."""
    ctype = cell.ctype
    value = cell.value

    if ctype == xlrd.XL_CELL_ERROR:  # pragma: no cover
        raise ValueError(repr(cell), 'cell error')

    elif ctype == xlrd.XL_CELL_BOOLEAN:
        return str(value).upper()

    elif ctype == xlrd.XL_CELL_NUMBER:
        if value.is_integer():
            value = int(value)
        return str(value)

    elif ctype == xlrd.XL_CELL_DATE:
        value = xlrd.xldate_as_tuple(value, datemode)
        if value[3:] == (0, 0, 0):
            return datetime.date(*value[:3]).isoformat()
        else:  # pragma: no cover
            return datetime.datetime(*value).isoformat()

    elif ctype in (xlrd.XL_CELL_TEXT, xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK):
        return value

    raise ValueError(repr(cell), 'unknown cell type')  # pragma: no cover


def data_formatter(value, val_type, field=None):
    """Return formatted data."""
    try:
        if val_type in ["int", "integer"]:
            return int(value)
        elif val_type in ["num", "number"]:
            return float(value)
        elif val_type in ["list", "array"]:
            data_list = value.strip("[\']").split(",")
            return [data.strip() for data in data_list]
        else:
            # default assumed to be string
            return str(value)
    except ValueError:
        print("Field '{}' contains value '{}' which is not of type {}".format(field, value, val_type.upper()))
        return


def get_field_name(field_name):
    """handle type at end, plus embedded objets."""
    field = field_name.replace('*', '')
    field = field.split(':')[0]
    return field.split(".")[0]


def get_sub_field(field_name):
    """Construct embeded field names."""
    try:
        return field_name.split(".")[1].rstrip('-0123456789')
    except:  # pragma: no cover
        return ''


def get_field_type(field_name):
    """Grab old style (ENCODE) data field type."""
    try:
        return field_name.split(":")[1]
    except:
        return "string"


def is_embedded_field(field_name):
    """See if field is embedded."""
    return '.' in field_name


def get_sub_field_number(field_name):
    """Name clearing for multiple objects."""
    field_name = field_name.replace('*', '')
    field = field_name.split(":")[0]
    try:
        return int(field.split("-")[1])
    except:
        return 0


@attr.s
class FieldInfo(object):
    name = attr.ib()
    field_type = attr.ib(default=u'')
    value = attr.ib(default=u'')


def build_field(field, field_data, field_type):
    if not field_data or not field:
        return None
    patch_field_name = get_field_name(field)
    if not field_type:
        field_type = get_field_type(field)
    if is_embedded_field(field):
        sub_field = get_sub_field(field)
        return build_field(sub_field, field_data, 'string')
    else:
        patch_field_data = data_formatter(field_data, field_type, field)
    return {patch_field_name: patch_field_data}


def build_patch_json(fields, fields2types):
    """Create the data entry dictionary from the fields."""
    # convert array types to array
    for field, ftype in fields2types.items():
        if 'array' in ftype:
            fields2types[field] = 'array'

    patch_data = {}
    for field, field_data in fields.items():
        field_type = None
        if fields2types is not None:
            field_type = fields2types[field]

        patch_field = build_field(field, field_data, field_type)
        if patch_field is not None:
            if is_embedded_field(field):
                top_field = get_field_name(field)
                if patch_data.get(top_field, None) is None:
                    # initially create an empty list for embedded field
                    patch_data[top_field] = []
                # we can have multiple embedded objects (they are numbered in excel)
                subobject_num = get_sub_field_number(field)

                if subobject_num >= len(patch_data[top_field]):
                    # add a new row to the list
                    patch_data[top_field].append(patch_field)
                else:
                    # update existing object in the list
                    patch_data[top_field][subobject_num].update(patch_field)
            else:
                # normal case, just update the dictionary
                patch_data.update(patch_field)

    return patch_data


def get_existing(post_json, connection):
    """Get the entry that will be patched from the server."""
    temp = {}
    if post_json.get("uuid"):
        temp = fdnDCIC.get_FDN(post_json["uuid"], connection)
    elif post_json.get("aliases"):
        temp = fdnDCIC.get_FDN(post_json["aliases"][0], connection)
    elif post_json.get("accession"):
        temp = fdnDCIC.get_FDN(post_json["accession"], connection)
    elif post_json.get("@id"):
        temp = fdnDCIC.get_FDN(post_json["@id"], connection)
    return temp


def filter_set_from_exps(post_json):
    """Experiments set information is taken from experiments and submitted to experiment_set."""
    rep_set_info = []
    exp_set_info = []
    # Part I - Replicate Sets
    # store the values in a list and delete them from post_json
    if post_json.get('replicate_set'):
        for replicate_field in ['replicate_set', 'bio_rep_no', 'tec_rep_no']:
            rep_set_info.append(post_json[replicate_field])
            post_json.pop(replicate_field)
    # Part II - Experiment Sets
    if post_json.get('experiment_set'):
        exp_set_info = post_json['experiment_set']
        post_json.pop('experiment_set')
    return post_json, rep_set_info, exp_set_info


def filter_set_from_files(post_json):
    """File set information is taken from files."""
    file_set_info = []
    # store the values in a list and delete them from post_json
    if post_json.get('filesets'):
        file_set_info = post_json['filesets']
        post_json.pop('filesets')
    return post_json, file_set_info


def filter_loadxl_fields(post_json, sheet):
    """All fields from the list_of_loadxl_fields are taken out of post_json and accumulated in dictionary."""
    patch_loadxl_item = {}
    for sheet_loadxl, fields_loadxl in list_of_loadxl_fields:
        if sheet == sheet_loadxl:
            for field_loadxl in fields_loadxl:
                if post_json.get(field_loadxl):
                    patch_loadxl_item[field_loadxl] = post_json[field_loadxl]
                    del post_json[field_loadxl]
    return post_json, patch_loadxl_item


def combine_set(post_json, existing_data, sheet, accumulate_dict):
    """Combine experiment related information form dictionaries with existing information."""
    # find all identifiers from exisiting set item to match the one used in experiments sheet
    identifiers = []
    for identifier in ['accession', 'uuid', 'aliases', '@id']:
        ex_item_id = existing_data.get(identifier, '')
        item_id = post_json.get(identifier, ex_item_id)
        # to extract alias from list
        if isinstance(item_id, list) and item_id:
            item_id = item_id[0]
        if item_id:
            identifiers.append(item_id)
    # search dictionary for the existing item id
    for identifier in identifiers:
        if accumulate_dict.get(identifier):
            add_to_post = accumulate_dict.get(identifier)
            # Combination for experimentsets
            if sheet == "ExperimentSet":
                if existing_data.get('experiments_in_set'):
                    existing_exps = existing_data.get('experiments_in_set')
                    post_json['experiments_in_set'] = list(set(add_to_post + existing_exps))
                else:
                    post_json['experiments_in_set'] = add_to_post
            # Combination for replicate sets
            if sheet == "ExperimentSetReplicate":
                if existing_data.get('replicate_exps'):
                    existing_sets = existing_data.get('replicate_exps')
                    new_exps = [i['replicate_exp'] for i in add_to_post]
                    existing_sets = [i for i in existing_sets if i['replicate_exp'] not in new_exps]
                    post_json['replicate_exps'] = add_to_post + existing_sets
                else:
                    post_json['replicate_exps'] = add_to_post
            # Combination for filesets
            if sheet == "FileSet":
                if existing_data.get('files_in_set'):
                    existing_files = existing_data.get('files_in_set')
                    post_json['files_in_set'] = list(set(add_to_post + existing_files))
                else:
                    post_json['files_in_set'] = add_to_post
            # remove found item from the accumulate_dict
            accumulate_dict.pop(identifier)
            break
    return post_json, accumulate_dict


def fix_attribution(sheet, post_json, connection):
    if sheet.lower() not in ['lab', 'award', 'user', 'organism']:
        if not post_json.get('lab'):
            post_json['lab'] = connection.lab
        if not post_json.get('award'):
            post_json['award'] = connection.award
    return post_json


def excel_reader(datafile, sheet, update, connection, patchall,
                 dict_patch_loadxl, dict_replicates, dict_exp_sets, dict_file_sets):
    """takes an excel sheet and post or patched the data in."""
    # dict for acumulating cycle patch data
    patch_loadxl = []
    row = reader(datafile, sheetname=sheet)
    keys = next(row)  # grab the first row of headers
    types = next(row)  # grab second row with type info
    # remove title column
    keys.pop(0)
    types.pop(0)
    fields2types = dict(zip(keys, types))
    # set counters to 0
    total = 0
    error = 0
    success = 0
    patch = 0
    not_patched = 0
    # iterate over the rows
    for values in row:
        # Rows that start with # are skipped
        if values[0].startswith("#"):
            continue
        # Get rid of the first empty cell
        values.pop(0)
        total += 1
        post_json = dict(zip(keys, values))
        post_json = build_patch_json(post_json, fields2types)
        # add attchments here
        if post_json.get("attachment"):
            attach = attachment(post_json["attachment"])
            post_json["attachment"] = attach

        # Get existing data if available
        existing_data = get_existing(post_json, connection)

        # should I upload files as well?
        file_to_upload = False
        filename_to_post = post_json.get('filename')
        if filename_to_post:
            # remove full path from filename
            just_filename = filename_to_post.split('/')[-1]
            # if new file
            if not existing_data:
                post_json['filename'] = just_filename
                file_to_upload = True
            # if there is an existing file metadata, the status should be uploading
            if existing_data.get('status') == 'uploading':
                post_json['filename'] = just_filename
                file_to_upload = True

        # if no existing data (new item), add missing award/lab information from submitter
        if not existing_data.get("award"):
            post_json = fix_attribution(sheet, post_json, connection)
        # Filter loadxl fields
        post_json, patch_loadxl_item = filter_loadxl_fields(post_json, sheet)
        # Filter experiment set related fields from experiment
        if sheet.startswith('Experiment') and not sheet.startswith('ExperimentSet'):
            post_json, rep_set_info, exp_set_info = filter_set_from_exps(post_json)
        # Filter file set related fields from file
        if sheet.startswith('File') and not sheet.startswith('FileSet'):
            post_json, file_set_info = filter_set_from_files(post_json)
        # Combine set items with stored dictionaries
        if sheet == 'ExperimentSet':
            post_json, dict_exp_sets = combine_set(post_json, existing_data, sheet, dict_exp_sets)
        if sheet == 'ExperimentSetReplicate':
            post_json, dict_replicates = combine_set(post_json, existing_data, sheet, dict_replicates)
        if sheet == 'FileSet':
            post_json, dict_file_sets = combine_set(post_json, existing_data, sheet, dict_file_sets)

        # Run update or patch
        e = {}
        flow = ''
        if existing_data.get("uuid"):
            if not patchall:
                not_patched += 1
            if patchall:
                # add the md5
                if file_to_upload and not post_json.get('md5sum'):
                    print("calculating md5 sum for file %s " % (filename_to_post))
                    post_json['md5sum'] = md5(filename_to_post)

                e = fdnDCIC.patch_FDN(existing_data["uuid"], connection, post_json)
                if file_to_upload:
                    # get s3 credentials
                    creds = get_upload_creds(e['@graph'][0]['accession'], connection, e['@graph'][0])
                    e['@graph'][0]['upload_credentials'] = creds
                    # upload
                    upload_file(e, filename_to_post)
                flow = 'patch'
        else:
            if update:
                # add the md5
                if file_to_upload and not post_json.get('md5sum'):
                    print("calculating md5 sum for file %s " % (filename_to_post))
                    post_json['md5sum'] = md5(filename_to_post)
                e = fdnDCIC.new_FDN(connection, sheet, post_json)
                if file_to_upload:
                    # upload the file
                    upload_file(e, filename_to_post)
            else:
                print("This looks like a new row but the update flag wasn't passed, use --update to"
                      " post new data")
                return

        # check status and if success fill transient storage dictionaries
        if e.get("status") == "error":  # pragma: no cover
            error += 1
        elif e.get("status") == "success":
            success += 1
            if flow == 'patch':
                patch += 1
            # uuid of the posted/patched item
            item_uuid = e['@graph'][0]['uuid']
            item_id = e['@graph'][0]['@id']
            # if post/patch successful, append uuid to patch_loadxl_item if full
            if patch_loadxl_item != {}:
                patch_loadxl_item['uuid'] = item_uuid
                patch_loadxl.append(patch_loadxl_item)
            # if post/patch successful, add the replicate/set information to the accumulate lists
            if sheet.startswith('Experiment') and not sheet.startswith('ExperimentSet'):
                # Part-I Replicates
                if rep_set_info:
                    rep_id = rep_set_info[0]
                    saveitem = {'replicate_exp': item_id, 'bio_rep_no': rep_set_info[1], 'tec_rep_no': rep_set_info[2]}
                    if dict_replicates.get(rep_id):
                        dict_replicates[rep_id].append(saveitem)
                    else:
                        dict_replicates[rep_id] = [saveitem, ]
                    # Part-II Experiment Sets
                    if exp_set_info:
                        for exp_set in exp_set_info:
                            if dict_exp_sets.get(exp_set):
                                dict_exp_sets[exp_set].append(item_id)
                            else:
                                dict_exp_sets[exp_set] = [item_id, ]
            # if post/patch successful, add the fileset information to the accumulate lists
            if sheet.startswith('File') and not sheet.startswith('FileSet'):
                if file_set_info:
                    for file_set in file_set_info:
                        if dict_file_sets.get(file_set):
                            dict_file_sets[file_set].append(item_id)
                        else:
                            dict_file_sets[file_set] = [item_id, ]

    # add all object loadxl patches to dictionary
    if patch_loadxl:
        dict_patch_loadxl[sheet] = patch_loadxl
    # print final report, and if there are not patched entries, add to report
    not_patched_note = '.'
    if not_patched > 0:
        not_patched_note = ", " + str(not_patched) + " not patched (use --patchall to patch)."
    print("{sheet}: {success} out of {total} posted, {error} errors, {patch} patched{not_patch}".format(
        sheet=sheet.upper(), success=success, total=total, error=error, patch=patch, not_patch=not_patched_note))
    # if sheet == 'ExperimentSet':
    #     if dict_exp_sets
    # if sheet == 'ExperimentSetReplicate':
    #     if dict_replicates


def get_upload_creds(file_id, connection, file_info):  # pragma: no cover
    url = "%s%s/upload/" % (connection.server, file_id)
    req = requests.post(url,
                        auth=connection.auth,
                        headers=connection.headers,
                        data=json.dumps({}))
    return req.json()['@graph'][0]['upload_credentials']


def upload_file(metadata_post_response, path):  # pragma: no cover
    try:
        item = metadata_post_response['@graph'][0]
        creds = item['upload_credentials']
    except Exception as e:
        print(e)
        return
    ####################
    # POST file to S3
    env = os.environ.copy()  # pragma: no cover
    env.update({
        'AWS_ACCESS_KEY_ID': creds['access_key'],
        'AWS_SECRET_ACCESS_KEY': creds['secret_key'],
        'AWS_SECURITY_TOKEN': creds['session_token'],
    })
    # ~10s/GB from Stanford - AWS Oregon
    # ~12-15s/GB from AWS Ireland - AWS Oregon
    print("Uploading file.")
    start = time.time()
    try:
        subprocess.check_call(['aws', 's3', 'cp', path, creds['upload_url']], env=env)
    except subprocess.CalledProcessError as e:
        # The aws command returns a non-zero exit code on error.
        print("Upload failed with exit code %d" % e.returncode)
        sys.exit(e.returncode)
    else:
        end = time.time()
        duration = end - start
        print("Uploaded in %.2f seconds" % duration)


# the order to try to upload / update the items
# used to avoid dependencies... i.e. biosample needs the biosource to exist
def order_sorter(list_of_names):
    ret_list = []
    for i in sheet_order:
        if i in list_of_names:
            ret_list.append(i)
    if list(set(list_of_names)-set(ret_list)) != []:
        missing_items = ", ".join(list(set(list_of_names)-set(ret_list)))
        print("WARNING!", missing_items, "sheet(s) are not loaded")
        print("WARNING! Check the sheet names and the reference list \"sheet_order\"")
    return ret_list


def loadxl_cycle(patch_list, connection):
    for n in patch_list.keys():
        total = 0
        for entry in patch_list[n]:
            if entry != {}:
                total = total + 1
                fdnDCIC.patch_FDN(entry["uuid"], connection, entry)
        print("{sheet}(phase2): {total} items patched.".format(sheet=n.upper(), total=total))


def main():  # pragma: no cover
    args = getArgs()
    key = fdnDCIC.FDN_Key(args.keyfile, args.key)
    if key.error:
        sys.exit(1)
    connection = fdnDCIC.FDN_Connection(key)
    print("Running on:       {server}".format(server=connection.server))
    # test connection
    if not connection.check:
        print("CONNECTION ERROR: Please check your keys.")
        return
    print("Submitting User:  {server}".format(server=connection.email))
    print("Submitting Lab:   {server}".format(server=connection.lab))
    print("Submitting Award: {server}".format(server=connection.award))

    # check input file (xls)
    if not os.path.isfile(args.infile):
        print("File {filename} not found!".format(filename=args.infile))
        sys.exit(1)
    if not args.remote:
        response = input("Do you want to continue with these credentials? (Y/N): ") or "N"
        if response.lower() not in ["y", "yes"]:
            sys.exit(1)
    if args.type:
        names = [args.type]
    else:
        book = xlrd.open_workbook(args.infile)
        names = book.sheet_names()
    # get me a list of all the data_types in the system
    profiles = fdnDCIC.get_FDN("/profiles/", connection)
    supported_collections = list(profiles.keys())
    supported_collections = [s.lower() for s in list(profiles.keys())]
    # we want to read through names in proper upload order
    sorted_names = order_sorter(names)
    # dictionaries that accumulate information during submission
    dict_loadxl = {}
    dict_replicates = {}
    dict_exp_sets = {}
    dict_file_sets = {}
    for n in sorted_names:
        if n.lower() in supported_collections:
            excel_reader(args.infile, n, args.update, connection, args.patchall, dict_loadxl,
                         dict_replicates, dict_exp_sets, dict_file_sets)
        else:
            print("Sheet name '{name}' not part of supported object types!".format(name=n))
    loadxl_cycle(dict_loadxl, connection)
    # if any item left in the following dictionaries
    # it means that this items are not posted/patched
    # because they are not on the exp_set file_set sheets
    for dict_store, dict_sheet in [[dict_replicates, "ExperimentSetReplicate"],
                                   [dict_exp_sets, "ExperimentSet"],
                                   [dict_file_sets, "FileSet"]]:
        if dict_store:
            remains = ', '.join(dict_store.keys())
            print('Following items are not posted')
            print('make sure they are on {} sheet'.format(dict_sheet))
            print(remains)


if __name__ == '__main__':
        main()
