# -*- coding: utf-8 -*-

# Copyright 2020-2023 Alexis Royer <https://github.com/alxroyer/scenario>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


class Feature:
    def __init__(
            self,
            id,  # type: str  # noqa  ## Shadows built-in name 'id'
            title,  # type: str
            text,  # type: str
    ):  # type: (...) -> None
        self.id = id  # type: str
        self.title = title  # type: str
        self.text = text  # type: str

    def __repr__(self):  # type: () -> str
        return f"<Feature id={self.id!r} title={self.title!r}>"

    def __str__(self):  # type: () -> str
        return f"{self.id} - {self.title}"


SCENARIO_EXECUTION = Feature(
    id="SCENARIO_EXECUTION",
    title="Scenario steps execution",
    text="""
        A scenario is an assertive context that defines an ordered list of test steps.

        A scenario execution gives a final status:

        - SUCCESS,
        - WARNINGS (in case of known issues, see KNOWN_ISSUES),
        - FAIL (see ERROR_HANDLING).
    """,
)  # type: Feature

DOC_ONLY = Feature(
    id="DOC_ONLY",
    title="Documentation generation",
    text="""
        The scenario framework shall generate the test documentation without executing the test.
    """,
)  # type: Feature

ERROR_HANDLING = Feature(
    id="ERROR_HANDLING",
    title="Error handling",
    text="""
        When an exception is thrown, the step ends in error immediately.
        The consecutive steps are not executed by default.
        The error information is eventually stored and displayed to help investigating on it.
        The test status falls to FAIL (see SCENARIO_EXECUTION).

        Error known issues (see KNOWN_ISSUES) also make the test status fall to FAIL,
        but they don't break the test execution.
    """,
)  # type: Feature

EVIDENCE = Feature(
    id="EVIDENCE",
    title="Evidence collection",
    text="""
        Evidence may be saved in the test report
        with their related actions and expected results.
    """,
)  # type: Feature

KNOWN_ISSUES = Feature(
    id="KNOWN_ISSUES",
    title="Known issues",
    text="""
        Known issues may be registered at the scenario definition level,
        or during test execution.

        By default, known issues generate execution warnings.
        These warnings are stored in reports,
        and make the test status fall to WARNINGS (see SCENARIO_EXECUTION)
        unless the test is executed in --doc-only mode.

        Known issues may be registered with an optional issue level,
        an ``int`` value possibly linked with a meaningful name.
        When an error issue level threshold is set, issue levels from and above are considered as errors (see ERROR_HANDLING).
        When an ignored issue level threshold is set, issue levels from and under are ignored.

        Known issues may also be registered with an optional issue id,
        referencing a ticket in a tier bugtracking system.
        A URL builder handler may be configured in order to facilitate the navigation to from test reports.
    """,
)  # type: Feature

LOGGING = Feature(
    id="LOGGING",
    title="Logging facilities",
    text="""
        The scenario framework provides logging facilities
        with the following characteristics in order to ease test execution analyses:

        - Date/time timestamps,
        - Log levels: ERROR, WARNING, INFO, DEBUG,
        - Log classes,
        - Log level colorization,
        - Log class colorization,
        - Scenario stack indentation,
        - Additional user indentation,
        - Console logging (by default) and/or file logging.
    """,
)  # type: Feature

DEBUG_LOGGING = Feature(
    id="DEBUG_LOGGING",
    title="Debug logging facilities",
    text="""
        The logging facilites makes it possible to activate dynamically debug logging for each log class.
    """,
)  # type: Feature

SCENARIO_LOGGING = Feature(
    id="SCENARIO_LOGGING",
    title="`scenario` logging",
    text="""
        The scenario execution provides log information that lets the tester know the useful information about it:

        - The name of the scenario being executed,
        - The scenario attributes declared with it (see ATTRIBUTES),
        - The steps, actions and expected results being executed,
        - The errors that occurred (see ERROR_HANDLING),
        - The evidence collected (see EVIDENCE),
        - The known issues registered (see KNOWN_ISSUES),
        - The final status of the test execution.
    """,
)  # type: Feature

