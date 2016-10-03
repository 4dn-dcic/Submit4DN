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
    with the format used on https://www.encodeproject.org/profiles/
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


def getArgs():
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
                        and will only PATCH with user override")
    args = parser.parse_args()
    return args


def attachment(path):
    """Create an attachment upload object from a filename and embed the attachment as a data url."""
    if not os.path.isfile(path):
        r = requests.get(path)
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
            'href': 'data:%s;base64,%s' % (mime_type, b64encode(stream.read()).decode('ascii'))
        }

        if mime_type in ('application/pdf', 'text/plain', 'text/tab-separated-values', 'text/html'):
            # XXX Should use chardet to detect charset for text files here.
            return attach

        if major == 'image' and minor in ('png', 'jpeg', 'gif', 'tiff'):
            # XXX we should just convert our tiffs to pngs
            stream.seek(0, 0)
            im = Image.open(stream)
            im.verify()
            if im.format != minor.upper():
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

    if ctype == xlrd.XL_CELL_ERROR:
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
        else:
            return datetime.datetime(*value).isoformat()

    elif ctype in (xlrd.XL_CELL_TEXT, xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK):
        return value

    raise ValueError(repr(cell), 'unknown cell type')


def data_formatter(value, val_type):
    """Return formatted data."""
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


def clear_out_empty_field(field_name, fields):
    """Remove fields with empty value."""
    if fields[field_name] == '':
        fields.pop(field_name)


def get_field_name(field_name):
    """handle type at end, plus embedded objets."""
    field = field_name.replace('*', '')
    return field.split(".")[0]


def get_sub_field(field_name):
    """Construct embeded field names."""
    try:
        return field_name.split(".")[1].rstrip('-0123456789')
    except:
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
    if field_data == '' or field == '':
        return None

    patch_field_name = get_field_name(field)
    if field_type is None:
        field_type = get_field_type(field)

    if is_embedded_field(field):
        sub_field = get_sub_field(field)
        return build_field(sub_field, field_data, 'string')
    else:
        patch_field_data = data_formatter(field_data, field_type)
    return {patch_field_name: patch_field_data}


def build_patch_json(fields, fields2types):
    """Create the data entry dictionary from the fields."""
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


def excel_reader(datafile, sheet, update, connection, patchall):
    row = reader(datafile, sheetname=sheet)
    keys = next(row)  # grab the first row of headers
    types = next(row)  # grab second row with type info
    # remove title column
    fields2types = None
    keys.pop(0)
    row2name = types.pop(0)
    if 'Type' in row2name:
        fields2types = dict(zip(keys, types))
        for field, ftype in fields2types.items():
            if 'array' in ftype:
                fields2types[field] = 'array'
    # print(fields2types)
    # sys.exit()

    total = 0
    error = 0
    success = 0
    patch = 0
    for values in row:
        # Rows that start with # are skipped
        if values[0].startswith("#"):
            continue
        # Get rid of the first empty cell
        values.pop(0)
        total += 1
        post_json = dict(zip(keys, values))
        post_json = build_patch_json(post_json, fields2types)
        # print(post_json)
        # combine exp sets
        if "Experiment" in sheet:
            if sheet != "ExperimentSet":
                comb_sets = []
                for set_key in ["experiment_sets|0", "experiment_sets|1", "experiment_sets|2", "experiment_sets|3"]:
                    try:
                        comb_sets.extend(post_json.get(set_key))
                    except:
                        continue
                    post_json.pop(set_key, None)
                post_json['experiment_sets'] = comb_sets
        # add attchments here
        if post_json.get("attachment"):
            attach = attachment(post_json["attachment"])
            post_json["attachment"] = attach
        # should I upload files as well?
        file_to_upload = False
        filename_to_post = post_json.get('filename')
        if filename_to_post:
            # remove full path from filename
            post_json['filename'] = filename_to_post.split('/')[-1]
            file_to_upload = True

        existing_data = get_existing(post_json, connection)

        if existing_data.get("uuid"):
            to_patch = 'n'
            if not patchall:
                print("Object {} already exists.  Would you like to patch it "
                      "instead?".format(existing_data["uuid"]))
                to_patch = input("PATCH? y/n ")

            if patchall or to_patch.lower() == 'y':
                # add the md5
                if file_to_upload and not post_json.get('md5sum'):
                    print("calculating md5 sum for file %s " % (filename_to_post))
                    post_json['md5sum'] = md5(filename_to_post)

                e = fdnDCIC.patch_FDN(existing_data["uuid"], connection, post_json)
                if file_to_upload:
                    # get s3 credentials
                    creds = get_upload_creds(
                        e['@graph'][0]['accession'],
                        connection,
                        e['@graph'][0])
                    e['@graph'][0]['upload_credentials'] = creds

                    # upload
                    upload_file(e, filename_to_post)

                if e["status"] == "error":
                    error += 1
                elif e["status"] == "success":
                    success += 1
                    patch += 1
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
                if e["status"] == "error":
                    error += 1
                elif e["status"] == "success":
                    success += 1
            else:
                print("This looks like a new row but the update flag wasn't passed, use --update to"
                      " post new data")
                return
    # print(post_json)
    print("{sheet}: {success} out of {total} posted, {error} errors, {patch} patched".format(
        sheet=sheet.upper(), success=success, total=total, error=error, patch=patch))


def get_upload_creds(file_id, connection, file_info):
    url = "%s%s/upload/" % (connection.server, file_id)
    req = requests.post(url,
                        auth=connection.auth,
                        headers=connection.headers,
                        data=json.dumps({}))
    return req.json()['@graph'][0]['upload_credentials']


def upload_file(metadata_post_response, path):
    try:
        item = metadata_post_response['@graph'][0]
        creds = item['upload_credentials']
    except Exception as e:
        print(e)
        return

    ####################
    # POST file to S3

    env = os.environ.copy()
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


def order_sorter(key):
    ORDER = [i.lower for i in sheet_order]
    key = key.lower()
    if key in ORDER:
        return ORDER.index(key)
    else:
        return 999


def main():
    args = getArgs()
    key = fdnDCIC.FDN_Key(args.keyfile, args.key)
    connection = fdnDCIC.FDN_Connection(key)
    print("Running on {server}".format(server=connection.server))
    if not os.path.isfile(args.infile):
        print("File {filename} not found!".format(filename=args.infile))
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
    # that way we have dependencies inserted in the proper order
    sorted_names = sorted(names, key=order_sorter)

    for n in sorted_names:
        if n.lower() in supported_collections:
            excel_reader(args.infile, n, args.update, connection, args.patchall)
        else:
            print("Sheet name '{name}' not part of supported object types!".format(name=n))

if __name__ == '__main__':
        main()
