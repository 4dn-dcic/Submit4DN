
# Submit 4DN - Data Submitter Tools

[![Build Status](https://travis-ci.org/4dn-dcic/Submit4DN.svg?branch=master)](https://travis-ci.org/4dn-dcic/Submit4DN)
[![Coverage Status](https://coveralls.io/repos/github/4dn-dcic/Submit4DN/badge.svg?branch=master)](https://coveralls.io/github/4dn-dcic/Submit4DN?branch=master)
[![Code Quality](https://api.codacy.com/project/badge/Grade/a4d521b4dd9c49058304606714528538)](https://www.codacy.com/app/jeremy_7/Submit4DN)
[![PyPI version](https://badge.fury.io/py/Submit4DN.svg)](https://badge.fury.io/py/Submit4DN)

The Submit4DN package is written by the [4DN Data Coordination and Integration Center](http://dcic.4dnucleome.org/) for data submitters from the 4DN Network. Please [contact us](mailto:support@4dnucleome.org) to get access to the system, or if you have any questions or suggestions.  Detailed documentation on data submission can be found [at this link](https://data.4dnucleome.org/help/submitter-guide/getting-started-with-submissions)

## Installing the package

```
pip install submit4dn
```

To upgrade to the latest version

```
pip install submit4dn --upgrade
```

### Troubleshooting

This package may install and run on Python v2.7 but using this package with that version is no longer officially supported and your mileage may vary.

It is recommended to install this package in a virtual environment to avoid dependency clashes.

Problems have been reported on recent MacOS X versions having to do with the inablity to find `libmagic`,
a C library to check file types that is used by the `python-magic` library.

eg. `ImportError: failed to find libmagic.  Check your installation`

First thing to try is:

```
pip uninstall python-magic
pip install python-magic
```

If that doesn't work one solution that has worked for some from [here](https://github.com/Yelp/elastalert/issues/1927):

```
pip uninstall python-magic
pip install python-magic-bin==0.4.14
```

Others have had success using homebrew to install `libmagic`:

```
brew install libmagic
brew link libmagic  (if the link is already created is going to fail, don't worry about that)
```

## Connecting to the Data Portal
To be able to use the provided tools, you need to generate an AccessKey on the [data portal](https://data.4dnucleome.org/).
If you do not yet have access, please contact [4DN Data Wranglers](mailto:support@4dnucleome.org)
to get an account and [learn how to generate and save a key](https://data.4dnucleome.org/help/submitter-guide/getting-started-with-submissions#getting-connection-keys-for-the-4dn-dcic-servers).

## Generating data submission forms
To create the data submission xls forms, you can use `get_field_info`.

It will accept the following parameters:
~~~~
    --type           use for each sheet that you want to add to the excel workbook
    --descriptions   adds the descriptions in the second line (by default True)
    --enums          adds the enum options in the third line (by default True)
    --comments       adds the comments together with enums (by default False)
    --writexls       creates the xls file (by default True)
    --outfile        change the default file name "fields.xls" to a specified one
    --order          create an ordered and filtered version of the excel (by default True)
~~~~

Examples generating a single sheet:
~~~~
get_field_info --type Biosample
get_field_info --type Biosample --comments
get_field_info --type Biosample --comments --outfile biosample.xls
~~~~

Example Workbook with all sheets:
~~~~
get_field_info --type all --outfile MetadataSheets.xls
~~~~

Examples for Workbooks using a preset option:
~~~~
get_field_info --type HiC --comments --outfile exp_hic_generic.xls
get_field_info --type ChIP-seq --comments --outfile exp_chipseq_generic.xls
get_field_info --type FISH --comments --outfile exp_fish_generic.xls
~~~~

Current presets include: `Hi-C, ChIP-seq, Repli-seq, ATAC-seq, DamID, ChIA-PET, Capture-C, FISH, SPT`

## Data submission

Please refer to the [submission guidelines](https://data.4dnucleome.org/help/submitter-guide) and become familiar with the metadata structure prior to submission.

After you fill out the data submission forms, you can use `import_data` to submit the metadata. The method can be used both to create new metadata items and to patch fields of existing items.
~~~~
	import_data filename.xls
~~~~

#### Uploading vs Patching

Runnning `import_data` without one of the flags described below will perform a dry run submission that will include several validation checks.
It is strongly recommended to do a dry run prior to actual submission and if necessary work with a Data Wrangler to correct any errors.

If there are uuid, alias, @id, or accession fields in the xls form that match existing entries in the database, you will be asked if you want to PATCH each object.
You can use the `--patchall` flag, if you want to patch ALL objects in your document and ignore that message.

If no object identifiers are found in the document, you need to use `--update` for POSTing to occur.

**Other Helpful Advanced parameters**

Normally you are asked to verify the **Lab** and **Award** that you are submitting for.  In some cases it may be desirable to skip this prompt so a submission
can be run by a scheduler or in the background:

`--remote` is an option that will skip any prompt before submission

**However** if you submit for more than one Lab or there is more than one Award associated with your lab you will need to specify these values
as parameters using `--lab` and/or `--award` followed by the uuids for the appropriate items.

<img src="https://media.giphy.com/media/l0HlN5Y28D9MzzcRy/giphy.gif" width="200" height="200" />


# Development
Note if you are attempting to run the scripts in the wranglertools directory without installing the package then in order to get the correct sys.path you need to run the scripts from the parent directory using the following command format:

```
  python -m wranglertools.get_field_info —-type Biosource
	python -m wranglertools.import_data filename.xls
```

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

    # Run only tests with file_operation
    py.test -m file_operation

For a better testing experienece that also check to ensure sufficient coverage and runs linters use invoke:

```
   invoke test
```

This will first run linters, if linters pass, tests will be run and if tests achieve specified minimum coverage (89% as of time of writting) pass the tests.
