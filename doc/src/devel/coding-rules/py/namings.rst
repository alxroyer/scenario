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


.. _coding-rules.py.namings:

Namings
=======

Python namings follow `PEP 8 <https://peps.python.org/pep-0008/#descriptive-naming-styles>`_ recommandations.
Let's remind them below:


.. _coding-rules.py.namings.packages:
.. _coding-rules.py.namings.modules:

Packages and modules
--------------------

Lowercase, without underscores.

.. note::
    As stated in `PEP 8 - Package and module names <https://peps.python.org/pep-0008/#package-and-module-names>`_
    "the use of underscores is discouraged".

Leading underscore for internal packages and modules.

.. note::
    Makes it possible to set :ref:`design a package <coding-rules.py.packages>` with protected modules,
    and explicitly select the symbols exported from them in the '__init__.py' module.


.. _coding-rules.py.namings.classes:
.. _coding-rules.py.namings.exceptions:
.. _coding-rules.py.namings.enum-classes:

Classes
-------

CamelCase, without underscores.

Leading underscore for internal classes.

Applicable to exceptions and enum classes.


.. _coding-rules.py.namings.types:

Types
-----

CamelCase, without underscores.

Leading underscore for internal types.


.. _coding-rules.py.namings.functions:
.. _coding-rules.py.namings.methods:

Functions and methods
---------------------

Lowercase, without underscores.

.. note::
    `PEP 8 - Function and variable names <https://peps.python.org/pep-0008/#function-and-variable-names>`_
    apparently makes no difference between function and variable namings.
    This is a `scenario`-specific refinement.

Leading underscore for internal functions and methods:

- non-exported functions (i.e. not supposed to be visible from other modules / packages),
- inner functions (functions defined inside another function / method),
- protected class and instance methods.


.. _coding-rules.py.namings.variables:
.. _coding-rules.py.namings.members:
.. _coding-rules.py.namings.parameters:

Variables, members and parameters
---------------------------------

Lowercase, with underscores.

Leading underscore for internal variables, or protected members:

- non-exported module attributes (i.e. not supposed to be visible from other modules / packages),
- protected class and instance members,
- variables defined inside functions and methods.

On the opposite, the following items may not start with a leading underscore:

- exported module attributes,
- public class and instance members,
- function and method parameters.

Applicable to getters (i.e. properties) and setters.


.. _coding-rules.py.namings.constants:
.. _coding-rules.py.namings.enum-items:

Constants
---------

Capital letters, with underscores.

Leading underscore for internal constants.

Applicable to enum items.

Singletons shall be considered as constants (better for *qa* checkings).
