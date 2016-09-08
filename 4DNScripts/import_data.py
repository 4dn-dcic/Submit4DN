#!/usr/bin/env python3
# -*- coding: latin-1 -*-

import argparse
import os.path
import encodedccMod as encodedcc
import xlrd
import datetime
import sys
import mimetypes
import requests
from PIL import Image
from base64 import b64encode
import ast
import magic  # install me with 'pip install python-magic'
# https://github.com/ahupp/python-magic
# this is the site for python-magic in case we need it
import attr
import os
import time
import subprocess

EPILOG = '''
This script takes in an Excel file with the data
This is a dryrun-default script, run with --update or --patchall to work

By DEFAULT:
If there is a uuid, alias, @id, or accession in the document
it will ask if you want to PATCH that object
Use '--patchall' if you want to patch ALL objects in your document and ignore that message

If no object identifiers are found in the document you need to use '--update'
for POSTing to occur

Defining Object type:
    Name each "sheet" of the excel file the name of the object type you are using
    with the format used on https://www.encodeproject.org/profiles/
Ex: Experiment, Biosample, Document, AntibodyCharacterization

    Or use the '--type' argument, but this will only work for single sheet documents
Ex: %(prog)s mydata.xsls --type Experiment


The header of each sheet should be the names of the fields just as in ENCODE_patch_set.py,
Ex: award, lab, target, etc.

    For integers use ':int' or ':integer'
    For lists use ':list' or ':array'
    String are the default and do not require an identifier


To upload objects with attachments, have a column titled "attachment"
containing the name of the file you wish to attach

FOR EMBEDDED SUBOBJECTS:
Embedded objects are considered to be things like:
 - characterization_reviews in AntibodyCharacterizations
 - tags in Constructs
 They are assumed to be of the format of a list of dictionary objects
 Ex:
 "characterization_reviews": [
        {
            "organism": "/organisms/human/",
            "biosample_term_name": "A375",
            "lane": 2,
            "biosample_type": "immortalized cell line",
            "biosample_term_id": "EFO:0002103",
            "lane_status": "compliant"
        },
        {
            "organism": "/organisms/mouse/",
            "biosample_term_name": "embryonic fibroblast",
            "lane": 3,
            "biosample_type": "primary cell",
            "biosample_term_id": "CL:2000042",
            "lane_status": "compliant"
        }
    ]

Formatting in the document should be as follows for the above example:
characterization_reviews.organism    characterization_reviews.lane:int    ....    characterization_reviews.organism-1    characterization_reviews.lane-1:int
/organisms/human/                    2                                            /organisms/mouse/                      3


REMEMBER:
to define multiple embedded items the number tag comes at the end
of the object but before the object type, such as object.subobject-N:type
    tags.name    tags.location    tags.name-1    tags.location-1
    FLAG         C-terminal       BOGUS          Fake-data

Again, this will become
"tags": [
        {
            "location": "C-terminal",
            "name": "FLAG"
        },
        {
            "location": "Fake-data",
            "name": "BOGUS"
        }
    ],

For more details:

        %(prog)s --help
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
                        help="The keypair file.  Default is --keyfile=%s" % (os.path.expanduser("~/keypairs.json")))
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
    parser.add_argument('--skiprows',
                        type=int,
                        default=4,
                        help="Number of rows from the beginning of sheet(s) to skip \
                        INCLUDING Field name row - Default is 4")
    args = parser.parse_args()
    return args


def attachment(path):
    """ Create an attachment upload object from a filename
    Embeds the attachment as a data url.
    """
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
    """ Read named sheet or first and only sheet from xlsx file
    """
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
    ''' returns formatted data'''
    if val_type in ["int", "integer"]:
        return int(value)
    elif val_type in ["num", "number"]:
        return float(value)
    elif val_type in ["list", "array"]:
        data_list = value.strip("[\']").split(",")
        return  [data.strip() for data in data_list]
    else:
        # default assumed to be string
        return str(value)

def clear_out_empty_field(field_name, fields):
    if fields[field_name] == '':
        fields.pop(field_name)

def get_field_name(field_name):
    '''handle type at end, plus embedded objets'''
    field = field_name.split(":")[0]
    return field.split(".")[0]

def get_sub_field(field_name):
    try:
        return field_name.split(".")[1]
    except:
        return ''

def get_field_type(field_name):
    try:
        return field_name.split(":")[1]
    except:
        return "string"


def is_embedded_field(field_name):
    return '.' in field_name


def get_sub_field_number(field_name):
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

def build_field(field, field_data):
    if field_data == '' or field == '':
        return '' 

    patch_field_name = get_field_name(field)
    patch_field_type = get_field_type(field)

    if is_embedded_field(field):
        sub_field = get_sub_field(field)
        return  build_field(sub_field,field_data)
    else:
        patch_field_data = data_formatter(field_data, patch_field_type)


    return {patch_field_name : patch_field_data}


def build_patch_json(fields):
    '''
    fields is a dictonary from json object
    '''
    patch_data = {}
    for field, field_data in fields.items():
        patch_field = build_field(field, field_data)
        if patch_field != None:
            if is_embedded_field(field):
                top_field = get_field_name(field)
                if patch_data.get(top_field, None) is None:
                    # initially create a list of object for the embedded field
                    patch_data[top_field] = [{}]
                # we can have multiple embedded objects (they are numbered in excel)
                subobject_num = get_sub_field_number(field)

                if subobject_num >= len(patch_data[top_field]):
                    # add a new row to the list
                    patch_data[top_field].extend(patch_field)
                else:
                    # update existing object in the list
                    patch_data[top_field][subobject_num].update(patch_field)
            else:
                # normal case, just update the dictionary
                patch_data.update(patch_field)
    return patch_data

def get_existing(post_json, connection):
    temp = {}
    if post_json.get("uuid"):
        temp = encodedcc.get_ENCODE(post_json["uuid"], connection)
    #elif post_json.get("aliases"):
        temp = encodedcc.get_ENCODE(post_json["aliases"][0], connection)
    elif post_json.get("alias"):
        temp = encodedcc.get_ENCODE(post_json["alias"], connection)
    elif post_json.get("accession"):
        temp = encodedcc.get_ENCODE(post_json["accession"], connection)
    elif post_json.get("@id"):
        temp = encodedcc.get_ENCODE(post_json["@id"], connection)
    return temp

def excel_reader(datafile, sheet, update, connection, patchall, skiprows):
    row = reader(datafile, sheetname=sheet)
    keys = next(row)  # grab the first row of headers
    # remove title column
    keys.pop(0)
    # skip the default three rows of description / comments /enums or the number
    # specified in the skiprows argument
    skiprows = skiprows - 1
    for _ in range(skiprows):
        next(row)

    total = 0
    error = 0
    success = 0
    patch = 0
    for values in row:
        # always remove first column cause that is used for titles of rows
        values.pop(0)
        total += 1
        post_json = dict(zip(keys, values))
        post_json = build_patch_json(post_json)

        # add attchments here
        if post_json.get("attachment"):
            attach = attachment(post_json["attachment"])
            post_json["attachment"] = attach
        print(post_json)

        # should I upload files as well?
        file_to_upload = False
        if post_json.get('filename'):
            file_to_upload = True

        existing_data = get_existing(post_json, connection)

        if existing_data.get("uuid"):
            to_patch = 'n'
            if not patchall:
                print("Object {} already exists.  Would you like to patch it "
                      "instead?".format(existing_data["uuid"]))
                to_patch = input("PATCH? y/n ")

            if patchall or to_patch.lower() == 'y':
                e = encodedcc.patch_ENCODE(existing_data["uuid"], connection, post_json)
                if e["status"] == "error":
                    error += 1
                elif e["status"] == "success":
                    success += 1
                    patch += 1
        else:
            if update:
                print("POSTing data!")
                e = encodedcc.new_ENCODE(connection, sheet, post_json)
                if file_to_upload:
                    upload_file(e, post_json.get('filename'))
                if e["status"] == "error":
                    error += 1
                elif e["status"] == "success":
                    success += 1
    print("{sheet}: {success} out of {total} posted, {error} errors, {patch} patched".format(
        sheet=sheet.upper(), success=success, total=total, error=error, patch=patch))

def upload_file(metadata_post_response, path):
    try:
        item = metadata_post_response['@graph'][0]
        creds = item['upload_credentials']
    except:
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
ORDER = [
    'user',
    'award',
    'lab',
    'organism',
    'document',
    'publication',
    'vendor',
    'protocol',
    'protocolscellculture',
    'protocol_cell_culture',
    'individualhuman',
    'individual_human',
    'individualmouse',
    'individual_mouse',
    'biosource',
    'enzyme',
    'construct',
    'treatmentrnai'
    'treatment_rnai',
    'modification',
    'biosample',
    'fileset',
    'file_set',
    'file',
    'experimentset',
    'experiment_set',
    'experimenthic',
    'experiment_hic'
]


def order_sorter(key):
    key = key.lower()
    if key in ORDER:
        return ORDER.index(key)
    else:
        return 999


def main():
    args = getArgs()
    key = encodedcc.ENC_Key(args.keyfile, args.key)
    connection = encodedcc.ENC_Connection(key)
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
    profiles = encodedcc.get_ENCODE("/profiles/", connection)
    supported_collections = list(profiles.keys())
    supported_collections = [s.lower() for s in list(profiles.keys())]

    # we want to read through names in proper upload order
    # that way we have dependencies inserted in the proper order
    sorted_names = sorted(names, key=order_sorter)

    for n in sorted_names:
        if n.lower() in supported_collections:
            excel_reader(args.infile, n, args.update, connection, args.patchall, args.skiprows)
        else:
            print("Sheet name '{name}' not part of supported object types!".format(name=n))

if __name__ == '__main__':
        main()
