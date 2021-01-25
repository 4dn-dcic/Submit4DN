#!/usr/bin/env python3
# -*- coding: latin-1 -*-
import os.path
import argparse
from dcicutils import ff_utils
import attr
import xlwt
import sys
import json
# import sys


EPILOG = '''
    To create an xls file with sheets to be filled use the example and modify to your needs.
    It will accept the following parameters.
        --type           use for each sheet that you want to add to the excel workbook
        --descriptions   adds the descriptions in the second line (by default True)
        --enums          adds the list of options for a fields if it has a controlled vocabulary (by default True)
        --comments       adds the comments together with enums (by default False)
        --writexls       creates the xls file (by default True)
        --outfile        change the default file name "fields.xls" to a specified one
        --order          create an ordered and filtered version of the excel (by default True)

    This program graphs uploadable fields (i.e. not calculated properties)
    for a type with optionally included description and enum values.

    To get multiple objects use the '--type' argument multiple times

            %(prog)s --type Biosample --type Biosource

    to include comments (useful tips) for all types use the appropriate flag at the end

            %(prog)s --type Biosample --comments
            %(prog)s --type Biosample --type Biosource --comments

    To change the result filename use --outfile flag followed by the new file name

            %(prog)s --type Biosample --outfile biosample_only.xls
            %(prog)s --type Biosample --type Experiment --outfile my_selection.xls

    '''


def getArgs():  # pragma: no cover
    parser = argparse.ArgumentParser(
        description=__doc__, epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--type',
                        help="Add a separate --type for each type you want to get or use 'all' to get all sheets.",
                        action="append")
    parser.add_argument('--descriptions',
                        default=True,
                        action='store_true',
                        help="Include descriptions for fields.")
    parser.add_argument('--comments',
                        default=False,
                        action='store_true',
                        help="Include comments for fields")
    parser.add_argument('--enums',
                        default=True,
                        action='store_true',
                        help="Include enums for fields.")
    parser.add_argument('--writexls',
                        default=True,
                        action='store_true',
                        help="Create an xls with the columns and sheets"
                             "based on the data returned from this command.")
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
    parser.add_argument('--outfile',
                        default='fields.xls',
                        help="The name of the output file. Default is fields.xls")
    parser.add_argument('--remote',
                        default=False,
                        action='store_true',
                        help="will skip attribution prompt \
                        needed for automated submissions")
    parser.add_argument('--noadmin',
                        default=False,
                        action='store_true',
                        help="Will set an admin user to non-admin for generating sheets")
    args = parser.parse_args()
    return args


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
        self.con_key = keys[keyname]
        if not self.con_key['server'].endswith("/"):
            self.con_key['server'] += "/"


class FDN_Connection(object):
    def __init__(self, key4dn):
        # passed key object stores the key dict in con_key
        self.check = False
        self.key = key4dn.con_key
        # check connection and find user uuid
        # TODO: we should not need try/except, since if me page fails, there is
        # no need to proggress, but the test are failing without this Part
        # make mocked connections and remove try/except
        # is public connection using submit4dn a realistic case?
        try:
            me_page = ff_utils.get_metadata('me', key=self.key)
            self.user = me_page['@id']
            self.email = me_page['email']
            self.check = True
            self.admin = True if 'admin' in me_page.get('groups', []) else False
        except:
            print('Can not establish connection, please check your keys')
            me_page = {}
        if not me_page:
            sys.exit(1)
        if me_page.get('submits_for') is not None:
            # get all the labs that the user making the connection submits_for
            self.labs = [l['@id'] for l in me_page['submits_for']]
            # take the first one as default value for the connection - reset in
            # import_data if needed by calling set_lab_award
            self.lab = self.labs[0]
            self.set_award(self.lab, dontPrompt=True)  # set as default first
        else:
            self.labs = None
            self.lab = None
            self.award = None

    def set_award(self, lab, dontPrompt=False):
        '''Sets the award for the connection for use in import_data
           if dontPrompt is False will ask the User to choose if there
           are more than one award for the connection.lab otherwise
           the first award for the lab will be used
        '''
        self.award = None
        if lab is not None:
            labjson = ff_utils.get_metadata(lab, key=self.key)
            if labjson.get('awards') is not None:
                awards = labjson.get('awards')
                if len(awards) == 1:
                    self.award = awards[0]['@id']
                    return

                # if don't prompt is active leave None
                if dontPrompt:
                    return

                # if there are multiple awards
                achoices = []
                print("Multiple awards for {labname}:".format(labname=lab))
                for i, awd in enumerate(awards):
                    ch = str(i + 1)
                    achoices.append(ch)
                    print("  ({choice}) {awdname}".format(choice=ch, awdname=awd['@id']))
                # re try the input until a valid choice is input
                awd_resp = ''
                while awd_resp not in achoices:
                    awd_resp = str(input("Select the award for this session {choices}: ".format(choices=achoices)))
                self.award = awards[int(awd_resp) - 1]['@id']
        return

    def prompt_for_lab_award(self, lab=None, award=None):
        '''Check to see if user submits_for multiple labs or the lab
            has multiple awards and if so prompts for the one to set
            for the connection
        '''
        if lab:
            if not award:
                self.set_award(self.lab)
        else:
            if self.labs is not None:
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
            if not award:
                self.set_award(self.lab, False)


