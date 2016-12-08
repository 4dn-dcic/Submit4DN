import wranglertools.fdnDCIC as fdnDCIC
import os
import json


def run(keypairs_file, post_json_file, schema_class_name):

    assert os.path.isfile(keypairs_file)

    try:
        key = fdnDCIC.FDN_Key(keypairs_file, "default")
    except Exception as e:
        print(e)
        print("key error")
        raise e

    try:
        connection = fdnDCIC.FDN_Connection(key)
    except Exception as e:
        print(e)
        print("connection error")
        raise e

    try:
        with open(post_json_file, 'r') as f:
            patch_item = json.load(f)
            resp = fdnDCIC.get_FDN("/search/?type=" + schema_class_name, connection)
            items_uuids = [i['uuid'] for i in resp['@graph']]
    except Exception as e:
        print(e)
        print("get error")
        raise e

    try:
        for item_uuid in items_uuids:
            response = fdnDCIC.patch_FDN(item_uuid, connection, patch_item)
            print(json.dumps(response))
    except Exception as e:
        print(e)
        print("get error")
        raise e



if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="file_reference_upload")
    parser.add_argument('-k', '--keypairs_file', help='key-pairs file')
    parser.add_argument('-p', '--post_json_file', help='key-pairs file')
    parser.add_argument('-c', '--schema_class', help='schema class name (e.g. FileReference, Workflow)')

    args = parser.parse_args()

    run(args.keypairs_file, args.post_json_file, args.schema_class)
