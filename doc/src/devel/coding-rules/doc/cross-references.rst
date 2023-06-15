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


.. _coding-rules.documentation.cross-references:

Cross references
================

Use relative imports as much as possible to reference symbols out of the current module.

In as much as `Sphinx` does not provide a directive to cross-reference function and method parameters,
use double backquotes to highlight them.

.. admonition:: Cross referencing parameters
    :class: note

    There is no current cross reference directive for function and method parameters
    (see `sphinx#538 <https://github.com/sphinx-doc/sphinx/issues/538>`_).

    From the `documentation of the python domain <https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html#cross-referencing-python-objects>`_,
    the best existing directive would be ``:obj:`` but it is not really clear
    (``:attr:`` is for data attributes of objects).
    Let's reserve ``:data:`` for module attributes.

    Other useful resources on that topic:

    - `<https://stackoverflow.com/questions/11168178/how-do-i-reference-a-documented-python-function-parameter-using-sphinx-markup>`_
    - `<https://pypi.org/project/sphinx-paramlinks/>`_

Sphinx does not provide a dedicated directive to cross-reference types, ``:class:`` does not work neither.
Use the default ``:obj:`` directive instead (see https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html#role-py-obj).
