"""GET the results of a search from an ENCODE server."""
import requests
import pickle
import json
import os

OBJlist = ['Lab', 'User', 'Experiment', 'Award', 'Reference',
           'Document', 'Replicate', 'AntibodyLot', 'Source', 'Donor',
           'Treatment', 'Library', 'Biosample', 'Organism']

for OBJ in OBJlist:
    Obj = OBJ
    Opt = "&frame=object&limit=all&format=json"

    Fname = "EncodeMeta/All{}.p".format(Obj)
    if os.path.isfile(Fname):
        print '{} \t is already stored, it is skipped'.format(Obj)
        continue
    print '{} \t is processing'.format(Obj)

    # Force return from the server in JSON format
    HEADERS = {'accept': 'application/json'}

    # This searches the ENCODE database for the phrase "bone chip"
    URL = "https://www.encodeproject.org/search/?type={}{}".format(Obj, Opt)
    print URL

    # GET the search result
    response = requests.get(URL, headers=HEADERS)

    # Extract the JSON response as a python dict
    response_json_dict = response.json()

    # Write dictionary to pickle
    Fname = "All{}.p".format(Obj)
    pickle.dump(response_json_dict, open(Fname, "wb"))
    filesize = os.path.getsize(Fname)
    if filesize < 1024:
        print "\"{}\" may not be the correct object name, please check again"\
            .format(Obj)
        os.remove(Fname)

# Print the object
# print json.dumps(response_json_dict, indent=4, separators=(',', ': '))
