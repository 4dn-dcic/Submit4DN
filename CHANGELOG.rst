===============
Submit4DN
===============

----------
Change Log
----------

3.4.2
=====

`PR 172: fix bug in get_upload_credentials <https://github.com/4dn-dcic/Submit4DN/pull/172>`_

* Bug fix that was introduced in the previous bug fix for extra_file upload creds that affected regular file upload


3.4.1
=====

`PR 170: fix bug in extra file upld <https://github.com/4dn-dcic/Submit4DN/pull/170>`_

* Update to allow extra_files to be uploaded even if the regular file was already uploaded (which was previously stymied by permission denied for POST to get extracreds)

3.4.0
=====

`PR 161: update error report <https://github.com/4dn-dcic/Submit4DN/pull/169>`_

* Updated 'error_report' function to handle additional output on validation exceptions due to fourfront schema version update
* added some additional test cases for this
* increased allowed line lenght in .flake8
* updated lock file with updated version of dcicutils


3.3.0
=====

Added/modified config files:

* ``.flake8``

  * declare expected line length, etc.

* ``pytest.ini``

  * Declare mark keywords (``pytest.mark.xxx``)

* ``Makefile``

  * Add targets ``clear-poetry-cache``, ``lint``, ``tag-and-push``
  * Make test target exclude ``pytest.mark.ftp``
  * Load (pinned) ``poetry 1.3.2``

* ``pyproject.toml``

  * update library versions, including ``poetry_core``.

* ``scripts/tag-and-push``

  * supports make target ``tag-and-push``

* ``tests/`` and ``wranglertools/``

  * misc PEP8


3.2.0
=====

* dependencies update - update lock file to resolve dependabot alerts 

3.1.2
=====

* update to ubuntu version 20.04 in github workflows

3.1.1
=====

* Bug fix: some "empty" cells were not handled correctly.

3.1.0
=====

`PR 161 <https://github.com/4dn-dcic/Submit4DN/pull/161>`_

* Added documentation regarding how to install Submit4DN on Windows machines in
  a virtual environment. There is a bug in ``awscli`` or in ``pyenv-win``, which
  requires to adjust the installation instructions for this use case (see
  troubleshooting in ``README.md`` for details).

* Added support for ``~`` in paths for file and attachment upload.

* Bug fix: a ``show`` command was giving intermittent errors.

3.0.1
=====

* Bug fix: Windows paths were not handled properly for File upload and keyfile handling.

3.0.0
=======

`PR 159: Remove Python3.6 support <https://github.com/4dn-dcic/Submit4DN/pull/159>`_

* Drop support for Python3.6

* Add this CHANGELOG and test warning if it's not updated

* Update dependency to use dcicutils >=4.0

2.2.0
=====

2.0.3
=====

2.0.0
=====

1.2.4
=====

1.2.2
=====

1.2.1
=====

1.2.0
=====

1.1.6
=====

1.1.5
=====

1.1.4
=====

1.1.3
=====

1.1.2
=====

1.1.1
=====

1.1.0
=====

1.0.9
=====

1.0.8
=====

1.0.7
=====

1.0.6
=====

1.0.5
=====

1.0.4
=====

1.0.3
=====

1.0.2
=====

1.0.1
=====

1.0.0
=====

0.9.22
======

0.9.21
======

0.9.20
======

0.9.19
======

0.9.17
======

0.9.16
======

0.9.15
======

0.9.14
======

0.9.13
======

0.9.12
======

0.9.11
======

0.9.10
======

0.9.9
=====

0.9.7
=====

0.9.6
=====

0.9.5
=====

0.9.4
=====

0.9.3
=====

0.9.2
=====

0.9.1
=====

0.9.0
=====

0.8.9
=====

0.8.8
=====

0.8.7
=====

0.8.6
=====

0.8.5
=====

0.8.4
=====

0.8.3
=====

0.8.2
=====

0.8.1
=====

0.8.0
=====

0.7.2
=====

0.7.1
=====

0.7.0
=====

0.6.0
=====

0.5.1
=====

0.5.0
=====

0.4.0
=====

0.3.0
=====

0.2.3
=====

0.2.2
=====
