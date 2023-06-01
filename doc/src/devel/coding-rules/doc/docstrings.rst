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


.. _coding-rules.documentation.docstrings:

Docstrings
==========

Python docstrings follow the *ReStructured Text* format.


.. _coding-rules.documentation.docstrings.classes:

Classes
-------

Use a leading doctring, at the beginning of the class definition.


.. _coding-rules.documentation.docstrings.functions:
.. _coding-rules.documentation.docstrings.methods:

Functions and methods
---------------------

.. admonition:: PyCharm configuration
    :class: tip

    In order to make PyCharm use the *ReStructured Text* format for docstrings, go through:
    "File" > "Settings" > "Tools" > "Python Integrated Tools" > "Docstrings" > "Docstring format"
    (as of PyCharm 2021.1.1)

    Select the "reStructured Text" option.

The 'Initializer' word in ``__init__()`` docstrings should be avoided.
``__init__()`` docstrings should be more specific on what the initializers do for the object.

Sphinx accepts a couple of keywords for a same meaning
(see `stackoverflow.com#34160968 <https://stackoverflow.com/questions/34160968/python-docstring-raise-vs-raises#34212785>`_
and `github.com <https://github.com/JetBrains/intellij-community/blob/210e0ed138627926e10094bb9c76026319cec178/python/src/com/jetbrains/python/documentation/docstrings/TagBasedDocString.java>`_).
Let's choose a couple of them:

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


.. _coding-rules.documentation.docstrings.attributes:
.. _coding-rules.documentation.docstrings.types:

Attributes & types
------------------

Types and attributes shall be documented with ``#:`` Sphinx comments.

.. code-block:: python

    #: Docstring.
    ATTR = ...  # type: ...

.. note::

    Types and attributes could be documented with docstrings following them.

    .. code-block:: python

        ATTR = ...  # type: ...
        """
        Docstring placed after.
        """

    But we consider this is less readable than using ``#:`` sphinx comments.
