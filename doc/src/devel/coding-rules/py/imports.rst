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

This section complies with `PEP8 import recommendations <https://peps.python.org/pep-0008/#imports>`_.


.. _coding-rules.py.imports.groups:
.. _coding-rules.py.imports.order:

Groups and order of imports
---------------------------

We consider the following groups of imports:

- **Module level imports:**

  Module level imports shall be placed at the top level of the module,
  after the module docstring if any.

  Within module level imports, we consider the following groups of imports again:

  - **System imports** :ref:`[sys] <coding-rules.py.imports.sys>`

  - **Project imports:**

    Whithin project imports, we consider:

    - **External core project imports** :ref:`[xcore-proj] <coding-rules.py.imports.xcore>`
      (only for :py:mod:`scenario.test`, :py:mod:`scenario.tools`, test cases and test data)
    - **Implementation project imports** :ref:`[impl-proj] <coding-rules.py.imports.impl>`
    - **Type checking imports** :ref:`[typing-proj] <coding-rules.py.imports.type-checking>`

- **Local imports** :ref:`[local] <coding-rules.py.imports.local>`


.. _coding-rules.py.imports.order.alpha-details:

.. admonition:: Alphabetical order details
    :class: note

    Whithin each import group,
    the following details apply for sorting alphabetically imported modules then symbols when applicable:

    - Dot characters before any other characters.
    - Underscore characters before letters.
    - Case insensitive comparison.
    - After case insensistive comparison, consider lower case letters before their capital equivalent.
    - ``from <modulename> import ...`` forms follow right after the ``import <modulename>`` form for the same module if any.

    .. admonition:: Justification for ordering imports
        :class: note

        Giving an order for imports is a matter of code stability.

        The alphabetical order works in almost any situation (except on vary rare occasion).
        It's simple, and easy to read through.
        That's the reason why it is chosen as the main order for imports.


.. _coding-rules.py.imports.order.module-level-spacing:

.. admonition:: Spacing around module level import groups
    :class: note

    Ensure one blank line between import groups,
    except between :ref:`[impl-proj] <coding-rules.py.imports.impl>` and :ref:`[typing-proj] <coding-rules.py.imports.type-checking>` groups
    which may follow one another without a blank line.

    Ensure two blank lines after all module level imports.


.. _coding-rules.py.imports.sys:

System imports [sys]
--------------------

System imports (or "standard library imports" as named by `PEP8 import recommendations <https://peps.python.org/pep-0008/#imports>`_),
shall come at the module level.

Exceptions for system imports as a :ref:`local imports <coding-rules.py.imports.local>`
should be justified, and probably better located right before there usage in the function or method body.

Use one system import per ``import`` line.

Sort imports in the :ref:`alphabetical order <coding-rules.py.imports.order.alpha-details>` of module names.

Avoid importing symbols from system imports.
Use the ``import ...`` form, then remind the system package name as a prefix in the code,
in order to make it explicit where the symbol comes from.

Example:

.. code-block:: python

    import abc

    class MyClass(abc.ABC):
        @abc.abstractmethod
        def methodname(self):  # type: (...) -> int
            ...


.. _coding-rules.py.imports.impl:

Implementation imports [impl-proj]
----------------------------------

We call implementation imports the project imports required for execution.

.. _coding-rules.py.imports.impl.no-folding:

Avoid folding: ``if True:`` blocks
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As explained in :ref:`coding-rules.py.imports.cyclic-deps`, we want to ensure the fewer implementation imports at the module level.

In order to avoid Python IDEs folding implementation imports,
giving us a chance to visually control and get rid of useless imports,
we choose to set them below a ``if True:`` block.

.. _coding-rules.py.imports.impl.suffix:

``Impl`` suffix
^^^^^^^^^^^^^^^

In order to discriminate :ref:`[impl-proj] <coding-rules.py.imports.impl>` v/s :ref:`[typing-proj] <coding-rules.py.imports.type-checking>` imports
(see explanation for the :ref:`type checking dilemma <coding-rules.py.imports.type-checking.dilemma>` below),
classes imported at the module level for execution shall be suffixed with ``Impl``.

