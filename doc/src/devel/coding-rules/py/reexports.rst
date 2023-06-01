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


.. _coding-rules.py.reexports:

Reexports
=========

'__init__.py' files usually declare the set of public symbols for the package they define,
by reexporting those symbols from the neighbour modules in the given package.

In order to keep it simple,
as long as the package does not rename exported items (but only modules),
use the explicit reexport pattern (inherited from `PEP 484 - Stub files <https://peps.python.org/pep-0484/#stub-files>`_ specifications):

.. code-block:: python

    # Non-renamed explicit export.
    from ._privatemodule import MyClass as MyClass

.. note::
    Our `mypy` configuration makes use of this syntax
    by disabling `implicit reexports <https://mypy.readthedocs.io/en/stable/config_file.html#confval-implicit_reexport>`_.

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
