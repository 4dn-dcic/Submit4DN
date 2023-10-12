
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

This package is not supported on older Python versions and is supported and tested for versions 3.8 - 3.11.  It may work with other python versions but your mileage may vary.

It is recommended to install this package in a virtual environment to avoid dependency clashes.

Problems have been reported on recent MacOS X and Windows versions having to do with the inablity to find `libmagic`,
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

Additionally, problems have been reported on Windows when installing Submit4DN
inside a virtual environment, due to `aws` trying to use the global python instead
of the python inside the virtual environment.

The workaround, then, because it’s actually OK if `aws` doesn’t use the python
inside the virtual environment, is to just install `awscli` in the global
environment before entering the virtual environment. Or if you discover the
problem after you’re in, then go outside, install `awscli`, and re-enter the
virtual environment.

```
deactivate
pip install awscli
VENV\scripts\activate  # replace VENV with your virtual environment name
aws --version  # this is to test that awscli is now installed correctly
```


## Connecting to the Data Portal
To be able to use the provided tools, you need to generate an AccessKey on the [data portal](https://data.4dnucleome.org/).
If you do not yet have access, please contact [4DN Data Wranglers](mailto:support@4dnucleome.org)
to get an account and [learn how to generate and save a key](https://data.4dnucleome.org/help/submitter-guide/getting-started-with-submissions#getting-connection-keys-for-the-4dn-dcic-servers).

## Generating data submission forms
To create the data submission excel workbook, you can use `get_field_info`.

It will accept the following parameters:
~~~~
    --keyfile        the path to the file where you have stored your access key info (default ~/keypairs.json)
    --key            the name of the key identifier for the access key and secret in your keys file (default=default)
    --type           use for each sheet that you want to add to the excel workbook
    --nodesc         do not add the descriptions in the second line (by default they are added)
    --noenums        do not add the list of options for a field if they are specified (by default they are added)
    --comments       adds any (usually internal) comments together with enums (by default False)
    --outfile        change the default file name "fields.xlsx" to a specified one
    --debug          to add more debugging output
    --noadmin        if you have admin access to 4DN this option lets you generate the sheet as a non-admin user
~~~~

Examples generating a single sheet:
~~~~
get_field_info --type Biosample
get_field_info --type Biosample --comments
get_field_info --type Biosample --comments --outfile biosample.xlsx
~~~~

Example Workbook with all sheets:
~~~~
get_field_info --outfile MetadataSheets.xlsx
~~~~

Examples for Workbooks using a preset option:
~~~~
get_field_info --type HiC --comments --outfile exp_hic_generic.xlsx
get_field_info --type ChIP-seq --comments --outfile exp_chipseq_generic.xlsx
get_field_info --type FISH --comments --outfile exp_fish_generic.xlsx
~~~~

Current presets include: `Hi-C, ChIP-seq, Repli-seq, ATAC-seq, DamID, ChIA-PET, Capture-C, FISH, SPT`

## Data submission

Please refer to the [submission guidelines](https://data.4dnucleome.org/help/submitter-guide) and become familiar with the metadata structure prior to submission.

After you fill out the data submission forms, you can use `import_data` to submit the metadata. The method can be used both to create new metadata items and to patch fields of existing items.
~~~~
	import_data filename.xlsx
~~~~

#### Uploading vs Patching

Runnning `import_data` without one of the flags described below will perform a dry run submission that will include several validation checks.
It is strongly recommended to do a dry run prior to actual submission and if necessary work with a Data Wrangler to correct any errors.

If there are uuid, alias, @id, or accession fields in the excel form that match existing entries in the database, you will be asked if you want to PATCH each object.
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
	python -m wranglertools.import_data filename.xlsx
```

pypi page is - https://pypi.python.org/pypi/Submit4DN

Submit4DN is packaged with poetry.  New versions can be released and submitted to pypi using `poetry publish`

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

    # skip tests that use ftp (do this when testing locally)
    py.test -m "not ftp"
