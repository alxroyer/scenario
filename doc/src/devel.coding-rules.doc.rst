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


.. _coding-rules.documentation:

Documentation
=============

Docstrings
----------

Python docstrings follow the *ReStructured Text* format.

.. admonition:: PyCharm configuration
    :class: tip

    In order to make PyCharm use the *ReStructured Text* format for docstrings, go through:
    "File" > "Settings" > "Tools" > "Python Integrated Tools" > "Docstrings" > "Docstring format"
    (as of PyCharm 2021.1.1)

    Select the "reStructured Text" option.

The 'Initializer' word in :py:meth:`__init__()` docstrings should be avoided.
:py:meth:`__init__()` docstrings should be more specific on what the initializers do for the object.

Sphinx accepts a couple of keywords for a same meaning
(see `stackoverflow.com#34160968 <https://stackoverflow.com/questions/34160968/python-docstring-raise-vs-raises#34212785>`_
and `github.com <https://github.com/JetBrains/intellij-community/blob/210e0ed138627926e10094bb9c76026319cec178/python/src/com/jetbrains/python/documentation/docstrings/TagBasedDocString.java>`_).
Let's choose of them:

.. list-table:: Preferred ReStructured Text tags
    :widths: auto
    :header-rows: 1
    :stub-columns: 0

    * - Preferred tag
      - Unused tags
      - Justification
    * - ``:return:``
      - ``:returns:``
      - ``:return:`` is the default tag used by PyCharm when generating a docstring pattern.
    * - ``:raise:``
      - ``:raises:``
      - Consistency with ``:return:``.

The ``:raise:`` syntax is the following:

.. code-block:: python

    """
    :raise: Unspecified exception type.
    :raise ValueError: System exception.
    :raise .neighbourmodule.MyException: Project defined exception.
    """

The exception type can be specified:

- It must be set before the second colon (Sphinx handles it a makes an dedicated presentation for it).
- It can be either a system exception type, or a project exception defined in the current or a neighbour module
  (same syntax as within a ``:class:`MyException``` syntax).


Admonitions: notes, warnings...
-------------------------------

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


ReStructured Text indentation
-----------------------------

ReStructured Text directives could lead to use indentations of 3 spaces.

Considering that this is hard to maintain with regular configurations of editors,
4 space indentations shall be preferred in docstrings and `.rst` files.


Domains
-------

.. admonition:: Default domain
    :class: note

    Unless the ``.. default-domain::`` directive is used,
    the `Python domain <https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html#the-python-domain>`_
    is the `default domain <https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html#basic-markup>`_.

We do not use the ``:py`` domain specification in the Python docstrings, in as much as it is implicit.

However, we use the ``:py`` domain specification in `.rst` files in order to be explicit for `cross referencing python objects
<https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html#cross-referencing-python-objects>`_.


Cross references
----------------

Use relative imports as much as possible to reference symbols out of the current module.

In as much as `Sphinx` does not provide a directive to cross-reference them,
use double backquotes to highlight function and method parameters.

.. admonition:: Cross referencing parameters
    :class: note

    There is no current cross reference directive for function and method parameters
    (see `sphinx#538 <https://github.com/sphinx-doc/sphinx/issues/538>`_).

    From the `documentation of the python domain <https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html#cross-referencing-python-objects>`_,
    the best existing directive would be ``:obj:`` but it is not really clear
    (``:attr:`` is for data attributes of objects).

    Other useful resources on that topic:

    - `<https://stackoverflow.com/questions/11168178/how-do-i-reference-a-documented-python-function-parameter-using-sphinx-markup>`_
    - `<https://pypi.org/project/sphinx-paramlinks/>`_


Module attributes
-----------------

Module attributes should be documented using the ``.. py:attribute::`` pragma,
extending the ``__doc__`` variable.

.. code-block:: python

    __doc__ += """
    .. py:attribute:: MY_CONST

        Attribute description.
    """
    MY_CONST = 0  # type: int

Otherwise, they may not be cross-referenced from other modules.


Property return type hint
-------------------------

`sphinx.ext.autodoc` does not make use of property return type hints in the output documentation.

Nevertheless, we do not make use of the ``:type:`` directive,
which would be redundant with the return type hint already set.
The `sphinx#7837 <https://github.com/sphinx-doc/sphinx/issues/7837>`_ enhancement request
has been opened for that purpose.
