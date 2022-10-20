# -*- coding: utf-8 -*-

# Copyright 2020-2022 Alexis Royer <https://github.com/Alexis-ROYER/scenario>
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

"""
Campaign execution results.

The :class:`CampaignExecution` class stores the execution results of a campaign.
It owns a list of :class:`TestSuite` instances (actually one, called 'All'),
which owns a list of :class:`TestCase` instances (one test case per scenario).
"""

import typing

# `ExecutionStatus` used in method signatures.
from .executionstatus import ExecutionStatus
# `Path` used in method signatures.
from .path import Path
# `ScenarioExecution` used in method signatures.
from .scenarioexecution import ScenarioExecution
# `ExecTotalStats` and `TimeStats` used in method signatures.
from .stats import ExecTotalStats, TimeStats
# `TestError` used in method signatures.
from .testerrors import TestError

if typing.TYPE_CHECKING:
    # `AnyPathType` used in method signatures.
    # Type declared for type checking only.
    from .path import AnyPathType


class CampaignExecution:
    """
    Main campaign result object.
    """

    def __init__(
            self,
            outdir,  # type: typing.Optional[AnyPathType]
    ):  # type: (...) -> None
        """
        :param outdir:
            Output directory path.

            ``None`` initializes the output directory path with the current working directory.
        """
        #: Output directory path.
        self.outdir = Path(outdir)  # type: Path
        #: Test suite results.
        self.test_suite_executions = []  # type: typing.List[TestSuiteExecution]
        #: Time statistics.
        self.time = TimeStats()  # type: TimeStats

    def __repr__(self):  # type: (...) -> str
        """
        Canonical string representation.
        """
        # Use default implementation.
        return super().__repr__()

    @property
    def junit_path(self):  # type: (...) -> Path
        """
        JUnit path.
        """
        return self.outdir / "campaign.xml"

    @property
    def steps(self):  # type: (...) -> ExecTotalStats
        """
        Step statistics.
        """
        _stats = ExecTotalStats()  # type: ExecTotalStats
        for _test_suite_execution in self.test_suite_executions:  # type: TestSuiteExecution
            _stats.total += _test_suite_execution.steps.total
            _stats.executed += _test_suite_execution.steps.executed
        return _stats

    @property
    def actions(self):  # type: (...) -> ExecTotalStats
        """
        Action statistics.
        """
        _stats = ExecTotalStats()  # type: ExecTotalStats
        for _test_suite_execution in self.test_suite_executions:  # type: TestSuiteExecution
            _stats.total += _test_suite_execution.actions.total
            _stats.executed += _test_suite_execution.actions.executed
        return _stats

    @property
    def results(self):  # type: (...) -> ExecTotalStats
        """
        Expected result statistics.
        """
        _stats = ExecTotalStats()  # type: ExecTotalStats
        for _test_suite_execution in self.test_suite_executions:  # type: TestSuiteExecution
            _stats.total += _test_suite_execution.results.total
            _stats.executed += _test_suite_execution.results.executed
        return _stats

    @property
    def counts(self):  # type: (...) -> CampaignStats
        """
        Campaign statistics.
        """
        _stats = CampaignStats()
        for _test_suite_execution in self.test_suite_executions:  # type: TestSuiteExecution
            _stats.total += _test_suite_execution.counts.total
            _stats.disabled += _test_suite_execution.counts.disabled
            _stats.skipped += _test_suite_execution.counts.skipped
            _stats.warnings += _test_suite_execution.counts.warnings
            _stats.failures += _test_suite_execution.counts.failures
            _stats.errors += _test_suite_execution.counts.errors
        return _stats


