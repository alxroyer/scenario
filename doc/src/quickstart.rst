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


.. _quickstart:

Quick start
===========

.. _quickstart.first-scenario:

Create your first test scenario
-------------------------------

The example below shows how to describe a test scenario with step methods.

.. literalinclude:: ../../demo/commutativeaddition.py
    :language: python
    :linenos:

Start with importing the :py:mod:`scenario` module:

.. literalinclude:: ../../demo/commutativeaddition.py
    :language: python
    :start-at: # -*- coding: utf-8 -*-
    :end-at: import scenario

Within your module, declare a class that extends the base :py:class:`scenario.Scenario` class,
with optional information: short title and more detailed description:

.. literalinclude:: ../../demo/commutativeaddition.py
    :language: python
    :start-at: class CommutativeAddition
    :end-before: self.a = a

The initializer may also save member variables,
which condition the way the scenario works:

.. literalinclude:: ../../demo/commutativeaddition.py
    :language: python
    :start-at: self.a = a
    :end-at: self.result2 = 0

In this simple example, steps are defined with step methods, starting with the ``step`` pattern:

.. literalinclude:: ../../demo/commutativeaddition.py
    :language: python
    :start-at: def step000
    :lines: 1
    :dedent:

.. literalinclude:: ../../demo/commutativeaddition.py
    :language: python
    :start-at: def step010
    :lines: 1
    :dedent:

.. literalinclude:: ../../demo/commutativeaddition.py
    :language: python
    :start-at: def step020
    :lines: 1
    :dedent:

.. literalinclude:: ../../demo/commutativeaddition.py
    :language: python
    :start-at: def step030
    :lines: 1
    :dedent:

The steps are executed in their alphabetical order.
That's the reason why step methods usually hold a number after the ``step`` keyword.

Give the step descriptions at the beginning of each step method
by calling the :py:meth:`scenario._stepuserapi.StepUserApi.STEP()` method:

.. literalinclude:: ../../demo/commutativeaddition.py
    :language: python
    :start-at: self.STEP("Initial conditions")
    :lines: 1
    :dedent:

Define actions by calling the :py:meth:`scenario._stepuserapi.StepUserApi.ACTION()` method:

.. literalinclude:: ../../demo/commutativeaddition.py
    :language: python
    :start-at: self.ACTION(f"Let a =
    :lines: 1
    :dedent:

Define expected results by calling the :py:meth:`scenario._stepuserapi.StepUserApi.RESULT()` method:

.. literalinclude:: ../../demo/commutativeaddition.py
    :language: python
    :start-at: self.RESULT("result1 and result2 are the same.")
    :lines: 1
    :dedent:

Actions and expected results shall be used as the condition of an ``if`` statement.
The related test script should be placed below these ``if`` statements:

.. literalinclude:: ../../demo/commutativeaddition.py
    :language: python
    :start-at: self.ACTION("Compute (a + b)
    :end-at: self.result1 = self.a + self.b
    :dedent:

This makes it possible for the `scenario` library to call the step methods for different purposes:

1. to peak all the action and expected result descriptions, without executing the test script:
    in that case, the :py:meth:`scenario._stepuserapi.StepUserApi.ACTION()`
    and :py:meth:`scenario._stepuserapi.StepUserApi.RESULT()` methods
    return ``False``,
    which prevents the test script from being executed.
2. to execute the test script:
    in that case, these methods return ``True``,
    which lets the test script being executed.

The expected result test script sections may usually use assertion methods
provided by the :py:class:`scenario.Assertions` class:

.. literalinclude:: ../../demo/commutativeaddition.py
    :language: python
    :start-at: self.RESULT("result1 and result2 are the same.")
    :end-at: self.assertequal
    :dedent:

Eventually, the :py:meth:`scenario._stepuserapi.StepUserApi.evidence()` calls register :ref:`test evidence <evidence>` with the test results.
This kind of call may be used under an action or expected result ``if`` statement.

.. literalinclude:: ../../demo/commutativeaddition.py
    :language: python
    :start-at: self.ACTION("Compute (a + b)
    :end-at: self.evidence
    :dedent:

.. literalinclude:: ../../demo/commutativeaddition.py
    :language: python
    :start-at: self.RESULT("result1 and result2 are the same.")
    :end-at: self.evidence
    :dedent:

Your scenario is now ready to execute.


.. _quickstart.execution:

Scenario execution
------------------

A scenario must be executed with a launcher script.

A default launcher script is provided within the 'bin' directory
(from the main directory of the `scenario` library):

.. code-block:: bash

    $ ./bin/run-test.py --help

.. literalinclude:: ../data/run-test.help.log
    :language: none

.. tip::

    See the :ref:`launcher script extension <launcher>` section
    in order to define your own launcher if needed.

Give your scenario script as a positional argument to execute it:

.. code-block:: bash

    $ ./bin/run-test.py ./demo/commutativeaddition.py

.. literalinclude:: ../data/commutativeaddition.log
    :language: none

.. note:: The output presented above is a simplified version for documentation concerns.
          By default, test outputs are colored, and log lines give their timestamp
          (see :ref:`log colors <logging.colors>` and :ref:`log date/time <logging.date-time>` sections).


.. _quickstart.reuse:

Test code reuse
---------------

In order to quickly get a first test case running,
the example before defines a scenario with `step methods`.

As introduced in the :ref:`purpose section <purpose>`,
the `scenario` framework is better being used with :ref:`step objects <step-objects>` for test code reuse.

If you're interested in test code reuse,
go straight away to :ref:`step object <step-objects>` or :ref:`subscenario <subscenarios>` sections.

Otherwise, take a dive in the :ref:`advanced menu <advanced>` for further information on `scenario` features.
