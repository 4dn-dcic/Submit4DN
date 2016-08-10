"""GET the results of a search from an ENCODE server."""
import requests
import pickle
import json
import os
import pandas

OBJlist = [
    'User',
    'Award',
    'Lab',
    'Organism',
    'Publication',
    'Document',
    'Vendor',
    'Protocol',
    'ProtocolsCellCulture',
    'IndividualHuman',
    'IndividualMouse',
    'Biosource',
    'Enzyme',
    'Construct',
    'TreatmentRnai',
    'Modification',
    'Biosample',
    'File',
    'FileSet',
    'ExperimentHiC',
    'ExperimentSet',
    'Software',
    'Page'
    ]

for OBJ in OBJlist:
    Obj = OBJ
    Opt = "&format=json"
    fname = ""
    fname = "4DNScripts/Samples/All_{}.txt".format(Obj)
    if os.path.isfile(fname):
        print '{} \t is already stored, it is skipped'.format(Obj)
        continue
    print '{} \t is processing'.format(Obj)

    # Force return from the server in JSON format
    HEADERS = {'accept': 'application/json'}

    # This searches the ENCODE database for the phrase "bone chip"
    URL = "http://4dn-web-dev.us-east-1.elasticbeanstalk.com/search/?type={}{}".format(Obj, Opt)
    print URL

    # GET the search result
    response = requests.get(URL, headers=HEADERS)

    # Extract the JSON response as a python dict
    response_json_dict = response.json()

    # Check if there is an @graph key
    try:
        allitems = response_json_dict["@graph"]
    except:
        print "\"{}\" may not be the correct object name, please check again".format(Obj)
        continue

    # write dictionary to tab delimeted file
    df = pandas.DataFrame.from_records(allitems)
    CSV = df.to_csv(fname, sep='\t', index=False)






# Print the object
# print json.dumps(response_json_dict, indent=4, separators=(',', ': '))
