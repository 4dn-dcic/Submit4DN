#!/usr/bin/env python3
# -*- coding: latin-1 -*-
import os.path
import argparse
import encodedccMod

EPILOG = '''
    To get multiple objects use the '--object' argument
    and provide a file with the list of object identifiers

            %(prog)s --object filenames.txt

        this can take accessions, uuids, @ids, or aliases

    To get a single object use the '--object' argument
    and use the object's identifier, also will take a comma separated list

            %(prog)s --object ENCSR000AAA
            %(prog)s --object 3e6-some-uuid-here-e45
            %(prog)s --object this-is:an-alias
            %(prog)s --object ENCSR000AAA,ENCSR000AAB

    To get multiple fields use the '--field' argument
    and feed it a file with the list of fieldnames

            %(prog)s --field fieldnames.txt

        this should be a single column file

    To get a single field use the field argument:

            %(prog)s --field status
            %(prog)s --field status,target.title

    where field is a string containing the field name
    or a comma separated list of fieldnames,
    (this can be combined with the embedded values)

    To get embedded field values (such as target name from an experiment):

            %(prog)s --field target.title

        accession       target.title
        ENCSR087PLZ     H3K9ac (Mus musculus)
        this can also get embedded values from lists

            %(prog)s --field files.status
            *more about this feature is listed below*

    To use a custom query for your object list:

            %(prog)s --query www.my/custom/url

        this can be used with either useage of the '--field' option

    Output prints in format of fieldname:object_type for non-strings

        Ex: accession    read_length:int    documents:list
            ENCSR000AAA  31                 [document1,document2]

        integers  ':int'
        lists     ':list'
        string are the default and do not have an identifier
    ***please note that list type fields will show only unique items***

            %(prog)s --field files.status --object ENCSR000AAA

        accession       file.status:list
        ENCSR000AAA     ['released']

    possible output even if multiple files exist in experiment

    To show all possible outputs from a list type field
    use the '--listfull' argument

            %(prog)s --field files.status --listfull

        accession       file.status:list
        ENCSR000AAA     ['released', 'released', 'released']


        *** ENCODE_collection useage and functionality  ***
    %(prog)s has ported over some functions of ENCODE_collection
    and now supports the '--collection' and '--allfields' options

    Useage for '--allfields':

            %(prog)s --object ENCSR000AAA --allfields

        accession    status    files        award ...
        ENCSR000AAA  released  [/files/...] /awards/...

    The '--allfields' option can be used with any of the commands,
    it returns all fields at the frame=object level,
    it also overrides any other --field option


    Useage for '--collection':

            %(prog)s --collection Experiment --status

        accession    status
        ENCSR000AAA  released

    The  '--collection' option can be used with or without the '--es' option
    the '--es' option allows the script to search using elastic search,
    which is slightly faster than the normal table view used
    However, it may not posses the latest updates to the data and may not be
    preferable to your application
    '--collection' also overrides any other '--object' option and so but it
    can be combined with any of the '--field' or '--allfields' options

    NOTE: while '--collection' should work with the '--field' field.embeddedfield
    functionality I cannot guarantee speed when running due to embedded
    objects being extracted

    '''


def getArgs():
    parser = argparse.ArgumentParser(
        description=__doc__, epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        )
    parser.add_argument('--type',
                        help="Add a seperate --type for each type you want to get.",
                        action="append")
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


def get_field_type(field):
    field_type = field.get('type', '')
    if field_type == 'string':
        return ''
    return ":" + field_type

def build_field_list(properties):
    fields = []
    for name, props in properties.items():
        if not props.get('calculatedProperty', False):
            fields.append(name + get_field_type(props))

    return fields

def main():
    args = getArgs()
    key = encodedccMod.ENC_Key(args.keyfile, args.key)
    connection = encodedccMod.ENC_Connection(key)
    for name in args.type:
        fieldlist = []
        schema_name = encodedccMod.format_schema_name(name)
        uri = '/profiles/' + schema_name
        schema_grabber = encodedccMod.ENC_Schema(connection, uri)
        fieldlist = build_field_list(schema_grabber.properties)
        print('\t'.join(fieldlist))


if __name__ == '__main__':
    main()
