.. Copyright 2020-2022 Alexis Royer <https://github.com/Alexis-ROYER/scenario>
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


.. _arch:

Architecture
============

.. _arch.execution:

Scenario execution
------------------

The :py:class:`scenario.scenariodefinition.ScenarioDefinition`, :py:class:`scenario.stepdefinition.StepDefinition`
and :py:class:`scenario.actionresultdefinition.ActionResultDefinition` classes
are the base classes for the definition of scenarios, steps, actions and expected results respectively.

The :py:class:`scenario.scenariorunner.ScenarioRunner` instance handles the execution of them.

Its :py:meth:`scenario.scenariorunner.ScenarioRunner.main()` method is the entry point
that a :ref:`launcher script <launcher>` should call.
This method:

1. analyzes the command line arguments and loads the configuration files (see the :ref:`related design section <arch.configuration>`),
2. builds a scenario instance from the given scenario script, with reflexive programming,
3. proceeds with the scenario execution.

The :py:class:`scenario.scenariorunner.ScenarioRunner` class works with a couple of helper classes.

The :py:class:`scenario.scenarioexecution.ScenarioExecution`, :py:class:`scenario.stepexecution.StepExecution`
and :py:class:`scenario.actionresultexecution.ActionResultExecution` classes
store the execution information related to definition classes cited above.

.. list-table:: Definition v/s execution classes
    :widths: auto
    :header-rows: 1
    :stub-columns: 1

    * -
      - Definition
      - Execution

    * - Scenario level

      - :py:class:`scenario.scenariodefinition.ScenarioDefinition`

        - Describes the list of :py:class:`scenario.stepdefinition.StepDefinition` that define the scenario.
        - Gives the related :py:class:`scenario.scenarioexecution.ScenarioExecution` instance when executed.

      - :py:class:`scenario.scenarioexecution.ScenarioExecution`

        - Tells which step is currently being executed.
        - Stores the execution error, if any.
        - Stores execution statistics.
        - Gives access to the related :py:class:`scenario.scenariodefinition.ScenarioDefinition` instance.

    * - Step level

      - :py:class:`scenario.stepdefinition.StepDefinition`

        - Describes the list of :py:class:`scenario.actionresultdefinition.ActionResultDefinition` that define the step.
        - Gives the related :py:class:`scenario.stepexecution.StepExecution` instances when executed.

      - :py:class:`scenario.stepexecution.StepExecution`

        - Tells wich action or expected result is currently being executed.
        - Stores the execution error, if any.
        - Stores execution statistics.
        - Gives access to the related :py:class:`scenario.stepdefinition.StepDefinition` instance.

    * - Action and expected result level

      - :py:class:`scenario.actionresultdefinition.ActionResultDefinition`

        - Describes an action or an expected result, with its text.
        - Gives the related :py:class:`scenario.actionresultexecution.ActionResultExecution` instances when executed.

      - :py:class:`scenario.actionresultexecution.ActionResultExecution`

        - Stores :ref:`evidence <evidence>`.
        - Stores the execution error, if any.
        - Stores execution statistics.
        - Gives access to the related :py:class:`scenario.actionresultdefinition.ActionResultDefinition` instance.

.. note::
    Due to the :ref:`goto <goto>` feature, steps, actions and expected results may be executed several times
    within a single scenario execution.

The :py:class:`scenario.scenariostack.ScenarioStack` also is a helper class for :py:class:`scenario.scenariorunner.ScenarioRunner`:

