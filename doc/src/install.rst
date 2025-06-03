.. Copyright 2020-2023 Alexis Royer <https://github.com/alxroyer/scenario>
..
.. Licensed under the Apache License, Version 2.0 (the "License");
.. you may not use this file except in compliance with the License.
.. You may obtain a copy of the License at
..
..     http://www.apache.org/licenses/LICENSE-2.0
..
.. Unless required by applicable law or agreed to in writing, software
.. distributed under the License is distributed on an "AS IS" BASIS,
.. WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
.. See the License for the specific language governing permissions and
.. limitations under the License.


.. _install:

Installation
============

Prerequisites
-------------

Mandatory:

- Python 3.6 or later (https://www.python.org/downloads/)

  - Python >= 3.7 recommended (for compatibility with mypy v1.0.0).
  - Tested versions:

    - 3.6.8
    - 3.7.9

Recommended:

- pytz (https://pypi.org/project/pytz/):
  extended timezone support

- PyYAML (https://pypi.org/project/PyYAML/):
  optional support for YAML files

.. tip::

    In order to help installing recommended packages,
    generally in a `venv` environment,
    a 'requirements/recommended.txt' file is provided:

    .. code-block:: bash

        # In your user project directory, initiate a `venv` environment.
        $ python -m venv .venv
        $ source .venv/Scripts/activate

        # Install recommended requirements.
        $ pip install -r /path/to/scenario/requirements/recommended.txt


Development dependencies:

- Java

  - Tested with version 11.0.14.

- mypy (https://pypi.org/project/mypy/)

  - Versions prior to 1.0.0 not supported anymore.
  - Tested versions:

    - 1.0.1 (Python 3.7.9).

- PyYAML (https://pypi.org/project/PyYAML/)

- Sphinx (https://pypi.org/project/Sphinx/)

  - Tested versions:

    - 4.4.0 (Python 3.6.8, `typed_ast` installed, cross-references to typehints may not work)
    - 5.3.0 (Python 3.7.9, `typed_ast` installed)
    - 6.1.3 (Python 3.8.15, on readthedocs)

.. tip::

    Same as for recommended packages,
    a 'requirements/dev.txt' file is provided for Python development dependencies installation:

    .. code-block:: bash

        # In the scenario project directory, initiate a `venv` environment.
        $ cd /path/to/scenario/
        $ python -m venv .venv
        $ source .venv/Scripts/activate

        # Install development dependencies.
        $ pip install -r ./requirements/dev.txt


From sources
------------

Clone the project sources:

.. code-block:: bash

    $ git clone https://github.com/alxroyer/scenario

Use the 'bin/run-test.py' or 'bin/run-campaign.py' launchers directly.
Let's say you had cloned the project in '/path/to/scenario':

.. code-block:: bash

    $ /path/to/scenario/bin/run-test.py --help
    $ /path/to/scenario/bin/run-campaign.py --help
