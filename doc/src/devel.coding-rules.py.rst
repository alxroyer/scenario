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


.. _coding-rules.py:

Python coding
=============

.. _coding-rules.py.strings:

Strings
-------

.. todo:: Documentation needed for string coding rules:

    - Differenciate strings and byte-strings:
        - Use of ``""`` / ``r""`` / ``f""`` (double quote) to enclose ``str`` strings
            - Except for strings in f-string {}-blocks.
        - Use of ``b''`` / ``rb''`` (simple quotes) to enclose ``bytes`` strings
    - Use f-strings
        - Except for debugging (for optimization concerns)
        - Except for assertion errors and evidence (for optimization concerns)
        - Except for regex (because of '{}' escaping)
        - Except for bytes (f-strings not available)
    - Use *repr* specification (``f"{...!r}"`` / ``"%r"``) instead of calling ``repr()`` (for optimization concerns)


.. _coding-rules.py.namings:

Namings
-------

.. todo:: Documentation needed for namings:

    - PEP8 compatible
    - Packages
    - Modules
    - Classes
    - Attributes
    - Methods & functions
    - Getters (properties) and setters, same as attributes
    - Constants


.. _coding-rules.py.presentation:

Presentation
------------

.. todo:: Documentation needed for code presentation

    - Indentation:

      - Avoid right-aligned comments (hard to maintain when the names change)
      - Functions and methods (same purpose):

        - New line for the first parameter
        - Parameters indented with 2 tabs (as proposed by PyCharm by default).
          Makes it more readable by differenciating the parameters from the function / body.

    - Trailing commas (refer to PEP8 `<https://www.python.org/dev/peps/pep-0008/#when-to-use-trailing-commas>`_)
    - New line after the opening parenthesis of the function declarations


.. _coding-rules.py.packages:

Packages
--------

.. todo:: Documentation needed for packages, file names:

    - :py:mod:`scenario` package
    - '__init__.py' that exports symbols from the given package

.. note::

    :py:mod:`scenario.test`, :py:mod:`scenario.tools` subpackages are implemented at different locations,
    out of the main 'src/' directory.


.. _coding-rules.py.static:

Static & class methods
----------------------

Do not use the ``@staticmethod`` or ``@classmethod`` whenever a method could be converted so.
It is preferrable to rely on the meaning at first, in order to make the code more stable along the time.

By default, PyCharm "detects any methods which may safely be made static".
This coding rule goes against these suggestions.
By the way, we do not want to set ``# noinspection PyMethodMayBeStatic`` pragmas everywhere a method could "be made static" in the code.
Thus, please disable the "Method may be static" inspection rule in your PyCharm settings.


.. _coding-rules.py.typings:

Typings
-------

.. note::
    Memo: The `mypy website <https://www.mypy-lang.org/>`_ points to `PEP 484 <https://www.python.org/dev/peps/pep-0484/>`_
    as the reference for type annotations.

The code uses `Python 2 type hints <https://peps.python.org/pep-0484/#suggested-syntax-for-python-2-7-and-straddling-code>`_,
based on `type comments <https://peps.python.org/pep-0484/#type-comments>`_.

Even though Python 2 compatibility is not expected,
it has proved that comment type hints did not suffer a couple of limitations compared with Python 3 type hints:

- impossible for a method to return an instance of the current class,
  without a prior ``import __future__ import annotations`` statement,
  which is available from Python 3.8 only
  (see `PEP 484 - The problem of forward declarations <https://peps.python.org/pep-0484/#the-problem-of-forward-declarations>`_),

  .. code-block:: python

      # Python 3 type hints

      from __future__ import annotations  # << Python 3.8 only

      class A:
          def meth() -> A:  # << NameError: name 'A' is not defined, if `__future__.annotations` not imported
              return A()

  .. code-block:: python

      # Python 2 type hints

      class A:
          def meth():  # type: (...) -> A
              return A()

- impossible to define the type of the iterating variable in a ``for`` loop statement
  (see `PEP 484 - Type comments <https://peps.python.org/pep-0484/#type-comments>`_),

  .. code-block:: python

      # (Bad) python 3 type hints

      for _i: int in range(10):  # << SyntaxError: invalid syntax
          pass

  .. code-block:: python

      # Python 2 type hints

      for _i in range(10):  # type: int
          pass

- impossible to define the type of a couple of variables initialized from a function returning a tuple
  (see `PEP 484 - Type comments <https://peps.python.org/pep-0484/#type-comments>`_ as well).

  .. code-block:: python

      # (Bad) python 3 type hints

      _a: int, _b: str = func()  # << SyntaxError: invalid syntax

  .. code-block:: python

      # Python 2 type hints

      _a, _b = func()  # type: int, str

