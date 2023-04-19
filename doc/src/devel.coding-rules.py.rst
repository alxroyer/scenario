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

Python namings follow `PEP 8 <https://peps.python.org/pep-0008/#descriptive-naming-styles>`_ recommandations.
Let's remind them below:

.. _coding-rules.py.namings.packages:
.. _coding-rules.py.namings.modules:

:Packages and modules:
    Lowercase, without underscores.

    .. note::
        As stated in `PEP 8 - Package and module names <https://peps.python.org/pep-0008/#package-and-module-names>`_
        "the use of underscores is discouraged".

    Leading underscore for internal packages and modules.

    .. note::
        Makes it possible to set :ref:`design a package <coding-rules.py.packages>` with protected modules,
        and explicitely select the symbols exported from them in the '__init__.py' module.

.. _coding-rules.py.namings.classes:
.. _coding-rules.py.namings.exceptions:
.. _coding-rules.py.namings.enum-classes:

:Classes:
    CamelCase, without underscores.

    Leading underscore for internal classes.

    Applicable to exceptions and enum classes.

.. _coding-rules.py.namings.types:

:Types:
    CamelCase, without underscores.

    Leading underscore for internal types.

.. _coding-rules.py.namings.functions:
.. _coding-rules.py.namings.methods:

:Functions and methods:
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

:Variables, members and parameters:
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

:Constants:
    Capital letters, with underscores.

    Leading underscore for internal constants.

    Applicable to enum items.

    Singletons shall be considered as constants (better for *qa* checkings).


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

Even though Python3 automatically defines packages from directories,
every package should contain a dedicated '__init__.py' file in order to explicitize the way the package is defined:

1. If it exports nothing by default,
   but just holds public modules or subpackages (without a leading underscore) to load explicitely,
   this shall be mentioned in the docstring of the package, in the '__init__.py' file.

2. Otherwise, the '__init__.py' file declares the symbols it officially exports:

   - The package shall be implemented with :ref:`private modules <coding-rules.py.namings.modules>` (with a leading underscore).
   - Re-exports should follow the :ref:`re-export rules <coding-rules.py.re-exports>` described just after.

.. admonition:: Packages and subpackages defined from different directories
    :class: tip

    For the memo, ``pkgutil.extend_path()`` helps defining packages and subpackages of the same package at different locations.

    For instance:

    - The base :py:mod:`scenario` package is defined in the main 'src/' directory.
    - :py:mod:`scenario.test` comes as a subpackage of the latter, but is defined in 'test/src/'.
    - Same with :py:mod:`scenario.tools`, defined in 'tools/src/'.

    This avoids mixing test and tools sources with the core :py:mod:`scenario` implementation.


.. _coding-rules.py.re-exports:

Re-exports
----------

'__init__.py' files usually declare the set of public symbols for the package they define,
by re-exporting those symbols from the neighbour modules in the given package.

In order to keep it simple,
as long as the package does not rename exported items (but only modules),
use the explicit re-export pattern (inherited from `PEP 484 - Stub files <https://peps.python.org/pep-0484/#stub-files>`_ specifications):

.. code-block:: python

    # Non-renamed explicit export.
    from ._privatemodule import MyClass as MyClass

.. note::
    Our `mypy` configuration makes use of this syntax
    by disabling `implicit re-exports <https://mypy.readthedocs.io/en/stable/config_file.html#confval-implicit_reexport>`_.

If only attributes must be renamed,
or renamed modules in non-'__init__.py' modules fail,
intermediate private instances may be used:

.. code-block:: python

    # Renamed attribute export.
    from ._privatemodule import original_attr as _private_attr
    exported_attr = _private_attr

    # Renamed module export.
    from . import _privatemodule
    renamedmodule = _privatemodule

.. admonition:: Memo - No renamed attribute exports with a single ``from ... import ... as ...`` statement
    :class: note

    If we declare :py:data:`scenario.logging` as following in 'src/scenario/__init__.py':

    .. code-block:: python

        from ._loggermain import MAIN_LOGGER as logging
        # No `__all__` declaration afterwards.

    mypy fails with '"Module scenario" does not explicitly export attribute "logging"  [attr-defined]' errors.

.. admonition:: Memo - Renamed module exports with a single ``from ... import ... as ...`` statement only in '__init__.py' files
    :class: note

    Same with :py:data:`scenario.tools.data.scenarios`, the following in 'test/src/scenario/test/data.py':

    .. code-block:: python

        from . import _datascenarios as scenarios

    makes mypy fail with '"Module scenario.test._data" does not explicitly export attribute "scenarios"  [attr-defined]' errors.

    But the following works in 'test/src/scenario/test/__init__.py'!

    .. code-block:: python

        from . import _data as data

If exported classes are renamed, use explicit ``__all__`` declarations
(see https://docs.python.org/3/tutorial/modules.html#importing-from-a-package).
For consistency reasons, back every export of such module with an ``__all__`` declaration,
even though non renamed exports don't really need it.

.. code-block:: python

    # `__all__` export declaration.
    __all__ = []

    # Renamed attribute export.
    from ._privatemodule import original_attr as exported_attr
    __all__.append("exported_attr")

    # Renamed module export.
    from . import _originalmodule as exportedmodule
    __all__.append("exportedmodule")

    # Renamed class export.
    from ._privatemodule import OriginalClass as ExportedClass
    __all__.append("ExportedClass")

.. admonition:: Memo - No renamed class exports with alias instanciations
    :class: note

    Renamed class exports don't work well with every type checker or IDE when exported through alias instanciations.

    For instance, if we declare :py:class:`scenario.Scenario` as following:

    .. code-block:: python

        from ._scenariodefinition import ScenarioDefinition as ScenarioDefinition
        Scenario = ScenarioDefinition

    mypy succeeds, but IDEs get confused.


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
