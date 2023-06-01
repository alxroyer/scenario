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


.. _coding-rules.documentation.admonitions:

Admonitions: notes, warnings...
===============================

The ``.. admonition::`` directive makes it possible to define a title for a "message box" block
(see `<https://docutils.sourceforge.io/docs/ref/rst/directives.html#generic-admonition>`_).
Eg:

.. code-block:: rst

    .. admonition:: Message box title
        :class: tip

        Message box content...

.. admonition:: Message box title
    :class: tip

    Message box content...

The ``:class:`` attribute shall be set with one of the following classes
(see `<https://docutils.sourceforge.io/docs/ref/rst/directives.html#specific-admonitions>`_):

- ``tip`` (do not use ``hint``)
- ``note``
- ``important``
- ``warning`` (do not use ``attention``, ``caution`` nor ``danger``)
- ``error``

When no title is needed, the directive with names corresponding to the selected classes above
may be used.
Eg:

.. code-block:: rst

    .. tip:: Short tip text, without title,
             which may be continued on the next line.

.. tip:: Short tip text, without title,
         which may be continued on the next line.
