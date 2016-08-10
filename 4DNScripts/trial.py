"""trial."""
import FDNdcic
import os.path
import argparse

EPILOG = '''
    To get multiple objects use the '--object' argument
    and provide a file with the list of object identifiers

            %(prog)s --object filenames.txt
    '''

def getArgs():
    parser = argparse.ArgumentParser(
        description=__doc__, epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        )
    parser.add_argument('--object',
                        help="Either the file containing a list of ENCs as a column\
                        or this can be a single accession by itself")
    parser.add_argument('--query',
                        help="A custom query to get accessions.")
    parser.add_argument('--field',
                        help="Either the file containing single column of fieldnames\
                        or the name of a single field")
    parser.add_argument('--listfull',
                        help="Normal list-type output shows only unique items\
                        select this to list all values even repeats. Default is False",
                        default=False,
                        action='store_true')
    parser.add_argument('--allfields',
                        help="Overrides other field options and gets all fields\
                        from the frame=object level. Default is False",
                        default=False,
                        action='store_true')
    parser.add_argument('--collection',
                        help="Overrides other object options and returns all\
                        objects from the selected collection")
    parser.add_argument('--es',
                        help="Used for collections, uses elastic search instead of table view",
                        default=False,
                        action='store_true')
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


def main():
    args = getArgs()
    key = FDNdcic.FDN_Key(args.keyfile, args.key)
    connection = FDNdcic.FDN_Connection(key)
    output = FDNdcic.GetFields(connection, args)
    output.get_fields()

if __name__ == '__main__':
    main()
