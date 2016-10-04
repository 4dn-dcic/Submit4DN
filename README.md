# Submit 4DN - Data Submiter Tools

[![Build Status](https://travis-ci.org/hms-dbmi/Submit4DN.svg?branch=master)](https://travis-ci.org/hms-dbmi/Submit4DN)
[![Coverage Status](https://coveralls.io/repos/github/hms-dbmi/Submit4DN/badge.svg?branch=master)](https://coveralls.io/github/hms-dbmi/Submit4DN?branch=master)
[![Code Quality](https://api.codacy.com/project/badge/Grade/a4d521b4dd9c49058304606714528538)](https://www.codacy.com/app/jeremy_7/Submit4DN)
[![PyPI version](https://badge.fury.io/py/Submit4DN.svg)](https://badge.fury.io/py/Submit4DN)

##Installing the package

The Submit4DN package is registered with Pypi so installation is as simple as:

```
pip install submit4dn
```

Once installed then follow the directions below:


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

## Generate fields.xls
To create an xls file with sheets to be filled use the example and modify to your needs. It will accept the following parameters.

    --type           use for each sheet that you want to add to the excel workbook
    --descriptions   adds the descriptions in the second line (by default True)
    --enums          adds the enum options in the third line (by default True)
    --comments       adds the comments together with enums (by default False)
    --writexls       creates the xls file (by default True)
    --outfile        change the default file name "fields.xls" to a specified one
    --order          create an ordered and filtered version of the excel (by default True)

*Full list*
~~~~
python3 -m wranglertools.get_field_info --type Publication --type Document --type Vendor --type Protocol --type BiosampleCellCulture --type Biosource --type Enzyme --type Construct --type TreatmentChemical --type TreatmentRnai --type Modification --type Biosample --type FileFastq --type FileSet --type IndividualHuman --type IndividualMouse --type ExperimentHiC --type ExperimentCaptureC --type Target --type GenomicRegion --type ExperimentSet --type Image --comments --outfile AllItems.xls

~~~~
*To get a single sheet use*
```
python3 get_field_info.py --type Biosample
python3 get_field_info.py --type Biosample --comments
python3 get_field_info.py --type Biosample --comments --outfile biosample.xls

```

## Specifications for fields.xls
In fields.xls, each excel sheet is named after an object type, like ExperimentHiC, Biosample, Construct, Protocol...

*Each sheet has at least 4 rows that begin with a #*
1) Field name
2) Field type
3) Field description
4) Choices for controlled vocabulary (some fields only accept a value from a list of selection, like experiment type). NOTE if you add the optional --comments argument the comments will also be included in this row.

The first entry will start from row 4, and column 2.

Each field can be a certain type; string, number/integer, list. If the type is integer, number or array, it will be indicated with the fields name; field:number, fields:int, field:array. If the field is a string, you will only see the field name.
If the field is an array (field:list), you may enter a single item, or multiple items separated by comma.

    field:array
    item1,item2,item2,item4

Some objects containing fields that are grouped together, called embedded sub-objects. For example the "experiment_relations" has 2 fields called "relationship_type", and "experiment". In the field names you will see
* experiment_relations.relationship_type
* experiment_relations.experiment

If the embedded sub-object is a list, you can increase the number of items by creating new columns and appending numbers to the fields names
* experiment_relations.relationship_type-1
* experiment_relations.experiment-1
* experiment_relations.relationship_type-2
* experiment_relations.experiment-2


**Aliases**

When you create new object types at the same time, it is not possible to reference one item in another with an accession or uuid since it is not assigned yet. For example, if you have a new experiment with a new biosample in the same excel workbook (different sheets), what are you going to put in biosample field in experiments sheet? To overcome this problem, a lab specific identifier called alias is used. "aliases" field accepts multiple entries in the form of "labname:refname,labname:refname2" (testlab:expHic001). If you add lab:bisample1 to aliases field in biosample, you can then use this value in biosample field in experiment.


## Specifications for import_data.py
You can use import_data.py either to upload new metadata or patch fields of an existing metadata.
When you import file data, the status has to be "uploading". if you have some other status, like "uploaded" and then patch the status to "uploading", you will not be able to upload file, because the dedicated url for aws upload is creating during post if the status is uploading.

**Uploading vs Patching**

If there is a uuid, alias, @id, or accession in the document that matches and existing entry in the database, it will ask if you want to PATCH that object one by one.
If you use '--patchall' if you want to patch ALL objects in your document and ignore that message.

If no object identifiers are found in the document, you need to use '--update' for POSTing to occur.

To upload objects with attachments, use the column titled "attachment" containing the path the file you wish to attach

# Development
Note if you are attempting to run the scripts in the wranglertools directory without installing the package then in order to get the correct sys.path you need to run the scripts from the parent directory using the following command format::

    python3 -m wranglertools.get_field_info —-type Biosource
        python3 -m wranglertools.import_data filename.xls

