
##Connection
first thing you need is the keyfile to access the REST application
it is a json formatted file that contains key,secret and server
under one identifier. Here is the default structure. The default path
is /Users/user/keypairs.json

    {
      "default": {
        "key": "TheConnectionKey",
        "secret": "very_secret_key",
        "server":"www.The4dnWebsite.com"
      }
    }
if file name is different and the key is not named default add it to the code:
python3 code.py --keyfile nameoffile.json --key NotDefault

##Generate fields.xls
To create an xls file with sheets to be filled use the example and modify to your needs.
--descriptions   adds the descriptions in the second line
--enums adds the enum options in the third line

python3 get_field_info.py --type User --type Award --type Lab --type Organism --type Publication --type Document --type Vendor --type Protocol --type ProtocolsCellCulture --type Biosource --type Enzyme --type Construct --type TreatmentRnai --type Modification --type Biosample --type File --type FileSet --type IndividualHuman --type IndividualMouse --type ExperimentHiC --type ExperimentSet --descriptions --enums --writexls


To get a single sheet use
'''
python3 get_field_info.py --type Lab --descriptions --enums --writexls
python3 get_field_info.py --type ExperimentCaptureC --descriptions --enums --writexls --outfile HiC2.xls
'''
