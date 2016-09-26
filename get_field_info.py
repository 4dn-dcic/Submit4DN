#!/usr/bin/env python3
# -*- coding: latin-1 -*-
import os.path
import argparse
import encodedccMod
import attr
import xlwt
import xlrd

EPILOG = '''
    This program graphs uploadable fields (i.e. not calculated properties)
    for a type with optionally included description and enum values.

    To get multiple objects use the '--type' argument multiple times

            %(prog)s --type Biosample --type Biosource

    to include description and enum for all types use the appropriate flags

            %(prog)s --type Biosample --descriptions --enum
            %(prog)s --type Biosample --type Biosource --enum

    To write the result to an excel file with one sheet for each type use
    the --writexls switch:

            %(prog)s --type User --writexls
            %(prog)s --type Biosample --type Experiment --descriptions --writexls

    '''


def getArgs():
    parser = argparse.ArgumentParser(
        description=__doc__, epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--type',
                        help="Add a separate --type for each type you want to get.",
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
                        help="Create an xls with the columns and sheets, based on the data returned from this command.")
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
    parser.add_argument('--outfile',
                        default='fields.xls',
                        help="The name of the output file. Default is fields.xls")
    parser.add_argument('--order',
                        default=True,
                        action='store_true',
                        help="A reference file is used for ordering and filtering fields")
    args = parser.parse_args()
    return args


@attr.s
class FieldInfo(object):
    name = attr.ib()
    ftype = attr.ib()
    desc = attr.ib(default=u'')
    comm = attr.ib(default=u'')
    enum = attr.ib(default=u'')


def get_field_type(field):
    field_type = field.get('type', '')
    if field_type == 'string':
        if field.get('linkTo', ''):
            return "Item:" + field.get('linkTo')
        return 'string'
    elif field_type == 'array':
        return 'array of ' + get_field_type(field.get('items')) + 's'
    return field_type


def is_subobject(field):
    try:
        return field['items']['type'] == 'object'
    except:
        return False


def dotted_field_name(field_name, parent_name=None):
    if parent_name:
        return "%s.%s" % (parent_name, field_name)
    else:
        return field_name


def build_field_list(properties, include_description=False, include_comment=False,
                     include_enums=False, parent='', is_submember=False):
    fields = []
    for name, props in properties.items():
        is_member_of_array_of_objects = False
        if not props.get('calculatedProperty', False):
            if is_subobject(props):
                if get_field_type(props).startswith('array'):
                    is_member_of_array_of_objects = True
                fields.extend(build_field_list(props['items']['properties'],
                                               include_description,
                                               include_comment,
                                               include_enums,
                                               name,
                                               is_member_of_array_of_objects)
                              )
            else:
                field_name = dotted_field_name(name, parent)
                field_type = get_field_type(props)
                if is_submember:
                    field_type = field_type + " (array - multiple allowed paired with other " + parent + " fields)"
                # special case for attachemnts
                #if name == 'attachment':
                #    field_name = dotted_field_name(name, parent)
                desc = '' if not include_description else props.get('description', '')
                comm = '' if not include_comment else props.get('comment', '')
                enum = '' if not include_enums else props.get('enum', '')
                fields.append(FieldInfo(field_name, field_type, desc, comm, enum))
    return fields


def get_uploadable_fields(connection, types, include_description=False, include_comments=False, include_enums=False):
    fields = {}
    for name in types:
        schema_name = encodedccMod.format_schema_name(name)
        uri = '/profiles/' + schema_name
        schema_grabber = encodedccMod.ENC_Schema(connection, uri)
        fields[name] = build_field_list(schema_grabber.properties,
                                        include_description,
                                        include_comments,
                                        include_enums)
    return fields


def create_xls(fields, filename):
    '''
    fields being a dictionary of sheet -> FieldInfo(objects)
    create one sheet per dictionary item, with three columns of fields
    for fieldname, description and enum
    '''
    wb = xlwt.Workbook()
    for obj_name, fields in fields.items():
        ws = wb.add_sheet(obj_name)
        ws.write(0, 0, "#Field Name:")
        ws.write(1, 0, "#Field Type:")
        ws.write(2, 0, "#Description:")
        ws.write(3, 0, "#Additional Info:")
        for col, field in enumerate(fields):
            ws.write(0, col+1, str(field.name))
            ws.write(1, col+1, str(field.ftype))
            if field.desc:
                ws.write(2, col+1, str(field.desc))
            # combine comments and Enum
            add_info = ''
            if field.comm:
                add_info += str(field.comm)
            if field.enum:
                add_info += "Choices:" + str(field.enum)
            ws.write(3, col+1, add_info)
    wb.save(filename)


def ordered(input_file, reference_file="System_Files/reference_fields.xls"):
    folder = os.path.dirname(os.path.abspath(__file__))
    ReadFile = folder+'/'+input_file
    RefFile = folder+'/'+reference_file
    OutputFile = folder+'/'+input_file[:-4]+'_ordered.xls'

    bookref = xlrd.open_workbook(RefFile)
    bookread = xlrd.open_workbook(ReadFile)
    book_w = xlwt.Workbook()
    Sheets_read = bookread.sheet_names()
    Sheets_ref = bookref.sheet_names()
    Sheets = []
    for sh in Sheets_ref:
        if sh in Sheets_read:
            Sheets.append(sh)
            Sheets_read.remove(sh)
    Sheets.extend(Sheets_read)

    for sheet in Sheets:
        try:
            active_sheet_ref = bookref.sheet_by_name(sheet)
        except:
            print('The object {} does not exist in referece file, please update'.format(sheet))
            continue
        active_sheet_read = bookread.sheet_by_name(sheet)
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
    try:
        book_w.save(OutputFile)
    except:
        print('Ordered xls is not created, reference might be missing ordered object sheets')


def main():
    args = getArgs()
    key = encodedccMod.ENC_Key(args.keyfile, args.key)
    connection = encodedccMod.ENC_Connection(key)
    fields = get_uploadable_fields(connection, args.type,
                                   args.descriptions,
                                   args.comments,
                                   args.enums)

    if args.debug:
        print("retrieved fields as")
        from pprint import pprint
        pprint(fields)

    if args.writexls:
        file_name = args.outfile
        create_xls(fields, file_name)
        if args.order:
            ordered(file_name)

if __name__ == '__main__':
    main()
