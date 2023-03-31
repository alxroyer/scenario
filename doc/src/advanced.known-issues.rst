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


.. _known-issues:

Known issues
============

One dilemma we commonly have to face when managing tests is to deal with known issues.

On the one hand, as long as a known issue exists, the feature that the test verifies cannot be said to be completely fulfilled.
Thus, putting the test in the :py:const:`scenario._executionstatus.ExecutionStatus.FAIL` status is a formal way
to mark the corresponding feature as not fully supported yet.

On the other hand, from the continuous integration point of view,
seeing the test in the :py:const:`scenario._executionstatus.ExecutionStatus.FAIL` status from day to day,
apparently because of that known issue,
may occult useful information on other possible regressions.

That's the reason why the `scenario` framework provides an API in order to register known issues in the tests
(see :py:meth:`scenario._stepuserapi.StepUserApi.knownissue()` and :py:class:`scenario._knownissues.KnownIssue`).


.. _known-issues.default:

Default behaviour
-----------------

By default, known issues are handled as simple warnings,
making the tests fall to the intermediate :py:const:`scenario._executionstatus.ExecutionStatus.WARNINGS` status.
The warnings are logged in the console, and saved in :ref:`test reports <reports>`.

This way, a regression will be highlighted as soon as it occurs by the continuous integration process,
in as much as the test will turn to the :py:const:`scenario._executionstatus.ExecutionStatus.FAIL` status.

This way, one can safely implement a workaround in a test affected by a known issue,
but track it formally in the same time.
Once the known issue has been fixed in the *software/system under test* (SUT),
the workaround and the known issue reference can be removed from the test,
hopefully turning the latter into the :py:const:`scenario._executionstatus.ExecutionStatus.SUCCESS` status.


.. _known-issues.issue-levels:

Issue levels
------------

Issues may exist for various reasons, representing various criticities:

1. As introduced in the section before, an issue may be related to the *software/system under test* (SUT).
2. But talking about incremental development, it may also be because the SUT has not fully implemented a given feature yet,
   this being planned in a later release, which is a less critical situation than (1).
3. The issue may also be related to defects of the test environment, which is obviously less critical than defects of the SUT itself (1).
4. But talking about the test environment, it may also be related to the context in which the tests are being executed
   (Internet not ready, ability of the test platform, ...) which may be less critical again than real defects of the test environment (3).
5. *Other reasons...*

In order to discriminate the various situations, known issues may be registered with an issue level (:py:class:`scenario._issuelevels.IssueLevel`).

Issue levels are basically integer values.
The higher, the more critical.
Programmatically, they can be described by an ``enum.IntEnum``.

They can be associated with meaningful names,
with the help of the :py:meth:`scenario._issuelevels.IssueLevel.definenames()` and/or :py:meth:`scenario._issuelevels.IssueLevel.addname()` methods,
or :ref:`scenario.issue_levels <config-db.scenario.issue_levels>` configurations.
These names make it easier to read in the console, and maintain in the test code.

.. admonition:: Enum-defined issue levels
    :class: tip

    If issue levels are defined with an ``enum.IntEnum``,
    this ``enum.IntEnum`` class can be passed on as is to the :py:meth:`scenario._issuelevels.IssueLevel.definenames()` method.

    .. code-block:: python

        import enum
        import scenario


        # Define issue levels.
        class CommonIssueLevel(enum.IntEnum):
            SUT = 40
            TEST = 30
            CONTEXT = 20
            PLANNED = 10
        scenario.IssueLevel.definenames(CommonIssueLevel)


        class MyStep(scenario.Step):

            def step():
                self.STEP("...")

                # Track a known issue, with issue level *PLANNED=10*.
                # By default, this known issue is logged in the console, and saved in JSON reports, as warning.
                self.knownissue(
                    level=CommonIssueLevel.PLANNED,
                    message="Waiting for feature XXX to be implemented",
                )

                # Do not proceed with the following test actions and expected results until feature XXX is implemented.
                # if self.ACTION("..."):
                #     ...


.. _known-issues.issue-level-error:
.. _knwon-issues.issue-level-ignored:

Error / ignored issue level thresholds
--------------------------------------

Once issue levels are set, two issue level thresholds may be used when launching the test or campaign
in order to tell which issue levels should be considered as errors, warnings, or simply ignored.

.. list-table:: Error and ignored issue levels
    :widths: auto
    :header-rows: 1
    :stub-columns: 1

    * -
      - Configuration
      - Effect

    * - Error issue level

      - ``--issue-level-error`` option or :ref:`scenario.issue_level_error <config-db.scenario.issue_level_error>` configuration

      - Known issues with issue level greater than or equal to the given value are considered as errors.

        .. note:: When the *error issue level* is set, known issues without issue level turn to errors by default.

        Known errors don't break the test execution as :ref:`test exceptions <errors>` do.
        By the way, several errors may be logged and saved in :ref:`test reports <reports>`.

    * - Ignored issue level

      - ``--issue-level-ignored`` option or :ref:`scenario.issue_level_ignored <config-db.scenario.issue_level_ignored>` configuration

      - Known issues with issue level less than or equal to the given value are ignored.

This way, without changing the test code,
permissive executions can be launched for continuous integration purpose,
but stricter executions can still be launched to constitute official test results.


.. _known-issues.issue-ids:

Issue identifiers
-----------------

Known issues may be registered with an issue identifier, refering to a tier bugtracker tool.

Optionally, a URL builder handler may be installed (see :py:meth:`scenario._knownissues.KnownIssue.seturlbuilder()`),
in order to build URLs to the tier bugtracker tool from issue identifiers.
These URLs are then displayed in the console and saved in :ref:`test reports <reports>`,
and are usually directly clickable from both contexts.

.. code-block:: python

    import scenario
    import typing


    # Define and install a URL builder handler.
    def _urlbuilder(issue_id):  # type: (str) -> typing.Optional[str]
        if issue_id.startswith("#"):
            return f"https://repo/issues/{issue_id.lstrip('#')}"
        # Unexpected issue id format, return `None` for no URL.
        return None
    scenario.KnownIssue.seturlbuilder(_url_builder)


    class MyStep(scenario.Step):

        def step():
            self.STEP("...")

            # Track issue #10.
            # Thanks to the URL builder handler, the 'https://repo/issues/10' URL is displayed in the console and saved in JSON reports.
            self.knownissue(
                id="#10",
                message="Waiting for feature #10 to be implemented",
            )

            # Do not proceed with the following test actions and expected results until feature #10 is implemented.
            # if self.ACTION("..."):
            #     ...

.. tip::
    :ref:`Issue levels <known-issues.issue-levels>` and :ref:`issue identifiers <known-issues.issue-ids>` can be used in the same time
    when registering known issues.


.. _known-issues.registration-level:

Registration: definition v/s execution level
--------------------------------------------

It is generally preferrable to register known issues at the definition level (i.e. outside action / result blocks).
Doing so, even though an error occurs during a test execution, known issues are still saved with the test results.

Nevertheless, certain known issues can't be registered at the definition level
(issues related to the test execution context for instance).
For such situations, it remains possible to register known issues at the execution level (i.e. inside action / result blocks),
but there is no guarantee that the known issue will be saved with the test results, since it depends on the test execution.

.. admonition:: Known issues from test libraries
    :class: tip

    The :meth:`scenario._scenariostack.ScenarioStack.knownissue()` is provided
    in order to register known issues from anywhere in :ref:`test libraries <test-libs>`.
