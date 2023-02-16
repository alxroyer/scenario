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


.. _subscenarios:

Subscenarios: reuse existing scenarios in other scenarios
=========================================================

Scenarios can be reused as subscenarios in other ones.

Executing existing scenarios as sub-scenarios are particularly useful
for the following purposes:

- define alternative scenarios (error scenarios) from a nominal one,
- reuse a nominal scenario as the initial condition of other ones,
  in order to bring the system or software under test in the expected initial state,
- repeat a base scenario with varying input data.


.. _subscenarios.initial-conditions:

Initial conditions
------------------

.. todo:: Documentation needed for initial conditions.


.. _subscenarios.varying-input-data:

Varying input data
------------------

.. todo:: Improve subscenario documentation with a better example.


In order to illustrate this use case of subscenarios,
let's get back to the previous ``CommutativeAddition`` scenario
defined :ref:`previously <quickstart.first-scenario>`.

The ``CommutativeAddition`` scenario can be called multiple times, with different inputs,
in a super ``CommutativeAdditions`` scenario:

.. literalinclude:: ../../demo/commutativeadditions.py
    :language: python
    :linenos:

To do so, start with loading your base scenario with a regular ``import`` statement:

.. literalinclude:: ../../demo/commutativeadditions.py
    :language: python
    :lines: 8

Instanciate it with the appropriate values:

.. literalinclude:: ../../demo/commutativeadditions.py
    :language: python
    :lines: 20

And execute it as a subscenario:

.. literalinclude:: ../../demo/commutativeadditions.py
    :language: python
    :lines: 21

Executing this super scenario produces the following output:

.. code-block:: bash

    $ ./bin/run-test.py ./demo/commutativeadditions.py

.. literalinclude:: ../data/commutativeadditions.log
    :language: none

Each subscenario execution appears indented with a pipe character.

.. admonition:: Subscenario nestings
    :class: note

    A subscenario may call other subscenarios.

    For each subscenario in the execution stack,
    a pipe indentation is inserted in the log lines,
    in order to highlight the scenario and subscenario execution nestings.
