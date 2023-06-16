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


.. _coding-rules.documentation.property-return-type:

Property return type hint
=========================

`sphinx.ext.autodoc` does not make use of property return type hints in the output documentation.

Nevertheless, we do not make use of the ``:type:`` directive,
which would be redundant with the return type hint already set.
The `sphinx#7837 <https://github.com/sphinx-doc/sphinx/issues/7837>`_ enhancement request
has been opened for that purpose.