.. admonition:: Memo: leading underscore
    :class: note

    As explained :ref:`after <coding-rules.py.imports.no-reexports>`,
    implementation imports shall also be prefixed with a leading underscore.

.. _coding-rules.py.imports.impl.form:
.. _coding-rules.py.imports.impl.order:

Form and order
^^^^^^^^^^^^^^

Use the relative form ``from .modulename import ...``.

Import one symbol per ``import`` line
(implementation imports may be a bit long otherwise, especially with their :ref:`justification <coding-rules.py.imports.cyclic-deps>`).

Sort imports in the :ref:`alphabetical order <coding-rules.py.imports.order.alpha-details>` of module names first,
then in the :ref:`alphabetical order <coding-rules.py.imports.order.alpha-details>` of imported symbols.


.. _coding-rules.py.imports.type-checking:

Type checking imports [typing-proj]
-----------------------------------

Type checking imports are imports made under a ``if typing.TYPE_CHECKING:`` condition.

See `<https://stackoverflow.com/questions/39740632/python-type-hinting-without-cyclic-imports>`_
for some information on these so-called type checking imports.

.. _coding-rules.py.imports.type-checking.no-folding:
.. _coding-rules.py.imports.type-checking.condition:

``if typing.TYPE_CHECKING:`` condition
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Adding type hints to the Python code often leads to `cyclic dependencies` between modules of a same project.
Type checking imports are an efficient way to avoid such cyclic dependencies.

.. note::
    Such condition prevents Python IDEs from folding these imports by the way,
    which is convenient in order to give us a chance to visually control and get rid of useless imports,
    as we do with ``if True:`` blocks for :ref:`implementation imports <coding-rules.py.imports.impl.no-folding>`.

.. _coding-rules.py.imports.type-checking.suffix:

``Type`` suffix
^^^^^^^^^^^^^^^

Using type checking imports usually leads to writing code that passes type checking, but fails when executed.
Which is what we call the :ref:`type checking dilemma <coding-rules.py.imports.type-checking.dilemma>`.

In order to work around this dilemma,
when importing a class at the global scope,
a type checking import shall rename the imported symbol with the ``Type`` suffix.

.. admonition:: Memo: leading underscore
    :class: tip

    As explained :ref:`after <coding-rules.py.imports.no-reexports>`,
    implementation imports shall also be prefixed with a leading underscore.

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

.. note::
    Imported type symbols should normally don't need to be added the ``Type`` suffix,
    in as much as they should already hold it (see :ref:`type naming rules <coding-rules.py.namings.types>`).

.. code-block:: python

    if typing.TYPE_CHECKING:
        from .path import AnyPathType as _AnyPathType


.. _coding-rules.py.imports.type-checking.dilemma:

.. admonition:: Type checking imports and execution dilemma
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

.. _coding-rules.py.imports.type-checking.form:
.. _coding-rules.py.imports.type-checking.order:

Form and order
^^^^^^^^^^^^^^

Same as :ref:`implementation imports [impl-proj] <coding-rules.py.imports.impl.form>`.


.. _coding-rules.py.imports.xcore:

External core project imports [xcore-proj]
------------------------------------------

Only in :py:mod:`scenario.test`, :py:mod:`scenario.tools`, test cases and test data.
Used to import core :py:mod:`scenario` and related packages.

External core project imports are half the way between:

- :ref:`[sys] <coding-rules.py.imports.sys>` imports on the one hand:

  :py:mod:`scenario` is imported as if it was installed
  as a "related third party import" (as named in `PEP8 <https://peps.python.org/pep-0008/#imports>`_).
- :ref:`[impl-proj] <coding-rules.py.imports.impl>` and :ref:`[typing-proj] <coding-rules.py.imports.type-checking>` imports on the other hand:

  :py:mod:`scenario.test` and :py:mod:`scenario.tools` are still part of the `scenario` project.

Same form and order as :ref:`implementation <coding-rules.py.imports.impl.form>` and :ref:`typing imports <coding-rules.py.imports.type-checking.form>`,
except:

- Use regular imports for publicly exposed symbols:

  .. code-block:: python

      import scenario
      import scenario.test
      import scenario.text
      import scenario.tools

