
# Submit 4DN - Data Submitter Tools

[![Build Status](https://travis-ci.org/4dn-dcic/Submit4DN.svg?branch=master)](https://travis-ci.org/4dn-dcic/Submit4DN)
[![Coverage Status](https://coveralls.io/repos/github/4dn-dcic/Submit4DN/badge.svg?branch=master)](https://coveralls.io/github/4dn-dcic/Submit4DN?branch=master)
[![Code Quality](https://api.codacy.com/project/badge/Grade/a4d521b4dd9c49058304606714528538)](https://www.codacy.com/app/jeremy_7/Submit4DN)
[![PyPI version](https://badge.fury.io/py/Submit4DN.svg)](https://badge.fury.io/py/Submit4DN)

The Submit4DN package is written by the [4DN Data Coordination and Integration Center](http://dcic.4dnucleome.org/) for data submitters from the 4DN Network. Please [contact us](mailto:support@4dnucleome.org) to get access to the system, or if you have any questions or suggestions.  Detailed documentation on data submission can be found [at this link](https://docs.google.com/document/d/1Xh4GxapJxWXCbCaSqKwUd9a2wTiXmfQByzP0P8q5rnE/edit?usp=sharing)

## Installing the package

The Submit4DN package is registered with Pypi so installation is as simple as:

```
pip3 install submit4dn
```

To upgrade to the latest version

```
pip3 install submit4dn --upgrade
```

### Troubleshooting

If you encounter an error containing something like:

```
 Symbol not found: _PyInt_AsLong
```

Then it means that the imaging library Pillow / PIL is missing some required libraries.  You can fix it by doing the following.

```shell
$ pip uninstall pillow
$ brew install libjpeg zlib libtiff littlecms webp openjpeg tcl-tk
$ pip install pillow
```

That should fix it!


Once installed then follow the directions below:



## Connection
To be able to use the provided tools, you need to have a secure key to access the REST application.
If you do not have a secure key, please contact [4DN Data Wranglers](mailto:support@4dnucleome.org)
to get an account and to learn how to generate a key. Place your key in a json file in the following format.

    {
      "default": {
        "key": "TheConnectionKey",
        "secret": "very_secret_key",
        "server":"www.The4dnWebsite.com"
      }
    }

The default location for the keyfile is your home directory `~/keypairs.json`.
If you prefer to use a different file location or a different key name (not "default"), you can specify your key with the `keyfile` and `key` parameters:

    import_data --keyfile path/to/filename.json --key NotDefault

## Generating data submission forms
To create the data submission xls forms, you can use `get_field_info`.
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
get_field_info --type Biosample
get_field_info --type Biosample --comments
get_field_info --type Biosample --comments --outfile biosample.xls

```

Example list of sheets:
~~~~
get_field_info --type Publication --type Document --type Vendor --type Protocol --type BiosampleCellCulture --type Biosource --type Enzyme --type Construct --type TreatmentAgent --type TreatmentRnai --type Modification --type Biosample --type FileFastq --type IndividualMouse --type ExperimentHiC --type ExperimentSetReplicate --type ExperimentCaptureC --type BioFeature --type GenomicRegion --type ExperimentSet --type Image --comments --outfile MetadataSheets.xls
~~~~

Example list of sheets: (using python scripts)
~~~~
python3 -m wranglertools.get_field_info --type Publication --type Document --type Vendor --type Protocol --type BiosampleCellCulture --type Biosource --type Enzyme --type Construct --type TreatmentAgent --type TreatmentRnai --type Modification --type Biosample --type FileFastq --type IndividualHuman --type ExperimentHiC --type ExperimentCaptureC --type BioFeature --type GenomicRegion --type ExperimentSet --type ExperimentSetReplicate --type Image --comments --outfile MetadataSheets.xls
~~~~

Example list of sheets: (Experiment seq)
~~~~
python3 -m wranglertools.get_field_info --type Publication --type Document --type Vendor --type Protocol --type BiosampleCellCulture --type Biosource --type Enzyme --type Construct --type TreatmentAgent --type TreatmentRnai --type Modification --type Biosample --type FileFastq --type ExperimentSeq --type BioFeature --type GenomicRegion --type ExperimentSet --type ExperimentSetReplicate --type Image --comments --outfile exp_seq_all.xls
~~~~

Example list of sheets: (Experiment seq simple)
~~~~
python3 -m wranglertools.get_field_info --type Publication --type Protocol --type BiosampleCellCulture --type Biosource --type Biosample --type FileFastq --type ExperimentSeq --type ExperimentSetReplicate --type Image --comments --outfile exp_seq_simple.xls
~~~~

Examples for list of sheets using a preset option:
~~~~
python3 -m wranglertools.get_field_info --type HiC --comments --outfile exp_hic_generic.xls
python3 -m wranglertools.get_field_info --type ChIP-seq --comments --outfile exp_chipseq_generic.xls
python3 -m wranglertools.get_field_info --type FISH --comments --outfile exp_fish_generic.xls
~~~~




## Data submission
After you fill out the data submission forms, you can use `import_data` to submit the metadata. The method can be used both to create new metadata items and to patch fields of existing items.

	import_data filename.xls

**Uploading vs Patching**

If there are uuid, alias, @id, or accession fields in the xls form that match existing entries in the database, you will be asked if you want to PATCH each object.
You can use the `--patchall` flag, if you want to patch ALL objects in your document and ignore that message.

If no object identifiers are found in the document, you need to use `--update` for POSTing to occur.

Please refer to the submission guidelines provided by data wranglers, and get familiar with the metadata structure on example excel workbooks, like one for Rao et al data. You can find examples under the folder "Data Files". Once you understand how to fill in the fields in the excel workbook

<img src="https://media.giphy.com/media/l0HlN5Y28D9MzzcRy/giphy.gif" width="200" height="200" />

`--remote` is an option that will skip any prompt before submission, and useful if you are submitting LSF jobs where you expect to run automatically. You should take care of your submitting lab and award if you have multiple, since the first ones on your list will be assigned as default.

# Development
Note if you are attempting to run the scripts in the wranglertools directory without installing the package then in order to get the correct sys.path you need to run the scripts from the parent directory using the following command format:

    python3 -m wranglertools.get_field_info —-type Biosource
	python3 -m wranglertools.import_data filename.xls

pypi page is - https://pypi.python.org/pypi/Submit4DN


The proper way to create a new release is `invoke deploy` which will prompt
you to update the release number, then tag the code with that version number
and push it to github, which will trigger travis to build and test and if
tests pass it will deploy to production version of pypi. Note that travis will
automatically deploy the new version if you push a tag to git.

# Pytest
Every function is tested by pytest implementation. It can be run in terminal in submit4dn folder by:

    py.test

Some tests need internet access, and labeled with "webtest" mark.

Some tests have file operations, and labeled with "file_operation" mark.

To run the mark tests, or exclude them from the tests you can use the following commands:

    # Run all tests
    py.test

    # Run only webtest
    py.test -m webtest

    # Run only tests with file_opration
    py.test -m file_operation

For a better testing experienece that also check to ensure sufficient coverage and runs linters use invoke:

```
   invoke test
```

This will first run linters, if linters pass, tests will be run and if tests achieve specified minimum coverage (89% as of time of writting) pass the tests.