@attr.s
class FieldInfo(object):
    name = attr.ib()
    ftype = attr.ib()
    lookup = attr.ib()
    desc = attr.ib(default=u'')
    comm = attr.ib(default=u'')
    enum = attr.ib(default=u'')


# additional fields for experiment sheets to capture experiment_set related information
exp_set_addition = [FieldInfo('*replicate_set', 'Item:ExperimentSetReplicate', 3, 'Grouping for replicate experiments'),
                    FieldInfo('*bio_rep_no', 'integer', 4, 'Biological replicate number'),
                    FieldInfo('*tec_rep_no', 'integer', 5, 'Technical replicate number'),
                    # FieldInfo('experiment_set', 'array of Item:ExperimentSet', 2,
                    #          'Grouping for non-replicate experiments')
                    ]


sheet_order = [
    "User", "Award", "Lab", "Document", "Protocol", "ExperimentType",
    "Publication", "Organism", "Vendor", "IndividualChicken", "IndividualFly",
    "IndividualHuman", "IndividualMouse", "IndividualPrimate",
    "IndividualZebrafish", "FileFormat", "Enzyme", "GenomicRegion", "Gene",
    "BioFeature", "Construct", "TreatmentRnai", "TreatmentAgent",
    "Antibody", "Modification", "Image", "Biosource", "BiosampleCellCulture",
    "Biosample", "FileFastq", "FileProcessed", "FileReference",
    "FileCalibration", "FileSet", "FileSetCalibration", "MicroscopeSettingD1",
    "MicroscopeSettingD2", "MicroscopeSettingA1", "MicroscopeSettingA2",
    "FileMicroscopy", "FileSetMicroscopeQc", "ImagingPath", "ExperimentMic",
    "ExperimentMic_Path", "ExperimentHiC", "ExperimentCaptureC",
    "ExperimentRepliseq", "ExperimentAtacseq", "ExperimentChiapet",
    "ExperimentDamid", "ExperimentSeq", "ExperimentTsaseq", "ExperimentSet",
    "ExperimentSetReplicate", "WorkflowRunSbg", "WorkflowRunAwsem",
    "OntologyTerm"
]

file_types = [i for i in sheet_order if i.startswith('File') and not i.startswith('FileSet')]
file_types.remove('FileFormat')
exp_types = [i for i in sheet_order if i.startswith('Experiment') and 'Type' not in i and 'Set' not in i]


def get_field_type(field):
    field_type = field.get('type', '')
    if field_type == 'string':
        if field.get('linkTo', ''):
            return "Item:" + field.get('linkTo')
        # if multiple objects are linked by "anyOf"
        if field.get('anyOf', ''):
            links = list(filter(None, [d.get('linkTo', '') for d in field.get('anyOf')]))
            if links:
                return "Item:" + ' or '.join(links)
        # if not object return string
        return 'string'
    elif field_type == 'array':
        return 'array of ' + get_field_type(field.get('items'))
    return field_type


