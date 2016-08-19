#!/usr/bin/env python3
# -*- coding: latin-1 -*-
import os.path
import argparse
import encodedccMod
import attr
import xlwt

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
                        help="Add a seperate --type for each type you want to get.",
                        action="append")
    parser.add_argument('--descriptions',
                        default=False,
                        action='store_true',
                        help="Include descriptions for fields.")
    parser.add_argument('--enums',
                        default=False,
                        action='store_true',
                        help="Include enums for fields.")
    parser.add_argument('--writexls',
                        default=False,
                        action='store_true',
                        help="Create an xls with the appropriate columns and sheets, based on the data returned from this command.")
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
    args = parser.parse_args()
    return args

@attr.s
class FieldInfo(object):
    name = attr.ib()
    desc = attr.ib(default=u'')
    enum = attr.ib(default=u'')

def get_field_type(field):
    field_type = field.get('type', '')
    if field_type == 'string':
        return ''
    return ":" + field_type

def build_field_list(properties, include_description=False, include_enums=False):
    fields = []
    for name, props in properties.items():
        if not props.get('calculatedProperty', False):
            # special case for attachemnts
            if name == 'attachment':
                field_name = name
            else:
                field_name = name + get_field_type(props)
            desc = '' if not include_description else props.get('description')
            enum = '' if not include_enums else props.get('enum')
            fields.append(FieldInfo(field_name, desc, enum))
    return fields

def get_uploadable_fields(connection, types, include_description=False, include_enums=False):
    fields = {}
    for name in types:
        schema_name = encodedccMod.format_schema_name(name)
        uri = '/profiles/' + schema_name
        schema_grabber = encodedccMod.ENC_Schema(connection, uri)
        fields[name] = build_field_list(schema_grabber.properties, 
                                        include_description, include_enums)

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
        ws.write(0, 0, "Field Name:")
        ws.write(1, 0, "Description:")
        ws.write(2, 0, "Enum Values:")
        for col, field in enumerate(fields):
            ws.write(0, col+1, str(field.name))
            if field.desc:
                ws.write(1, col+1, str(field.desc))
            if field.enum:
                ws.write(2, col+1, str(field.enum))
    wb.save(filename)

def main():
    args = getArgs()
    key = encodedccMod.ENC_Key(args.keyfile, args.key)
    connection = encodedccMod.ENC_Connection(key)
    fields = get_uploadable_fields(connection, args.type, 
                                        args.descriptions,
                                        args.enums)

    if args.debug:
        print("retrieved fields as")
        from pprint import pprint
        pprint(fields)

    if args.writexls:
        file_name = 'fields.xls'
        create_xls(fields,file_name)

if __name__ == '__main__':
    main()
