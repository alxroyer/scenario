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

"""
Campaign execution results.

The :class:`CampaignExecution` class stores the execution results of a campaign.
It owns a list of :class:`TestSuiteExecution` instances (actually one, called 'All'),
which owns a list of :class:`TestCaseExecution` instances (one test case per scenario).
"""

import typing

if typing.TYPE_CHECKING:
    from ._executionstatus import ExecutionStatus as _ExecutionStatusType
    from ._path import AnyPathType as _AnyPathType
    from ._path import Path as _PathType
    from ._scenarioexecution import ScenarioExecution as _ScenarioExecutionType
    from ._stats import ExecTotalStats as _ExecTotalStatsType
    from ._testerrors import TestError as _TestErrorType


class CampaignExecution:
    """
    Main campaign result object.
    """

    def __init__(
            self,
            outdir,  # type: typing.Optional[_AnyPathType]
    ):  # type: (...) -> None
        """
        :param outdir:
            Output directory path.

            ``None`` initializes the output directory path with the current working directory.
        """
        from ._path import Path
        from ._stats import TimeStats

        #: Output directory path.
        self.outdir = Path(outdir)  # type: Path
        #: Campaign report path, when explicitly set.
        self._campaign_report_path = None  # type: typing.Optional[Path]
        #: Requirement database file path, when explicitly set.
        self._reqdb_path = None  # type: typing.Optional[Path]
        #: Downstream traceability file path, when explicitly set.
        self._downstream_traceability_path = None  # type: typing.Optional[Path]
        #: Upstream traceability file path, when explicitly set.
        self._upstream_traceability_path = None  # type: typing.Optional[Path]
        #: Test suite results.
        self.test_suite_executions = []  # type: typing.List[TestSuiteExecution]
        #: Time statistics.
        self.time = TimeStats()  # type: TimeStats

    def __repr__(self):  # type: () -> str
        """
        Canonical string representation.
        """
        # Use default implementation.
        return super().__repr__()

    @property
    def campaign_report_path(self):  # type: () -> _PathType
        """
        Campaign report path getter.

        Default path when not set yet.
        """
        if self._campaign_report_path is not None:
            return self._campaign_report_path
        return self.outdir / "campaign.xml"

    @campaign_report_path.setter
    def campaign_report_path(self, path):  # type: (_PathType) -> None
        """
        Campaign report path setter.
        """
        self._campaign_report_path = path

    @property
    def reqdb_path(self):  # type: () -> _PathType
        """
        Requirement database file path getter.

        Default path when not set yet.
        """
        if self._reqdb_path is not None:
            return self._reqdb_path
        return self.outdir / "req-db.json"

    @reqdb_path.setter
    def reqdb_path(self, path):  # type: (_PathType) -> None
        """
        Requirement database file path setter.
        """
        self._reqdb_path = path

    @property
    def downstream_traceability_path(self):  # type: () -> _PathType
        """
        Downstream traceability file path getter.

        Default path when not set yet.
        """
        if self._downstream_traceability_path is not None:
            return self._downstream_traceability_path
        return self.outdir / "req-downstream-traceability.json"

    @downstream_traceability_path.setter
    def downstream_traceability_path(self, path):  # type: (_PathType) -> None
        """
        Downstream traceability file path setter.
        """
        self._downstream_traceability_path = path

    @property
    def upstream_traceability_path(self):  # type: () -> _PathType
        """
        Upstream traceability file path getter.

        Default path when not set yet.
        """
        if self._upstream_traceability_path is not None:
            return self._upstream_traceability_path
        return self.outdir / "req-upstream-traceability.json"

    @upstream_traceability_path.setter
    def upstream_traceability_path(self, path):  # type: (_PathType) -> None
        """
        Upstream traceability file path setter.
        """
        self._upstream_traceability_path = path

    @property
    def steps(self):  # type: () -> _ExecTotalStatsType
        """
        Step statistics.
        """
        from ._stats import ExecTotalStats

        _stats = ExecTotalStats()  # type: ExecTotalStats
        for _test_suite_execution in self.test_suite_executions:  # type: TestSuiteExecution
            _stats.total += _test_suite_execution.steps.total
            _stats.executed += _test_suite_execution.steps.executed
        return _stats

    @property
    def actions(self):  # type: () -> _ExecTotalStatsType
        """
        Action statistics.
        """
        from ._stats import ExecTotalStats

        _stats = ExecTotalStats()  # type: ExecTotalStats
        for _test_suite_execution in self.test_suite_executions:  # type: TestSuiteExecution
            _stats.total += _test_suite_execution.actions.total
            _stats.executed += _test_suite_execution.actions.executed
        return _stats

    @property
    def results(self):  # type: () -> _ExecTotalStatsType
        """
        Expected result statistics.
        """
        from ._stats import ExecTotalStats

        _stats = ExecTotalStats()  # type: ExecTotalStats
        for _test_suite_execution in self.test_suite_executions:  # type: TestSuiteExecution
            _stats.total += _test_suite_execution.results.total
            _stats.executed += _test_suite_execution.results.executed
        return _stats

    @property
    def counts(self):  # type: () -> CampaignStats
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
            test_suite_path,  # type: typing.Optional[_AnyPathType]
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
        from ._path import Path
        from ._stats import TimeStats
        from ._testsuitefile import TestSuiteFile

        #: Owner campaign execution.
        self.campaign_execution = campaign_execution  # type: CampaignExecution
        #: Campaign file.
        self.test_suite_file = TestSuiteFile(Path(test_suite_path))  # type: TestSuiteFile
        #: Test cases.
        self.test_case_executions = []  # type: typing.List[TestCaseExecution]
        #: Time statistics.
        self.time = TimeStats()  # type: TimeStats

    def __repr__(self):  # type: () -> str
        """
        Canonical string representation.
        """
        from ._reflection import qualname

        return f"<{qualname(type(self))} of '{self.test_suite_file.path}'>"

    @property
    def steps(self):  # type: () -> _ExecTotalStatsType
        """
        Step statistics.
        """
        from ._stats import ExecTotalStats

        _stats = ExecTotalStats()  # type: ExecTotalStats
        for _test_case_execution in self.test_case_executions:  # type: TestCaseExecution
            if _test_case_execution.scenario_execution:
                _stats.add(_test_case_execution.scenario_execution.step_stats)
        return _stats

    @property
    def actions(self):  # type: () -> _ExecTotalStatsType
        """
        Action statistics.
        """
        from ._stats import ExecTotalStats

        _stats = ExecTotalStats()  # type: ExecTotalStats
        for _test_case_execution in self.test_case_executions:  # type: TestCaseExecution
            if _test_case_execution.scenario_execution:
                _stats.add(_test_case_execution.scenario_execution.action_stats)
        return _stats

    @property
    def results(self):  # type: () -> _ExecTotalStatsType
        """
        Expected result statistics.
        """
        from ._stats import ExecTotalStats

        _stats = ExecTotalStats()  # type: ExecTotalStats
        for _test_case_execution in self.test_case_executions:  # type: TestCaseExecution
            if _test_case_execution.scenario_execution:
                _stats.add(_test_case_execution.scenario_execution.result_stats)
        return _stats

    @property
    def counts(self):  # type: () -> CampaignStats
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
            script_path,  # type: typing.Optional[_AnyPathType]
    ):  # type: (...) -> None
        """
        :param test_suite_execution:
            Owner :class:`TestSuiteExecution` object.
        :param script_path:
            Scenario script path.

            ``None`` initializes the :attr:`script_path` member with a *void* file path.
            This path can be fixed programmatically later on.
        """
        from ._path import Path
        from ._stats import TimeStats

        #: Owner test suite execution.
        self.test_suite_execution = test_suite_execution  # type: TestSuiteExecution
        #: Scenario script path.
        self.script_path = Path(script_path)  # type: Path
        #: Time statistics.
        self.time = TimeStats()  # type: TimeStats
        #: Test case log output.
        self.log = LogFileReader()  # type: LogFileReader
        #: Test case report output.
        self.report = ReportFileReader()  # type: ReportFileReader

    def __repr__(self):  # type: () -> str
        """
        Canonical string representation.
        """
        from ._reflection import qualname

        return f"<{qualname(type(self))} of '{self.script_path}'>"

    @property
    def scenario_execution(self):  # type: () -> typing.Optional[_ScenarioExecutionType]
        """
        Scenario execution data.
        """
        if self.report.content:
            return self.report.content.execution
        return None

    @property
    def name(self):  # type: () -> str
        """
        Test case name.
        """
        if self.scenario_execution:
            return self.scenario_execution.definition.name
        else:
            # Use the script pretty path by default (base info to constitute the scenario name actually).
            return self.script_path.prettypath

    @property
    def status(self):  # type: () -> _ExecutionStatusType
        """
        Scenario execution status.
        """
        from ._executionstatus import ExecutionStatus

        if self.scenario_execution:
            return self.scenario_execution.status
        else:
            # FAIL by default.
            return ExecutionStatus.FAIL

    @property
    def errors(self):  # type: () -> typing.List[_TestErrorType]
        """
        Test errors.
        """
        if self.scenario_execution:
            return self.scenario_execution.errors
        return []

    @property
    def warnings(self):  # type: () -> typing.List[_TestErrorType]
        """
        Warnings.
        """
        if self.scenario_execution:
            return self.scenario_execution.warnings
        return []

    @property
    def steps(self):  # type: () -> _ExecTotalStatsType
        """
        Step statistics.
        """
        from ._stats import ExecTotalStats

        if self.scenario_execution:
            return self.scenario_execution.step_stats
        return ExecTotalStats()

    @property
    def actions(self):  # type: () -> _ExecTotalStatsType
        """
        Action statistics.
        """
        from ._stats import ExecTotalStats

        if self.scenario_execution:
            return self.scenario_execution.action_stats
        return ExecTotalStats()

    @property
    def results(self):  # type: () -> _ExecTotalStatsType
        """
        Expected result statistics.
        """
        from ._stats import ExecTotalStats

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
        self.path = None  # type: typing.Optional[_PathType]
        #: Test case log file content.
        self.content = None  # type: typing.Optional[bytes]

    def read(self):  # type: (...) -> bool
        """
        Read the log file.

        :return: ``True`` when the log file could be read successfully, ``False`` otherwise.
        """
        from ._loggermain import MAIN_LOGGER

        try:
            if self.path:
                self.content = self.path.read_bytes()
                return True
            else:
                MAIN_LOGGER.error("No log path to read")
        except Exception as _err:
            MAIN_LOGGER.error(f"Could not read log file '{self.path}': {_err}")
        return False


class ReportFileReader:
    """
    Scenario report file path and content.
    """

    def __init__(self):  # type: (...) -> None
        """
        Initializes :attr:`path` and :attr:`content` attributes with ``None``.
        """
        from ._scenariodefinition import ScenarioDefinition
        from ._path import Path

        #: Test case JSON file path.
        self.path = None  # type: typing.Optional[Path]
        #: Scenario execution data read from the test case JSON file.
        self.content = None  # type: typing.Optional[ScenarioDefinition]

    def read(self):  # type: (...) -> bool
        """
        Read the scenario report.

        :return: ``True`` when the scenario report file could be read and parsed successfully, ``False`` otherwise.
        """
        from ._loggermain import MAIN_LOGGER
        from ._scenarioreport import SCENARIO_REPORT

        if self.path:
            self.content = SCENARIO_REPORT.readscenarioreport(self.path, feed_reqdb=True)
        else:
            MAIN_LOGGER.error("No scenario report path to read")
        return self.content is not None