SCENARIO_REPORT = Feature(
    id="SCENARIO_REPORT",
    title="Scenario reports",
    text="""
        A scenario execution shall output a JSON report file.

        This report saves a structured information for a test execution.
        See SCENARIO_LOGGING for the list of items that scenario report contains.
    """,
)  # type: Feature

STATISTICS = Feature(
    id="STATISTICS",
    title="Scenario execution statistics",
    text="""
        The scenario execution shall give statistics on the number of steps, actions and expected results.
    """,
)  # type: Feature

ALTERNATIVE_SCENARIOS = Feature(
    id="ALTERNATIVE_SCENARIOS",
    title="Alternative scenarios",
    text="""
        A scenario may be derived from another one
        (basically an error scenario derivating from a nominal one),
        which can be done through different means:

        - Step picking,
        - Partial subscenarios execution,
        - Inheritance.
    """,
)  # type: Feature

STEP_PICKING = Feature(
    id="STEP_PICKING",
    title="Step picking",
    text="""
        A scenario shall be constituted by picking steps already defined.
    """,
)  # type: Feature

SUBSCENARIOS = Feature(
    id="SUBSCENARIOS",
    title="Subscenarios",
    text="""
        A scenario shall execute all or part of other scenarios as subscenarios.
    """,
)  # type: Feature

GOTO = Feature(
    id="GOTO",
    title="Jumping to another step",
    text="""
        A scenario execution shall jump to another step within the scenario.
    """,
)  # type: Feature

CONFIG_DB = Feature(
    id="CONFIG_DB",
    title="General configuration database",
    text="""
        The scenario framework provides a general configuration database.
        This database may be fed with configuration files or single values,
        either from the command line or programmatically.
        Configuration files may be in the INI, JSON or YAML format.

        Configurations are key-value pairs.
        Keys are in the 'section.subsection.(...).leaf' form (1).
        The configuration database also handles lists of values or sub-sections (2).
        Final values can be basic types like strings, integers or float numbers.

        (1) For INI files, the use of the dot character in section names can be used to declare sub-sections.

        (2) No lists available with INI files.

        When several configuration files are given,
        the configuration values from the latter overloads the ones from the formers.

        Configuration files may also be saved from the configuration database eventually.
    """,
)  # type: Feature

MULTIPLE_SCENARIO_EXECUTION = Feature(
    id="MULTIPLE_SCENARIO_EXECUTION",
    title="Multiple scenario execution",
    text="""
        Several scenarios may be executed with a single command line.
        Whether the tests succeed or fail, the command line executes every scenario given.
        The log output, in the end, gives a summary of the scenario execution status, and highlights the errors and warnings.
    """,
)  # type: Feature

CAMPAIGNS = Feature(
    id="CAMPAIGNS",
    title="Campaign executions",
    text="""
        A campaign is the execution of a set of test suites, each being a set of test cases, i.e. scenarios.
        Whether the tests succeed or fail, the campaign keeps going on.

        Test results (see SCENARIO_REPORT) are stored in the output directory.
        A JUnit XML campaign report is also saved in the output directory.

        The log output, in the end, gives a summary of the scenario execution status, and highlights the errors and warnings (see MULTIPLE_SCENARIO_EXECUTION).
    """,
)  # type: Feature

ATTRIBUTES = Feature(
    id="ATTRIBUTES",
    title="Scenario attributes",
    text="""
        Scenario attributes can be set with scenario definitions.

        They consist in free fields that are:

        - displayed in the console with scenario logging (see SCENARIO_LOGGING),
        - stored in scenario reports (see SCENARIO_REPORT).

        They may be displayed with scenario results,
        when executing multiple scenarios (see MULTIPLE_SCENARIO_EXECUTION),
        or when executing a campaign (see CAMPAIGNS).
    """,
)  # type: Feature
