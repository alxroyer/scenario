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


.. _coding-rules.files:

File conventions
================

.. _coding-rules.files.permissions:

File permissions
----------------

File permissions are stored apropriately in the git database, so that:

- regular files remain with 644 permissions,
- executable scripts and binaries get the 755 permissions.

The '.repo/checkfiles.yml' file describes the permissions applicable to each file of the repository.


.. _coding-rules.files.encodings:

Encodings
---------

Encoding is utf-8 for all files.

The encoding is explicitly specified in the first lines of Python scripts through:

.. code-block:: python

    # -*- coding: utf-8 -*-

The '.repo/checkfiles.yml' file describes the encoding applicable to each file of the repository.


.. _coding-rules.files.max-line-length:

Maximum line length
-------------------

The maximum line length is 160 (any kind of language).

.. admonition:: PyCharm configuration for maximum line length
    :class: tip

    Memo for PyCharm related configurations:

    - Editor > Code Style > Hard wrap at: Set 160
    - Editor > Code Style: Enable "Wrap on typing"
    - Editor > General > Appearance: Enable "Show hard wrap and visual guides"
