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


.. _evidence:

Test evidence
=============

Storing test evidence with the test results might be a good practice.

When one reads test results, and only knows about action and expected result texts,
he/she has to trust that the test script actually did what is written in the texts given.

In order to tackle this uncertainty, evidence may be stored with test results.
Doing so reinforces the credibility of the results,
in as much as a human could check manually that the automatic test script did the right thing.

As introduced in the :ref:`quickstart guide <quickstart.first-scenario>`,
the :py:meth:`scenario.stepuserapi.StepUserApi.evidence()` method,
available in :py:class:`scenario.scenariodefinition.ScenarioDefinition` and :py:class:`scenario.stepdefinition.StepDefinition` classes,
lets you save evidence while the test is executed.

:ref:`Assertion routines <assertions.evidence-param>` defined in the :py:class:`scenario.assertions.Assertions` class
can be used to collect evidence as well.
Set the optional ``evidence`` parameter to either :py:const:`True` or a string describing what is being checked.

Test evidence is saved with the scenario JSON reports in the 'evidence' list of each action or expected result execution.
