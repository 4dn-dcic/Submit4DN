# Submit 4DN - Data Submiter Tools

[![Build Status](https://travis-ci.org/hms-dbmi/Submit4DN.svg?branch=master)](https://travis-ci.org/hms-dbmi/Submit4DN)
[![Coverage Status](https://coveralls.io/repos/github/hms-dbmi/Submit4DN/badge.svg?branch=master)](https://coveralls.io/github/hms-dbmi/Submit4DN?branch=master)
[![Code Quality](https://api.codacy.com/project/badge/Grade/a4d521b4dd9c49058304606714528538)](https://www.codacy.com/app/jeremy_7/Submit4DN)
[![PyPI version](https://badge.fury.io/py/Submit4DN.svg)](https://badge.fury.io/py/Submit4DN)

The Submit4DN package is written by the [4DN Data Coordination and Integration Center](http://dcic.4dnucleome.org/) for data submitters from the 4DN Network. Please [contact us](mailto:4DN.DCIC.support@hms-dbmi.atlassian.net) to get access to the system, or if you have any questions or suggestions.

## Installing the package

The Submit4DN package is registered with Pypi so installation is as simple as:

```
pip3 install submit4dn
```


## Connection
To be able to use the provided tools, you need to have a secure key to access the REST application.
If you do not have a secure key, please contact [4DN Data Wranglers](mailto:4DN.DCIC.support@hms-dbmi.atlassian.net)
to get an account and to learn how to generate a key. Place your key in a json file in the following format.

    {
      "default": {
        "key": "TheConnectionKey",
        "secret": "very_secret_key",
        "server":"www.The4dnWebsite.com"
      }
    }

The default path for your keyfile is `/Users/<user>/keypairs.json`.
If you prefer to use a different file location or a different key name (not "default"), you can specify your key with the `keyfile` and `key` parameters:

    python3 code.py --keyfile nameoffile.json --key NotDefault

## Generating data submission forms
To create the data submission xls forms, you can use the `wranglertools.get_field_info` method.
It will accept the following parameters:

    --type           use for each sheet that you want to add to the excel workbook
    --descriptions   adds the descriptions in the second line (by default True)
    --enums          adds the enum options in the third line (by default True)
    --comments       adds the comments together with enums (by default False)
    --writexls       creates the xls file (by default True)
    --outfile        change the default file name "fields.xls" to a specified one
    --order          create an ordered and filtered version of the excel (by default True)


Examples generating a single sheet:
```
python3 get_field_info.py --type Biosample
python3 get_field_info.py --type Biosample --comments
python3 get_field_info.py --type Biosample --comments --outfile biosample.xls

```

Complete list of sheets:
~~~~
python3 -m wranglertools.get_field_info --type Publication --type Document --type Vendor --type Protocol --type BiosampleCellCulture --type Biosource --type Enzyme --type Construct --type TreatmentChemical --type TreatmentRnai --type Modification --type Biosample --type FileFastq --type FileSet --type IndividualHuman --type IndividualMouse --type ExperimentHiC --type ExperimentCaptureC --type Target --type GenomicRegion --type ExperimentSet --type Image --comments --outfile AllItems.xls
~~~~


## Data submission
After you fill out the data submission forms, you can use the `wranglertools.import_data` method to submit the metadata. The method can be used both to create new metadata items and to patch fields of existing items.

	python3 -m wranglertools.import_data filename.xls

**Uploading vs Patching**

If there are uuid, alias, @id, or accession fields in the xls form that match existing entries in the database, you will be asked if you want to PATCH each object.
You can use the `--patchall` flag, if you want to patch ALL objects in your document and ignore that message.

If no object identifiers are found in the document, you need to use `--update` for POSTing to occur.


# Development
Note if you are attempting to run the scripts in the wranglertools directory without installing the package then in order to get the correct sys.path you need to run the scripts from the parent directory using the following command format::

    python3 -m wranglertools.get_field_info —-type Biosource
	python3 -m wranglertools.import_data filename.xls

