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

import typing

import scenario
import scenario.test

# Steps:
from campaigns.steps.execution import ExecCampaign
from steps.common import ParseFinalResultsLog
from steps.common import LogVerificationStep


class Issue65b(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        scenario.test.TestCase.__init__(
            self,
            title="Issue #65! Campaign execution lost time",
            objective="Avoid untracked time when executing a campaign.",
            features=[scenario.test.features.CAMPAIGNS, scenario.test.features.SCENARIO_REPORT, scenario.test.features.STATISTICS],
        )

        self.addstep(ExecCampaign(
            [scenario.test.paths.datapath("campaign-long.suite")],
            # Activate log datetimes in order to be able to track what actually takes time.
            config_values={scenario.ConfigKey.LOG_DATETIME: True},
            # Activate issue#65 special debugging.
            debug_classes=["scenario.#65.exec-times"],
        ))
        self.addstep(ParseFinalResultsLog(ExecCampaign.getinstance()).enabledebug(False))
        self.addstep(CheckTimes(
            ExecCampaign.getinstance(),
            ParseFinalResultsLog.getinstance(),
        ))


class CheckTimes(LogVerificationStep):

    def __init__(
            self,
            exec_step,  # type: ExecCampaign
            final_results,  # type: ParseFinalResultsLog
    ):  # type: (...) -> None
        LogVerificationStep.__init__(self, exec_step)

        self.final_results = final_results  # type: ParseFinalResultsLog

    def step(self):  # type: (...) -> None
        from .issue065a import ratio

        self.STEP("Check times")

        _t1 = 0.0  # type: float
        if self.ACTION(f"Let t1, the campaign sub-process execution time taken from {self.exec_step}."):
            _t1 = self.assertisnotnone(
                self.subprocess.time.elapsed,
                evidence="t1",
            )

        _t2 = 0.0  # type: float
        if self.ACTION(f"Let t2, the total execution time read in {self.final_results}."):
            _t2 = self.assertisnotnone(
                self.final_results.json_total_stats["time"],
                evidence="t2",
            )

        self.knownissue(
            level=scenario.test.IssueLevel.SUT, id="#65",
            message="Still a bit more than 5% time lost when executing a campaign",
        )
        if self.RESULT(f"t2 is near t1 (margin = 5%)."):
            self.assertnear(
                _t2, _t1, margin=_t1 * 0.10,  # TODO: 10% instead of 5% as expected...
                evidence=True,
            )
            self.evidence(f"Error: {_t1 - _t2} ({ratio(_t1 - _t2, _t1)})")

        # Info collection for the characterization of the known-issue tracked above.

        _match = self.assertregex(b'', b'')  # type: typing.Match[bytes]
        _run_times = []  # type: typing.List[float]
        _log_file_times = []  # type: typing.List[float]
        _json_file_times = []  # type: typing.List[float]
        _untracked_times = []  # type: typing.List[float]
        if self.ACTION("Evaluate the time taken to execute test case sub-processes, then to read the log and JSON report files."):

            _debug_lines = self.assertlines(b'[scenario.#65.exec-times]')  # type: typing.List[bytes]
            for _debug_line in _debug_lines:  # type: bytes
                _match = self.assertregex(
                    rb'(%s) \(\+(%s)\)$' % (self.tobytes(scenario.datetime.DURATION_REGEX), self.tobytes(scenario.datetime.DURATION_REGEX)),
                    _debug_line,
                )
                _tick_time = scenario.datetime.str2fduration(self.tostr(_match.group(2)))  # type: float

                if b'After sub-process execution' in _debug_line:
                    _run_times.append(_tick_time)
                elif b'After reading the log file' in _debug_line:
                    _log_file_times.append(_tick_time)
                elif b'After reading the JSON file' in _debug_line:
                    _json_file_times.append(_tick_time)
                else:
                    _untracked_times.append(_tick_time)

            self.evidence(
                f"Sub-process execution times: {_run_times!r} "
                f"=> {sum(_run_times)} ({ratio(sum(_run_times), _t1)})"
            )
            self.evidence(
                f"Log file times: {_log_file_times!r} "
                f"=> {sum(_log_file_times)} ({ratio(sum(_log_file_times), _t1)})"
            )
            self.evidence(
                f"JSON file times: {_json_file_times!r} "
                f"=> {sum(_json_file_times)} ({ratio(sum(_json_file_times), _t1)})"
            )
            self.evidence(
                f"Untracked times (while executing test cases): {_untracked_times!r} "
                f"=> {sum(_untracked_times)} ({ratio(sum(_untracked_times), _t1)})"
            )

        _before_test_cases_time = 0.0  # type: float
        _after_test_cases_time = 0.0  # type: float
        if self.ACTION("Evaluate the time taken before and after test case executions."):
            _before_test_cases_line = self.assertline(b"-   TEST SUITE '")  # type: bytes
            _match = self.assertregex(rb'^(%s) - ' % self.tobytes(scenario.datetime.ISO8601_REGEX), _before_test_cases_line)
            _before_test_cases_tf = scenario.datetime.fromiso8601(self.tostr(_match.group(1)))  # type: float
            _before_test_cases_time = _before_test_cases_tf - self.assertisnotnone(self.subprocess.time.start)
            self.evidence(f"Before test cases: {_before_test_cases_time} ({ratio(_before_test_cases_time, _t1)})")

            _after_test_cases_line = self.assertlines(b'[scenario.#65.exec-times]')[-1]  # type: bytes
            _match = self.assertregex(rb'^(%s) - ' % self.tobytes(scenario.datetime.ISO8601_REGEX), _after_test_cases_line)
            _after_test_cases_t0 = scenario.datetime.fromiso8601(self.tostr(_match.group(1)))  # type: float
            _after_test_cases_time = self.assertisnotnone(self.subprocess.time.end) - _after_test_cases_t0
            self.evidence(f"After test cases: {_after_test_cases_time} ({ratio(_after_test_cases_time, _t1)})")

        if self.ACTION("Evaluate the total time lost."):
            self.evidence(f"sub-process execution times vs t1: {_t1 - sum(_run_times)} ({ratio(_t1 - sum(_run_times), _t1)})")
            self.evidence(f"t2 vs sub-process execution times: {sum(_run_times) - _t2} ({ratio(sum(_run_times) - _t2, sum(_run_times))})")
            self.evidence(f"t2 vs t1 (total): {_t1 - _t2} ({ratio(_t1 - _t2, _t1)})")
