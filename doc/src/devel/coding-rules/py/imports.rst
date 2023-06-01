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


.. _coding-rules.py.imports:

Imports
=======

.. _coding-rules.py.imports.order:

Order of Imports
----------------

1. Place system imports at first:

  - One system import per ``import`` line.
  - Sort imports in the alphabetical order.

2. Then project imports:

  - Use the relative form ``from .modulename import ClassName``
    (except for test cases and test data).
  - Sort imports in the alphabetical order of module names.
  - For a given module import statement, sort the symbols imported
    in their alphabetical order as well:

    - in a single line if the import line is not too long,
    - or repeat the module import with one line per imported symbol otherwise.

For :py:mod:`scenario.test`, :py:mod:`scenario.tools`, test cases and test data,
an intermediate import section is used for :py:mod:`scenario` and related packages.

Within a given import section,
place the :ref:`TYPE_CHECKING block <coding-rules.py.imports.TYPE_CHECKING>` after imports required for execution.

.. admonition:: Justification for ordering imports
    :class: note

    Giving an order for imports is a matter of code stability.

    The alphabetical order works in almost any situation (except on vary rare occasion).
    It's simple, and easy to read through.
    That's the reason why it is chosen as the main order for imports.


.. _coding-rules.py.imports.fewer-top:

The fewer project imports at the top level
------------------------------------------

In order to avoid cyclic module dependencies in a package,
the fewer project imports shall be placed at the top level of modules:

- Postpone as much as possible the imports with local imports
  in function or methods where the symbol is actually used.
- Whenever possible, use :ref:`TYPE_CHECKING imports <coding-rules.py.imports.TYPE_CHECKING>`
  for type hints.

In order to ensure that remaining top level project imports are legitimate,
they shall be justified with a comment at the end of the ``import`` line
(:ref:`TYPE_CHECKING imports <coding-rules.py.imports.TYPE_CHECKING>` imports don't need to be justified).

In the end, only a few top level project imports should remain:

- Classes used for inheritance,
- Classes used for global instanciations,
- (and that's probably all...)

The 'tools/check-module-deps.py' script helps visualizing `scenario` module dependencies:

.. code-block:: bash

    $ ./tools/check-module-deps.py

.. literalinclude:: ../../../../data/check-module-deps.log
    :language: none


.. _coding-rules.py.imports.TYPE_CHECKING:

``TYPE_CHECKING`` imports
-------------------------

See `<https://stackoverflow.com/questions/39740632/python-type-hinting-without-cyclic-imports>`_
for some information on these so-called ``TYPE_CHECKINGS`` imports.

Adding type hints to the Python code often leads to `cyclic dependencies` between modules of a same project.

``TYPE_CHECKING`` imports are an efficient way to avoid such cyclic dependencies.
But doing so also usually leads to writing code that passes type checking, but fails when executed.
Which is what we call the `type checking dilemma`.

.. admonition:: ``TYPE_CHECKING:`` imports and the type checking dilemma
    :class: note

    Sometimes, a class ``A`` requires another class ``B``
    (in one of its method signatures, or possibly because it inherits from ``B``),
    and so does the other class ``B`` with class ``A`` as well.

    From the execution point of view, this situation can usually be handled with local imports
    in some of the methods involved.

    Still, from the type hint point of view, a cyclic dependency remains between the two modules.
    The ``TYPE_CHECKING`` condition makes it possible to handle such cyclic dependencies.

    But caution! the use of this pattern generates a risk on the execution side.
    Making an import under an ``if typing.TYPE_CHECKING:`` condition at the top of a module
    makes the type checking pass.
    Nevertheless, the same import should not be forgotten in the method(s)
    where the cyclic dependency is actually used,
    otherwise it fails when executed,
    which is somewhat counterproductive regarding the type checking goals!

    Let's illustrate that point with an example.

    Let the ``a.py`` module define a super class ``A``
    with a ``getb()`` method returning a ``B`` instance or ``None``:

    .. code-block:: python

        if typing.TYPE_CHECKING:
            from .b import B

        class A:
            def getb(self, name):  # type: (str) -> typing.Optional[B]
                for _item in self.items:
                    if isinstance(_item, B):
                        return _item
                return None

    Let the ``b.py`` module define ``B``, a subclass of ``A``:

    .. code-block:: python

        from .a import A

        class B(A):
            def __init__(self):
                A.__init__(self)

    The ``B`` class depends on the ``A`` class for type hints *and* execution.
    So the ``from .a import A`` import statement must be set at the top of the ``b.py`` module.

    The ``A`` class needs the ``B`` class
    for the signature of its ``A.getb()`` method only.
    Thus, the ``from .b import B`` import statement is set at the top of the ``a.py`` module,
    but under a ``if typing.TYPE_CHECKING:`` condition.

    This makes type checking pass, but fails when the ``A.getb()`` method is executed.
    Indeed, in ``a.py``, as the ``B`` class is imported for type checking only,
    the class is not defined when the ``isinstance()`` call is made.
    By the way, the import statement must be repeated as a local import
    when the ``B`` class is actually used in the ``A.getb()`` method:

    .. code-block:: python

        class A:
            def getb(self, name):  # type: (str) -> typing.Optional[B]
                # Do not forget the local import!
                from .b import B

                for _item in self.items:
                    if isinstance(_item, B):
                        return _item
                return None

In order to work around this dilemma,
when importing an executable symbol at the global scope,
a ``TYPE_CHECKING`` import shall rename the imported symbol with the ``Type`` suffix
(plus the ``_`` prefix in order to limit the scope of this renamed symbol to the current module only).

.. code-block:: python

    if typing.TYPE_CHECKING:
        # `TYPE_CHECKING` import made for type checking only.
        # Required for the type hint of the `newneighbour()` function below in this example.
        from .neighbour import Neighbour as _NeighbourType

    # Type hint: `Neighbour` symbol required for type checking. Use the renamed version.
    def newneighbour():  # type: (...) -> _NeighbourType
        # If we forget this local import, type checkers will point an error on the instanciation line below.
        from .neighbour import Neighbour

        # Instanction: `Neighbour` symbol required for execution.
        _neighbour = Neighbour()  # type: Neighbour
        return _neighbour

Doins so, a difference is made between symbols imported for type checking, and symbols required for execution.
By the way, type checkers won't miss lacking imports required for execution.

Imported type-only symbols don't need to be renamed
(they usually already end with the ``Type`` suffix).

.. code-block:: python

    if typing.TYPE_CHECKING:
        from .path import AnyPathType