For function and method type hints,
we use a multi-line style with the ``(...)`` ellipsis pattern for return types
(see `PEP 484 - Suggested syntax for Python 2.7 and straddling code <https://peps.python.org/pep-0484/#suggested-syntax-for-python-2-7-and-straddling-code>`_).
It makes the code diffs shorter, and the maintainance simpler by the way.

Exceptions for getters, setters and well known special functions when presented on a single line.

.. code-block:: python

    class MyClass:

        def __init__(self):  # type: (...) -> None
            """
            We may extend the constructor parameters in the future
            => use an ellipsis, even though the method is currently presented on a single line.
            """
            self.__a = 0  # type: int

        def __str__(self):  # type: () -> str
            """
            The :meth:`__str__()` special function is not subject to changes with its parameters
            => no ellipsis.
            """
            return ""

        @property
        def a(self):  # type: () -> int
            """
            No parameter for a getter
            => no ellipsis.
            """
            return self.__a

        @a.setter
        def a(self, value):  # type: (int) -> None
            """
            Single parameter for a setter
            => single line, no ellipsis.
            """
            self.__a = value

        def method1(
            self,
            p1,  # type: int
            p2,  # type: str
            p3=None,  # type: typing.Optional[bool]
        ):  # type: (...) -> None
            """
            The list of parameters may evolve in the general case
            => prefer multi-line presentation, use an ellipsis in any case.
            """


.. _coding-rules.py.imports:

Imports
-------

.. _coding-rules.py.imports.order:

Order of Imports
^^^^^^^^^^^^^^^^

1. Place system imports at first:

  - One system import per ``import`` line.
  - Sort imports in the alphabetical order.

2. Then project imports (i.e. `scenario` imports):

  - Use the relative form ``from .modulename import ClassName``.
  - Sort project imports in the alphabetical order of module names.
  - For a given module import statement, sort the symbols imported
    in their alphabetical order as well:

    - in a single line if the import line is not too long,
    - or repeat the module import with one line per imported symbol otherwise.

3. Then test imports (for test modules only).

.. admonition:: Justification for ordering imports
    :class: note

    Giving an order for imports is a matter of code stability.

    The alphabetical order works in almost any situation (except on vary rare occasion).
    It's simple, and easy to read through.
    That's the reason why it is chosen as the main order for imports.


.. _coding-rules.py.imports.fewer-top:

The fewer project imports at the top level
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

The 'tools/checkdeps.py' script helps visualizing `scenario` module dependencies:

.. code-block:: bash

    $ ./tools/checkdeps.py

.. literalinclude:: ../data/checkdeps.log
    :language: none


.. _coding-rules.py.imports.TYPE_CHECKING:

``TYPE_CHECKING`` imports
^^^^^^^^^^^^^^^^^^^^^^^^^

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

    Let the ``a.py`` module define a super class :py:class:`A`
    with a :py:meth:`getb()` method returning a :py:class:`B` instance or ``None``:

    .. code-block:: python

        if typing.TYPE_CHECKING:
            from .b import B

        class A:
            def getb(self, name):  # type: (str) -> typing.Optional[B]
                for _item in self.items:
                    if isinstance(_item, B):
                        return _item
                return None

    Let the ``b.py`` module define :py:class:`B`, a subclass of :py:class:`A`:

    .. code-block:: python

        from .a import A

        class B(A):
            def __init__(self):
                A.__init__(self)

    The :py:class:`B` class depends on the :py:class:`A` class for type hints *and* execution.
    So the ``from .a import A`` import statement must be set at the top of the ``b.py`` module.

    The :py:class:`A` class needs the :py:class:`B` class
    for the signature of its :py:meth:`A.getb()` method only.
    Thus, the ``from .b import B`` import statement is set at the top of the ``a.py`` module,
    but under a ``if typing.TYPE_CHECKING:`` condition.

    This makes type checking pass, but fails when the :py:meth:`A.getb()` method is executed.
    Indeed, in ``a.py``, as the :py:class:`B` class is imported for type checking only,
    the class is not defined when the ``isinstance()`` call is made.
    By the way, the import statement must be repeated as a local import
    when the :py:class:`B` class is actually used in the :py:meth:`A.getb()` method:

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


.. _coding-rules.py.compat:

Python compatibility
--------------------

The code supports Python versions from 3.6.

The 'tools/checktypes.py' scripts checks code amongst Python 3.6.

.. admonition:: Python versions
    :class: note

    No need to handle Python 2 anymore, as long as its end-of-line was set on 2020-01-01
    (see `PEP 373 <https://www.python.org/dev/peps/pep-0373/>`_).

    As of 2021/09, Python 3.6's end-of-life has not been declared yet (see `<https://devguide.python.org/devcycle/#end-of-life-branches>`_),
    while Python 3.5's end-of-life was set on 2020-09-30 (see `PEP 478 <https://www.python.org/dev/peps/pep-0478/>`_).
