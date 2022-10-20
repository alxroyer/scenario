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


.. _known-issues:

Known issues
============

One dilemma we commonly have when managing tests is how to deal with known issues.

On the one hand, while a known issue exists, the feature that the test verifies cannot be said to be completely fulfilled.
Thus, putting the test in a :py:const:`scenario.executionstatus.ExecutionStatus.FAIL` state is a formal way
to mark the corresponding feature as not fully supported yet.

On the other hand, from the continuous integration point of view,
seeing the test in a :py:const:`scenario.executionstatus.ExecutionStatus.FAIL` state from day to day,
apparently because of that known issue,
may occult useful information on other possible regressions.

That's the reason why the :mod:`scenario` framework provides an API in order to register known issues in the tests
(see :py:meth:`scenario.stepuserapi.StepUserApi.knownissue()`).

By default, known issues are handled in *relax mode*, which means that they are considered as warnings.
This way, a regression will be highlighted as soon as it occurs by the continuous integration,
in as much as the test will turn from the :py:const:`scenario.executionstatus.ExecutionStatus.WARNINGS`
to the :py:const:`scenario.executionstatus.ExecutionStatus.FAIL` state.

When producing official test results, the tests can be executed in *strict mode*.
In this *strict mode*, known issues are handled as non-blocking errors,
and therefore ensure the desired :py:const:`scenario.executionstatus.ExecutionStatus.FAIL` state of the tests.

This way, one can safely implement a workaround in a test affected by a known issue,
but track it formally at the same time.
Once the known issue has been fixed in the software/system under test,
the workaround and the known issue reference can be removed from the test,
hopefully turning it to the :py:const:`scenario.executionstatus.ExecutionStatus.SUCCESS` state.

.. todo:: Documentation needed for known issues:

    - Examples: *relax-mode* & *strict-mode*
    - Recommendation to declare known issues outside of ACTION/RESULT blocks, i.e. at definition level.
    - :py:meth:`scenario.scenariostack.ScenarioStack.knownissue()` available to declare known issues
      from :ref:`test libraries <test-libs>`.
