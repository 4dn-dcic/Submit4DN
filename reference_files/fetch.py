import wranglertools.fdnDCIC as fdnDCIC
import os
import json

def run(keypairs_file):

  assert os.path.isfile(str(keypairs_file))

  post_json_file = "file_reference.json"

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
    #response = fdnDCIC.get_FDN("/profiles/file_reference.json", connection, frame="object")
    response = fdnDCIC.get_FDN("/files_reference", connection, frame=None)
  except Exception as e:
    print(e)
    print("post error")
    raise e

  print(response)


if __name__ == "__main__":
  import argparse

  parser = argparse.ArgumentParser(description="file_reference_upload")
  parser.add_argument('-k','--keypairs_file',help='key-pairs file')
  args = parser.parse_args()

  run(args.keypairs_file)