def is_subobject(field):
    if field.get('type') == 'object':
        return True
    try:
        return field['items']['type'] == 'object'
    except:
        return False


def dotted_field_name(field_name, parent_name=None):
    if parent_name:
        return "%s.%s" % (parent_name, field_name)
    else:
        return field_name


def build_field_list(properties, required_fields=None, include_description=False,
                     include_comment=False, include_enums=False, parent='', is_submember=False, admin=False):
    fields = []
    for name, props in properties.items():
        is_member_of_array_of_objects = False
        if props.get('calculatedProperty'):
            continue
        if 'submit4dn' in props.get('exclude_from', []):
            continue
        if ('import_items' in props.get('permission', []) and not admin):
            continue
        if is_subobject(props) and name != 'attachment':
            if get_field_type(props).startswith('array'):
                is_member_of_array_of_objects = True
                fields.extend(build_field_list(props['items']['properties'],
                                               required_fields,
                                               include_description,
                                               include_comment,
                                               include_enums,
                                               name,
                                               is_member_of_array_of_objects)
                              )
            else:
                fields.extend(build_field_list(props['properties'],
                                               required_fields,
                                               include_description,
                                               include_comment,
                                               include_enums,
                                               name,
                                               is_member_of_array_of_objects)
                              )
        else:
            field_name = dotted_field_name(name, parent)
            if required_fields is not None:
                if field_name in required_fields:
                    field_name = '*' + field_name
            field_type = get_field_type(props)
            if is_submember:
                field_type = "array of embedded objects, " + field_type
            desc = '' if not include_description else props.get('description', '')
            comm = '' if not include_comment else props.get('comment', '')
            enum = ''
            if include_enums:
                enum = props.get('enum') if 'enum' in props else props.get('suggested_enum', '')
            lookup = props.get('lookup', 500)  # field ordering info
            # if array of string with enum
            if field_type == "array of string":
                sub_props = props.get('items', '')
                enum = ''
                if include_enums:
                    enum = sub_props.get('enum') if 'enum' in sub_props else sub_props.get('suggested_enum', '')
            # copy paste exp set for ease of keeping track of different types in experiment objects
            fields.append(FieldInfo(field_name, field_type, lookup, desc, comm, enum))
    return fields


class FDN_Schema(object):
    def __init__(self, connection, schema_name):
        uri = '/profiles/' + schema_name + '.json'
        response = ff_utils.get_metadata(uri, key=connection.key, add_on="frame=object")
        self.required = None
        if 'required' in response:
            self.required = response['required']
        if schema_name in file_types and response['properties'].get('file_format'):
            q = '/search/?type=FileFormat&field=file_format&valid_item_types={}'.format(schema_name)
            formats = [i['file_format'] for i in ff_utils.search_metadata(q, key=connection.key)]
            response['properties']['file_format']['enum'] = formats
        elif schema_name in exp_types and response['properties'].get('experiment_type'):
            q = '/search/?type=ExperimentType&field=title&valid_item_types={}'.format(schema_name)
            exptypes = [i['title'] for i in ff_utils.search_metadata(q, key=connection.key)]
            response['properties']['experiment_type']['enum'] = exptypes
        self.properties = response['properties']


def get_uploadable_fields(connection, types, include_description=False,
                          include_comments=False, include_enums=False):
    fields = {}
    for name in types:
        schema_grabber = FDN_Schema(connection, name)
        required_fields = schema_grabber.required
        properties = schema_grabber.properties
        fields[name] = build_field_list(properties,
                                        required_fields,
                                        include_description,
                                        include_comments,
                                        include_enums,
                                        admin=connection.admin)
        if name.startswith('Experiment') and not name.startswith('ExperimentSet') and name != 'ExperimentType':
            fields[name].extend(exp_set_addition)
        if 'extra_files' in properties:
            if 'submit4dn' not in properties['extra_files'].get('exclude_from', [""]):
                fields[name].extend([FieldInfo('extra_files.filename', 'array of embedded objects, string',
                                               401, 'Full Path to Extrafile to upload')])
    return fields