class TestSuiteExecution:
    """
    Test suite execution object.
    """

    def __init__(
            self,
            campaign_execution,  # type: CampaignExecution
            test_suite_path,  # type: typing.Optional[AnyPathType]
    ):  # type: (...) -> None
        """
        :param campaign_execution:
            Owner :class:`CampaignExecution` object.
        :param test_suite_path:
            Test suite file path.

            ``None`` initializes the :attr:`test_suite_file` member with a *void* file path,
            which makes the :attr:`test_suite_file` instance *void* as well.
            This path can be fixed programmatically later on.
        """
        from .testsuitefile import TestSuiteFile

        #: Owner campaign execution.
        self.campaign_execution = campaign_execution  # type: CampaignExecution
        #: Campaign file.
        self.test_suite_file = TestSuiteFile(Path(test_suite_path))  # type: TestSuiteFile
        #: Test cases.
        self.test_case_executions = []  # type: typing.List[TestCaseExecution]
        #: Time statistics.
        self.time = TimeStats()  # type: TimeStats

    def __repr__(self):  # type: (...) -> str
        """
        Canonical string representation.
        """
        from .reflex import qualname

        return f"<{qualname(type(self))} of '{self.test_suite_file.path}'>"

    @property
    def steps(self):  # type: (...) -> ExecTotalStats
        """
        Step statistics.
        """
        _stats = ExecTotalStats()  # type: ExecTotalStats
        for _test_case_execution in self.test_case_executions:  # type: TestCaseExecution
            if _test_case_execution.scenario_execution:
                _stats.add(_test_case_execution.scenario_execution.step_stats)
        return _stats

    @property
    def actions(self):  # type: (...) -> ExecTotalStats
        """
        Action statistics.
        """
        _stats = ExecTotalStats()  # type: ExecTotalStats
        for _test_case_execution in self.test_case_executions:  # type: TestCaseExecution
            if _test_case_execution.scenario_execution:
                _stats.add(_test_case_execution.scenario_execution.action_stats)
        return _stats

    @property
    def results(self):  # type: (...) -> ExecTotalStats
        """
        Expected result statistics.
        """
        _stats = ExecTotalStats()  # type: ExecTotalStats
        for _test_case_execution in self.test_case_executions:  # type: TestCaseExecution
            if _test_case_execution.scenario_execution:
                _stats.add(_test_case_execution.scenario_execution.result_stats)
        return _stats

    @property
    def counts(self):  # type: (...) -> CampaignStats
        """
        Campaign statistics.
        """
        _stats = CampaignStats()  # type: CampaignStats
        _stats.total = len(self.test_case_executions)
        for _test_case_execution in self.test_case_executions:  # type: TestCaseExecution
            if not _test_case_execution.scenario_execution:
                _stats.errors += 1
            elif _test_case_execution.scenario_execution.errors:
                _stats.failures += 1
            elif _test_case_execution.scenario_execution.warnings:
                _stats.warnings += 1
        return _stats


class TestCaseExecution:
    """
    Test case (i.e. test scenario) execution object.
    """

    def __init__(
            self,
            test_suite_execution,  # type: TestSuiteExecution
            script_path,  # type: typing.Optional[AnyPathType]
    ):  # type: (...) -> None
        """
        :param test_suite_execution:
            Owner :class:`TestSuite` object.
        :param script_path:
            Scenario script path.

            ``None`` initializes the :attr:`script_path` member with a *void* file path.
            This path can be fixed programmatically later on.
        """
        #: Owner test suite execution.
        self.test_suite_execution = test_suite_execution  # type: TestSuiteExecution
        #: Scenario script path.
        self.script_path = Path(script_path)  # type: Path
        #: Time statistics.
        self.time = TimeStats()  # type: TimeStats
        #: Test case log output.
        self.log = LogFileReader()  # type: LogFileReader
        #: Test case JSON output.
        self.json = JsonReportReader()  # type: JsonReportReader

    def __repr__(self):  # type: (...) -> str
        """
        Canonical string representation.
        """
        from .reflex import qualname

        return f"<{qualname(type(self))} of '{self.script_path}'>"

    @property
    def scenario_execution(self):  # type: (...) -> typing.Optional[ScenarioExecution]
        """
        Scenario execution data.
        """
        if self.json.content:
            return self.json.content.execution
        return None

    @property
    def name(self):  # type: (...) -> str
        """
        Test case name.
        """
        if self.scenario_execution:
            return self.scenario_execution.definition.name
        else:
            # Use the script pretty path by default (base info to constitute the scenario name actually).
            return self.script_path.prettypath

    @property
    def status(self):  # type: (...) -> ExecutionStatus
        """
        Scenario execution status.
        """
        if self.scenario_execution:
            return self.scenario_execution.status
        else:
            # FAIL by default.
            return ExecutionStatus.FAIL

    @property
    def errors(self):  # type: (...) -> typing.List[TestError]
        """
        Test errors.
        """
        if self.scenario_execution:
            return self.scenario_execution.errors
        return []

    @property
    def warnings(self):  # type: (...) -> typing.List[TestError]
        """
        Warnings.
        """
        if self.scenario_execution:
            return self.scenario_execution.warnings
        return []

    @property
    def steps(self):  # type: (...) -> ExecTotalStats
        """
        Step statistics.
        """
        if self.scenario_execution:
            return self.scenario_execution.step_stats
        return ExecTotalStats()

    @property
    def actions(self):  # type: (...) -> ExecTotalStats
        """
        Action statistics.
        """
        if self.scenario_execution:
            return self.scenario_execution.action_stats
        return ExecTotalStats()

    @property
    def results(self):  # type: (...) -> ExecTotalStats
        """
        Expected result statistics.
        """
        if self.scenario_execution:
            return self.scenario_execution.result_stats
        return ExecTotalStats()


