Submit 4DN - Data Submiter Tools
================================

|Build Status| |Coverage Status| |Code Quality| |PyPI version|

The Submit4DN package is written by the `4DN Data Coordination and
Integration Center <http://dcic.4dnucleome.org/>`__ for data submitters
from the 4DN Network. Please `contact
us <mailto:4DN.DCIC.support@hms-dbmi.atlassian.net>`__ to get access to
the system, or if you have any questions or suggestions. Detailed
documentation on data submission can be found `at this
link <https://docs.google.com/document/d/1Xh4GxapJxWXCbCaSqKwUd9a2wTiXmfQByzP0P8q5rnE/edit?usp=sharing>`__

Installing the package
----------------------

The Submit4DN package is registered with Pypi so installation is as
simple as:

::

    pip3 install submit4dn

Connection
----------

To be able to use the provided tools, you need to have a secure key to
access the REST application. If you do not have a secure key, please
contact `4DN Data
Wranglers <mailto:4DN.DCIC.support@hms-dbmi.atlassian.net>`__ to get an
account and to learn how to generate a key. Place your key in a json
file in the following format.

::

    {
      "default": {
        "key": "TheConnectionKey",
        "secret": "very_secret_key",
        "server":"www.The4dnWebsite.com"
      }
    }

The default location for the keyfile is your home directory
``~/keypairs.json``. If you prefer to use a different file location or a
different key name (not "default"), you can specify your key with the
``keyfile`` and ``key`` parameters:

::

    import_data --keyfile path/to/filename.json --key NotDefault

Generating data submission forms
--------------------------------

To create the data submission xls forms, you can use ``get_field_info``.
It will accept the following parameters:

::

    --type           use for each sheet that you want to add to the excel workbook
    --descriptions   adds the descriptions in the second line (by default True)
    --enums          adds the enum options in the third line (by default True)
    --comments       adds the comments together with enums (by default False)
    --writexls       creates the xls file (by default True)
    --outfile        change the default file name "fields.xls" to a specified one
    --order          create an ordered and filtered version of the excel (by default True)

Examples generating a single sheet:

::

    get_field_info --type Biosample
    get_field_info --type Biosample --comments
    get_field_info --type Biosample --comments --outfile biosample.xls

Complete list of sheets: ~\ :sub:`~` get\_field\_info --type Publication
--type Document --type Vendor --type Protocol --type
BiosampleCellCulture --type Biosource --type Enzyme --type Construct
--type TreatmentChemical --type TreatmentRnai --type Modification --type
Biosample --type FileFastq --type FileSet --type IndividualHuman --type
IndividualMouse --type ExperimentHiC --type ExperimentCaptureC --type
Target --type GenomicRegion --type ExperimentSet --type Image --comments
--outfile AllItems.xls ~\ :sub:`~`

Data submission
---------------

After you fill out the data submission forms, you can use
``import_data`` to submit the metadata. The method can be used both to
create new metadata items and to patch fields of existing items.

::

    import_data filename.xls

**Uploading vs Patching**

If there are uuid, alias, @id, or accession fields in the xls form that
match existing entries in the database, you will be asked if you want to
PATCH each object. You can use the ``--patchall`` flag, if you want to
patch ALL objects in your document and ignore that message.

If no object identifiers are found in the document, you need to use
``--update`` for POSTing to occur.

Development
===========

Note if you are attempting to run the scripts in the wranglertools
directory without installing the package then in order to get the
correct sys.path you need to run the scripts from the parent directory
using the following command format:

::

    python3 -m wranglertools.get_field_info —-type Biosource
    python3 -m wranglertools.import_data filename.xls

pypi page is - https://pypi.python.org/pypi/Submit4DN

The proper way to create a new release is ``invoke deploy`` which will
prompt you to update the release number, then tag the code with that
version number and push it to github, which will trigger travis to build
and test and if tests pass it will deploy to production version of pypi.
Note that travis will automatically deploy the new version if you push a
tag to git.

.. |Build Status| image:: https://travis-ci.org/hms-dbmi/Submit4DN.svg?branch=master
   :target: https://travis-ci.org/hms-dbmi/Submit4DN
.. |Coverage Status| image:: https://coveralls.io/repos/github/hms-dbmi/Submit4DN/badge.svg?branch=master
   :target: https://coveralls.io/github/hms-dbmi/Submit4DN?branch=master
.. |Code Quality| image:: https://api.codacy.com/project/badge/Grade/a4d521b4dd9c49058304606714528538
   :target: https://www.codacy.com/app/jeremy_7/Submit4DN
.. |PyPI version| image:: https://badge.fury.io/py/Submit4DN.svg
   :target: https://badge.fury.io/py/Submit4DN
   