def create_xls(all_fields, filename):
    '''
    fields being a dictionary of sheet -> FieldInfo(objects)
    create one sheet per dictionary item, with three columns of fields
    for fieldname, description and enum
    '''
    wb = xlwt.Workbook()
    # text styling for all columns
    style = xlwt.XFStyle()
    style.num_format_str = "@"
    # order sheets
    sheet_list = [(sheet, all_fields[sheet]) for sheet in sheet_order if sheet in all_fields.keys()]
    for obj_name, fields in sheet_list:
        ws = wb.add_sheet(obj_name)
        ws.write(0, 0, "#Field Name:")
        ws.write(1, 0, "#Field Type:")
        ws.write(2, 0, "#Description:")
        ws.write(3, 0, "#Additional Info:")
        # add empty formatting for first column
        for i in range(100):
            ws.write(4+i, 0, '', style)
        # order fields in sheet based on lookup numbers, then alphabetically
        for col, field in enumerate(sorted(sorted(fields), key=lambda x: x.lookup)):
            ws.write(0, col+1, str(field.name), style)
            ws.write(1, col+1, str(field.ftype), style)
            if field.desc:
                ws.write(2, col+1, str(field.desc), style)
            # combine comments and Enum
            add_info = ''
            if field.comm:
                add_info += str(field.comm)
            if field.enum:
                add_info += "Choices:" + str(field.enum)
            if not field.comm and not field.enum:
                add_info = "-"
            ws.write(3, col+1, add_info, style)
            # add empty formatting for all columns
            for i in range(100):
                ws.write(4+i, col+1, '', style)
    wb.save(filename)


def get_sheet_names(types_list):
    lowercase_types = [item.lower().replace('-', '').replace('_', '') for item in types_list if
                       item != 'ExperimentMic_Path']
    if lowercase_types == ['all']:
        sheets = [sheet for sheet in sheet_order if sheet not in ['ExperimentMic_Path', 'OntologyTerm']]
    else:
        presets = {
            'hic': ["image", "filefastq", "experimenthic"],
            'chipseq': ["gene", "biofeature", "antibody", "filefastq", "experimentseq"],
            'repliseq': ["filefastq", "experimentrepliseq", "experimentset"],
            'atacseq': ["enzyme", "filefastq", "experimentatacseq"],
            'damid': ["gene", "biofeature", "filefastq", "fileprocessed", "experimentdamid"],
            'chiapet': ["gene", "biofeature", "filefastq", "experimentchiapet"],
            'capturec': ["genomicregion", "biofeature", "filefastq", "filereference", "experimentcapturec"],
            'fish': [
                "genomicregion", "biofeature", "antibody", "microscopesettinga1", "filemicroscopy",
                "filereference", "fileprocessed", "imagingpath", "experimentmic",
            ],
            'spt': [
                "gene", "biofeature", "modification", "microscopesettinga2",
                "fileprocessed", "imagingpath", "experimentmic",
            ]}
        for key in presets.keys():
            if key in lowercase_types:
                lowercase_types.remove(key)
                lowercase_types += presets[key]
                lowercase_types += [
                    'protocol', 'publication', 'biosource', 'biosample',
                    'biosamplecellculture', 'image', 'experimentsetreplicate'
                ]
        sheets = [sheet for sheet in sheet_order if sheet.lower() in lowercase_types]
        for name in types_list:
            modified_name = name.lower().replace('-', '').replace('_', '')
            if modified_name in lowercase_types and modified_name not in [sheetname.lower() for sheetname in sheets]:
                print('No schema found for type {} -- skipping'.format(name))
    return sheets


def main():  # pragma: no cover
    args = getArgs()
    key = FDN_Key(args.keyfile, args.key)
    if key.error:
        sys.exit(1)
    connection = FDN_Connection(key)
    if args.noadmin:
        connection.admin = False
    sheets = get_sheet_names(args.type)
    fields = get_uploadable_fields(connection, sheets, args.descriptions, args.comments, args.enums)

    if args.debug:
        print("retrieved fields as")
        from pprint import pprint
        pprint(fields)

    if args.writexls:
        file_name = args.outfile
        create_xls(fields, file_name)


if __name__ == '__main__':
    main()