- It stores the current stack of scenarios being executed (see :ref:`sub-scenarios <arch.subscenario-execution>`.
- It also provides a couple of accessors to the current step, action or expected result being executed.

The :py:class:`scenario.scenariorunner.ScenarioRunner` class remains the conductor of all:

#. The :py:meth:`scenario.scenariorunner.ScenarioRunner.main()` method is called.
#. For each script path given in the command line:

   #. A main :py:class:`scenario.scenariodefinition.ScenarioDefinition` instance is created [#meth-executepath]_
      from the scenario class in the script [#class-ScenarioDefinitionHelper]_.
      A :py:class:`scenario.scenarioexecution.ScenarioExecution` instance is created as well,
      and pushed to the :py:class:`scenario.scenariostack.ScenarioStack` instance [#meth-beginscenario]_.
   #. :py:attr:`scenario.scenariorunner.ScenarioRunner._execution_mode`
      is set to :py:attr:`scenario.scenariorunner.ScenarioRunner.ExecutionMode.BUILD_OBJECTS`:

      #. In case the steps are defined with ``step...()`` methods,
         the :py:class:`scenario.scenariodefinition.ScenarioDefinition` is fed using reflexive programmation
         (the same for scenario attributes defined with class members)
         [#meth-beginscenario]_ [#class-ScenarioDefinitionHelper]_.
      #. Each step is executed a first time [#meth-beginscenario]_ [#meth-execstep]_ in order to build
         its :py:class:`scenario.actionresultdefinition.ActionResultDefinition` instances
         for each :py:meth:`scenario.stepuserapi.StepUserApi.ACTION()` and :py:meth:`scenario.stepuserapi.StepUserApi.RESULT()` call [#meth-onactionresult]_.
         During this first execution of the step, the two latter methods return ``False`` [#attr-execution_mode]_,
         which prevents the test from being executed at this point.

   #. :py:attr:`scenario.scenariorunner.ScenarioRunner._execution_mode`
      is set to :py:attr:`scenario.scenariorunner.ScenarioRunner.ExecutionMode.EXECUTE`
      or :py:attr:`scenario.scenariorunner.ScenarioRunner.ExecutionMode.DOC_ONLY` [#meth-executescenario]_.
      For each step [#meth-executescenario]_ [#meth-execstep]_:

      #. A :py:class:`scenario.stepexecution.StepExecution` instance is created [#meth-execstep]_.
      #. The user test code is called [#meth-execstep]_.
      #. For each :py:meth:`scenario.stepuserapi.StepUserApi.ACTION()`
         and :py:meth:`scenario.stepuserapi.StepUserApi.RESULT()` call [#meth-onactionresult]_:

         #. A :py:class:`scenario.actionresultexecution.ActionResultExecution` instance is created [#meth-onactionresult]_.
         #. If a sub-scenario is executed, then it is pushed to the :py:class:`scenario.scenariostack.ScenarioStack` instance [#meth-beginscenario]_,
            built [#meth-beginscenario]_ [#class-ScenarioDefinitionHelper]_ [#meth-execstep]_,
            executed [#meth-executescenario]_ [#meth-execstep]_,
            and eventually popped from the :py:class:`scenario.scenariostack.ScenarioStack` instance [#meth-endscenario]_.

   #. The main scenario is eventually popped from the :py:class:`scenario.scenariostack.ScenarioStack` instance [#meth-endscenario]_.

#. If there were several scenarios executed, the final results are displayed [#class-ScenarioResults]_.

---

.. [#attr-execution_mode] See :py:attr:`scenario.scenariorunner.ScenarioRunner._execution_mode`.
.. [#meth-executepath] See :py:meth:`scenario.scenariorunner.ScenarioRunner.executepath()`.
.. [#meth-executescenario] See :py:meth:`scenario.scenariorunner.ScenarioRunner.executescenario()`.
.. [#meth-beginscenario] See :py:meth:`scenario.scenariorunner.ScenarioRunner._beginscenario()`.
.. [#meth-execstep] See :py:meth:`scenario.scenariorunner.ScenarioRunner._execstep()`.
.. [#meth-onactionresult] See :py:meth:`scenario.scenariorunner.ScenarioRunner.onactionresult()`.
.. [#meth-endscenario] See :py:meth:`scenario.scenariorunner.ScenarioRunner._endscenario()`.
.. [#class-ScenarioDefinitionHelper] See :py:class:`scenario.scenariodefinition.ScenarioDefinitionHelper`.
.. [#class-ScenarioResults] See :py:class:`scenario.scenarioresults.ScenarioResults`.


.. _arch.subscenario-execution:

Subscenarios
------------

.. todo:: Documentation needed: Architecture - Subscenarios


.. _arch.error-management:

Assertions, error management & execution locations
--------------------------------------------------

.. todo:: Documentation needed: Architecture - Error management


.. _arch.campaign-execution:

Campaign execution
------------------

.. todo:: Documentation needed: Architecture - Campaign execution

    - `CampaignRunner`
    - `CampaignExecution`, `TestSuiteExecution`, `TestCaseExecution` classes.
    - Test suite files.
    - Test cases executed in separate processes.


.. _arch.logging:

Logging
-------

.. todo:: Documentation needed: Architecture - Logging


.. _arch.configuration:

Configuration
-------------

.. todo:: Documentation needed: Architecture - Configuration


.. _arch.paths:

Path management
---------------

.. todo:: Documentation needed: Architecture - Path
