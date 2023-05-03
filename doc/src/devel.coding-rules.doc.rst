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

.. _coding-rules.documentation.admonitions:

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


.. _coding-rules.documentation.indentation:

ReStructured Text indentation
-----------------------------

ReStructured Text directives could lead to use indentations of 3 spaces.

Considering that this is hard to maintain with regular configurations of editors,
4 space indentations shall be preferred in docstrings and `.rst` files.

Exception for unordered and numbered lists that require the sub-content to be aligned with the bullet or item number.


.. _coding-rules.documentation.domains:

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


.. _coding-rules.documentation.docstrings:

Docstrings
----------

Python docstrings follow the *ReStructured Text* format.


.. _coding-rules.documentation.docstrings.classes:

Classes
^^^^^^^

Use a leading doctring, at the beginning of the class definition.


.. _coding-rules.documentation.docstrings.functions:
.. _coding-rules.documentation.docstrings.methods:

Functions and methods
^^^^^^^^^^^^^^^^^^^^^

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
^^^^^^^^^^^^^^^^^^

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


.. _coding-rules.documentation.cross-references:

Cross references
----------------

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


.. _coding-rules.documentation.property-return-type:

Property return type hint
-------------------------

`sphinx.ext.autodoc` does not make use of property return type hints in the output documentation.

Nevertheless, we do not make use of the ``:type:`` directive,
which would be redundant with the return type hint already set.
The `sphinx#7837 <https://github.com/sphinx-doc/sphinx/issues/7837>`_ enhancement request
has been opened for that purpose.


.. _coding-rules.documentation.reexports:

Re-exports
----------

Documenting a '__init__.py' file that exports symbols from neighbour modules is a pain with `autodoc`.

This section does not really describe a rule, but rather tracks the history of our observations on that topic:

- We first considered documenting exported symbols as regular module attributes:

  - Imported members, i.e. exported members are not documented by default.

  - According to `sphinx#4372 <https://github.com/sphinx-doc/sphinx/issues/4372>`_,
    we should have added the `:imported-members:` option in the 'doc/src/py/scenario.rst' output file:

    .. code-block:: rst

        .. automodule:: scenario
           :members:
           :imported-members:
           :undoc-members:
           :show-inheritance:

  - Instead of that, since the 'doc/src/py/scenario.rst' was automatically generated by `sphinx-apidoc`,
    we eventually decided to manually document the exported symbols in 'src/scenario/__init__.py'
    by extending ``__doc__`` with explicit ReStructuredText ``.. py:attribute::`` directives "as aliases to the inner items",
    "which [let] us define documentation sections by the way".

  - However, since this caused "duplicate object description" errors,
    we hid those in `sphinx-build` output with 'mkdoc.py'.

- Then, with `enhancement #77 <https://github.com/alxroyer/scenario/issues/77>`_),
  we added ``__all__`` export declarations for typing considerations in 'src/scenario/__init__.py'
  (see :ref:`re-exports coding rules <coding-rules.py.re-exports>`).

  - As soon as a ``__all__`` list is declared, things change a bit with Sphinx:

    - For each exported symbol declared in ``__all__``,
      Sphinx automatically repeats the documentation defined in the privte module
      at the end of the output documentation page for the module (our :py:mod:`scenario` package).

    - Since we generate the documentation for private modules in separate pages,
      this additional documentation eventually comes to be a duplication of the one defined in private modules.

      .. note::
          Actually, it seems we can't get rid of generating the documentation for private modules,
          otherwise the output documentation has lots of missing references.

    - This additional documentation comes unordered, compared with the grouping in sections we had done before.

    - Moreover, Sphinx sets non-desired "alias of" lines in the output documentation for renamed class exports
      (see https://stackoverflow.com/questions/38765577/overriding-sphinx-autodoc-alias-of-for-import-of-private-class
      for a Q&A on how to get rid of these "alias of" in the output documentation).

    - Errors come up also:

      - a couple of "Inline emphasis start-string without end-string",
      - lots of "WARNING: more than one target found for cross-reference" errors,
        eg: "'KnownIssue': scenario.KnownIssue, scenario._knownissues.KnownIssue".

  - In order to solve these issues, we adopted the following strategy for 'src/scenario/__init__.py':

    - Deactivation of module member documentation:
      ``:(xxx-)member:`` `autodoc` options removed in 'doc/src/py/scenario.rst' after `sphinx-apidoc` execution.

    - Short introductions only (instead of ``.. py:attribute::`` documentations) for exported symbols,
      with cross-references to private module documentations.

  - When we activated warnings, we figured out that we had a number of missing references for `scenario.Scenario`, `scenario.logging`...

    - Module member documentation being still deactivated,
      we eventually set back ``.. py:attribute::`` documentations for exported symbols in the module docstring of 'src/scenario/__init__.py'.