- Use the following pattern (after regular imports as above) to access protected symbols:

  .. code-block:: python

      from scenario._privatemodule import ProtectedSymbol as _ProtectedSymbol  # noqa  ## Access to protected module


.. _coding-rules.py.imports.local:

Local imports [local]
---------------------

Local imports may be done at the beginning of a function or method, after the docstring if any:

No blank line before.
Ensure one blank line after, before the function or method body.

Use the relative form ``from .modulename import ...`` (unless not applicable for some reason).

Sort imports:

1. in the :ref:`alphabetical order <coding-rules.py.imports.order.alpha-details>` of module names first.
2. If symbol(s) from a given module need a ``if typing.TYPE_CHECKING:`` guard,
   this(these) import statement(s) shall still be sorted in the :ref:`alphabetical order <coding-rules.py.imports.order.alpha-details>` of module names,
   after the last implementation import for the same module if any.
3. Eventually, sort imported symbols in the :ref:`alphabetical order <coding-rules.py.imports.order.alpha-details>`:

   - in a single line, if the line is not too long.
   - or repeat the import statement with one line per imported symbol otherwise.


.. _coding-rules.py.imports.no-reexports:

Avoid reexporting symbols imported at the module level
------------------------------------------------------

In order to avoid :ref:`reexporting <coding-rules.py.reexports>` imported symbols,
symbols imported at the module level shall be renamed with a leading underscore.


.. _coding-rules.py.imports.cyclic-deps:

Cyclic dependencies
-------------------

In order to avoid cyclic module dependencies in a package,
the fewer project imports shall be placed at the module level:

- Postpone as much as possible the imports with :ref:`local imports <coding-rules.py.imports.local>` [#local-import-perf-limitation]_.
- Discriminate remaining project imports:
  :ref:`implementation imports [impl-proj] <coding-rules.py.imports.impl>`
  v/s :ref:`type checking imports [typing-proj] <coding-rules.py.imports.type-checking>`.

  :Implementation imports [impl-proj]:
      In order to ensure that remaining implementation imports are legitimate,
      they shall be justified with a comment at the end of the ``import`` line.

      In the end, only a few implementation imports should remain:

      - Classes used for inheritance,
      - Classes used for global instanciations,
      - Functions executed in the module level context,
      - Performance concerns.

  :Typing imports [typing-proj]:
      As for implementation imports, we will not to define more type checking imports than necessary.

      Nevertheless, thanks to the ``if typing.TYPE_CHECKING:`` guard, type checking imports don't cause cyclic dependendies.
      Thus, typing checking imports don't need to be justified as for implementation imports.

The 'tools/check-module-deps.py' script helps visualizing `scenario` module dependencies:

.. code-block:: bash

    $ ./tools/check-module-deps.py

.. literalinclude:: ../../../../data/check-module-deps.log
    :language: none

.. Footnotes.

---

.. [#local-import-perf-limitation] About local imports and performance:

    .. admonition:: Performance limitations due to local imports
        :class: note

        On the one hand, local imports avoid cyclic module dependencies.
        But on the other hand, they may cause performance issues, especially when used in low-level functions called numerous times.
        By the way, our local import strategy may lead to performance limitations.

        That's the reason why a couple of modules have been identified for optimization,
        and are expected to be imported at the module level, not through local imports.

        The :ref:`'tools/check-imports.py script <coding-rules.py.imports.check>` checks this list of optimized modules.

        The list of optimized modules is defined in 'scenario/tools/imports/_optimized.py'.

        .. tip::
            The :class:`scenario._perfutils.PerfImportWrapper` util may be used to determine which modules are imported the most
            during a given code execution.

        .. tip::
            When reintroducing :ref:`implementation imports <coding-rules.py.imports.impl>` for performance concerns,
            if a risk of cyclic dependency come up, use fast-path data (see :attr:`scenario._fastpath.FAST_PATH`).


.. _coding-rules.py.imports.check:

Import checkings
----------------

The 'tools/check-imports.py' script helps checking imports in the whole `scenario` project.

.. tip::
    The ``# check-import: ignore`` pattern may be used to hide an import error reported by the 'tools/check-imports.py'.
    This may be particularly useful for optimized imports in local imports (with additional ``##`` justification).
