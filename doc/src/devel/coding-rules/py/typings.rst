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


.. _coding-rules.py.typings:

Typings
=======

.. note::
    Memo: The `mypy website <https://www.mypy-lang.org/>`_ points to `PEP 484 <https://www.python.org/dev/peps/pep-0484/>`_
    as the reference for type annotations.

The code uses `Python 2 type hints <https://peps.python.org/pep-0484/#suggested-syntax-for-python-2-7-and-straddling-code>`_,
based on `type comments <https://peps.python.org/pep-0484/#type-comments>`_.

Even though Python 2 compatibility is not expected (see :ref:`coding-rules.py.compatibility`),
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
