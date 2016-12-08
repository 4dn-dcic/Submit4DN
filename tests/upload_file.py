import wranglertools.fdnDCIC as fdnDCIC
import wranglertools.import_data as import_data
from wranglertools.fdnDCIC import md5
import os


def run(keypairs_file, accession, filename_to_post):

    assert os.path.isfile(keypairs_file)
    assert os.path.isfile(filename_to_post)

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
        resp = fdnDCIC.get_FDN("/" + accession, connection)
        print(resp)
        item_uuid = resp.get('uuid')
    except Exception as e:
        print(e)
        print("get error")
        raise e

    try:
        # add the md5
        print("calculating md5 sum for file %s " % (filename_to_post))
        patch_item = {'md5sum': md5(filename_to_post), 'status': 'uploading'}
        e = fdnDCIC.patch_FDN(item_uuid, connection, patch_item)
        print(e)
        import_data.upload_file(e, filename_to_post)

    except Exception as e:
        print(e)
        print("file upload error")
        raise e


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="file_upload")
    parser.add_argument('-k', '--keypairs_file', help='key-pairs file')
    parser.add_argument('-a', '--accession', help='file accession')
    parser.add_argument('-f', '--filename_to_post', help='filename (local) to upload')

    args = parser.parse_args()

    run(args.keypairs_file, args.accession, args.filename_to_post)
