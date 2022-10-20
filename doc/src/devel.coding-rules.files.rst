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


.. _coding-rules.files:

Files
-----

.. _coding-rules.files.permissions:

File permissions
^^^^^^^^^^^^^^^^

File permissions are stored apropriately in the git database, so that:

- regular files remain with 644 permissions,
- executable scripts and binaries get the 755 permissions.

As long as the ``chmod`` command is available in the development environment,
the ``tools/checkrepo.py`` script checks this rule over the files of the git repository.


.. _coding-rules.files.encodings:

Encodings
^^^^^^^^^

Encoding is utf-8 for all files.

The encoding is explicitely specified in the first lines of Python scripts through:

.. code-block:: python

    # -*- coding: utf-8 -*-

The ``tools/checkrepo.py`` script checks this rule over the files of the git repository.