class CampaignStats:
    """
    JUnit compatible statistics.

    .. admonition:: Failures v/s errors
        :class: note

        According to https://stackoverflow.com/questions/3425995/whats-the-difference-between-failure-and-error-in-junit:

        - tests are considered that they have "failed" because of an assertion,
        - tests are said to be in "error" but of an unexpected error.
    """

    def __init__(self):  # type: (...) -> None
        """
        Initializes all counters with ``0``.
        """
        #: Total number of test cases.
        self.total = 0  # type: int
        #: Number of test cases disabled.
        self.disabled = 0  # type: int
        #: Number of skipped test cases.
        #:
        #: For test suites.
        self.skipped = 0  # type: int
        #: Number of tests that terminated with warnings.
        self.warnings = 0  # type: int
        #: Number of test cases that failed due to assertions.
        self.failures = 0  # type: int
        #: Number of test cases that failed unexpectedly.
        self.errors = 0  # type: int


class LogFileReader:
    """
    Log file path and content.
    """

    def __init__(self):  # type: (...) -> None
        """
        Initializes :attr:`path` and :attr:`content` attributes with ``None``.
        """
        #: Test case log file path.
        self.path = None  # type: typing.Optional[Path]
        #: Test case log file content.
        self.content = None  # type: typing.Optional[bytes]

    def read(self):  # type: (...) -> bool
        """
        Read the log file.

        :return: ``True`` when the log file could be read successfully, ``False`` otherwise.
        """
        from .loggermain import MAIN_LOGGER

        try:
            if self.path:
                self.content = self.path.read_bytes()
                return True
            else:
                MAIN_LOGGER.error("No log path to read")
        except Exception as _err:
            MAIN_LOGGER.error(f"Could not read log file '{self.path}': {_err}")
        return False


class JsonReportReader:
    """
    JSON file path and content.
    """

    def __init__(self):  # type: (...) -> None
        """
        Initializes :attr:`path` and :attr:`content` attributes with ``None``.
        """
        from .scenariodefinition import ScenarioDefinition
        from .path import Path

        #: Test case JSON file path.
        self.path = None  # type: typing.Optional[Path]
        #: Scenario execution data read from the test case JSON file.
        self.content = None  # type: typing.Optional[ScenarioDefinition]

    def read(self):  # type: (...) -> bool
        """
        Read the JSON report.

        :return: ``True`` when the JSON report file could be read and parsed successfully, ``False`` otherwise.
        """
        from .loggermain import MAIN_LOGGER
        from .scenarioreport import SCENARIO_REPORT

        if self.path:
            self.content = SCENARIO_REPORT.readjsonreport(self.path)
        else:
            MAIN_LOGGER.error("No JSON path to read")
        return self.content is not None
