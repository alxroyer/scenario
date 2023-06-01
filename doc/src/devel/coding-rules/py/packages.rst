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


.. _coding-rules.py.packages:

Packages
========

Even though Python 3 automatically defines packages from directories,
every package should contain a dedicated '__init__.py' file in order to explicitize the way the package is defined:

1. If it exports nothing by default,
   but just holds public modules or subpackages (without a leading underscore) to load explicitly,
   this shall be mentioned in the docstring of the package, in the '__init__.py' file.

2. Otherwise, the '__init__.py' file declares the symbols it officially exports:

   - The package shall be implemented with :ref:`private modules <coding-rules.py.namings.modules>` (with a leading underscore).
   - Reexports should follow the :ref:`reexport rules <coding-rules.py.reexports>` described just after.

.. admonition:: Packages and subpackages defined from different directories
    :class: tip

    For the memo, ``pkgutil.extend_path()`` helps defining packages and subpackages of the same package at different locations.

    For instance:

    - The base :py:mod:`scenario` package is defined in the main 'src/' directory.
    - :py:mod:`scenario.test` comes as a subpackage of the latter, but is defined in 'test/src/'.
    - Same with :py:mod:`scenario.tools`, defined in 'tools/src/'.

    This avoids mixing test and tools sources with the core :py:mod:`scenario` implementation.
