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


.. _assertions:

Assertions
==========

The :py:mod:`scenario` framework comes with a rich set of assertion methods, dealing with:

- Equalities, inequalities and comparisons,
- ``None`` values, object references and types,
- Strings and regular expressions,
- Sets of values (lists or tuples),
- Times v/s step executions,
- JSON data,
- Files and directories.

For the full list of assertion methods,
please refer to the detailed documentation of the :py:class:`scenario.assertions.Assertions` class
which defines them.

It constitutes a base class for common classes like
:py:class:`scenario.scenariodefinition.ScenarioDefinition` and :py:class:`scenario.stepdefinition.StepDefinition`.

All assertion methods generally have the following parameters:

.. _assertions.err-param:

``err``
    The ``err`` message is the same as the optional message of ``unittest`` assertion methods.

    It gives the opportunity to explicitize the error message when the assertion fails.

.. _assertions.evidence-param:

``evidence``
    The ``evidence`` parameter may be either a boolean or a string value.

    When this parameter is set with a ``True``-like value,
    :ref:`evidence <evidence>` is automatically stored with the data used for the assertion when it succeeds:

    - Set it to ``True`` to use the default evidence message only.
    - Set it with a string to specialize the evidence message.

.. admonition:: ``unittest`` assertions
    :class: note

    The :py:mod:`scenario` assertions take great inspiration from the well known ``unitest`` module.

    All ``unittest`` assertions methods may not have their equivalent in the :py:class:`scenario.assertions.Assertions` class.

    In case you need one of these, the :py:attr:`scenario.assertionhelpers.unittest` object makes it available.
