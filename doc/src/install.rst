.. Copyright 2020-2022 Alexis Royer <https://github.com/Alexis-ROYER/scenario>
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

- Python 3.6 or later (`https://www.python.org/downloads/ <https://www.python.org/downloads/>`_)

Recommended:

- mypy (`https://pypi.org/project/mypy/ <https://pypi.org/project/mypy/>`_), tested with version 0.931
- pytz (`https://pypi.org/project/pytz/ <https://pypi.org/project/pytz/>`_)
- PyYAML (`https://pypi.org/project/PyYAML/ <https://pypi.org/project/PyYAML/>`_)

Documentation generation (optional):

- Sphinx (`https://pypi.org/project/Sphinx/ <https://pypi.org/project/Sphinx/>`_)
- Java


From sources
------------

Clone the project sources:

.. code-block:: bash

    $ git clone https://github.com/Alexis-ROYER/scenario.git

Use the 'bin/run-test.py' or 'bin/run-campaign.py' launchers directly.
Let's say you had cloned the project in '/path/to/scenario':

.. code-block:: bash

    $ /path/to/scenario/bin/run-test.py --help
    $ /path/to/scenario/bin/run-campaign.py --help
