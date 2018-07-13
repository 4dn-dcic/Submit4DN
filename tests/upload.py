from dcicutils import ff_utils
from wranglertools.get_field_info import FDN_Key, FDN_Connection
import os
import json


def run(keypairs_file, post_json_file, schema_name):

    assert os.path.isfile(keypairs_file)

    try:
        key = FDN_Key(keypairs_file, "default")
    except Exception as e:
        print(e)
        print("key error")
        raise e

    try:
        connection = FDN_Connection(key)
    except Exception as e:
        print(e)
        print("connection error")
        raise e

    try:
        with open(post_json_file, 'r') as f:
            post_item = json.load(f)
            response = ff_utils.post_metadata(post_item, schema_name, key=connection.key)
    except Exception as e:
        print(e)
        print("post error")
        raise e

    print(json.dumps(response))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="file_reference_upload")
    parser.add_argument('-k', '--keypairs_file', help='key-pairs file')
    parser.add_argument('-p', '--post_json_file', help='key-pairs file')
    parser.add_argument('-s', '--schema', help='schema name (e.g. file_reference, workflow)')
    args = parser.parse_args()

    run(args.keypairs_file, args.post_json_file, args.schema)
