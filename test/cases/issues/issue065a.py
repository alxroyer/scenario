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

import abc
import typing

import scenario
import scenario.test

if True:
    from steps.common import LogVerificationStep as _LogVerificationStepImpl  # `LogVerificationStep` used for inheritance.
if typing.TYPE_CHECKING:
    from steps.common import ExecScenario as _ExecScenarioType
    from steps.common import ParseScenarioLog as _ParseScenarioLogType


class Issue65a(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from steps.common import ExecScenario, ParseScenarioLog

        scenario.test.TestCase.__init__(
            self,
            title="Issue #65! Scenario execution lost time",
            description="Avoid untracked time when executing a scenario.",
        )
        self.covers(
            scenario.test.reqs.STATISTICS,
        )

        self.addstep(ExecScenario(
            scenario.test.paths.WAITING_SCENARIO,
            # Activate log datetimes in order to be able to track what actually takes time.
            config_values={scenario.ConfigKey.LOG_DATETIME: True},
            # Activate issue#65 special debugging.
            debug_classes=["scenario.#65.exec-times"],
        ))
        self.addstep(ParseScenarioLog(ExecScenario.getinstance()).enabledebug(False))
        self.addstep(CheckTimes(ExecScenario.getinstance(), ParseScenarioLog.getinstance()))


class CheckTimeLostStep(_LogVerificationStepImpl, abc.ABC):
    """
    Memo: This abstract step inherits from ``LogVerificationStep`` for the needs of 'issue065b.py'.
    """

    # Say we expect that only up to 1% mount of time shall be lost between the actual time elapsed and the time reported.
    TIME_LOST_TOLERANCE = 0.01  # type: float

    @staticmethod
    def ratio(
            time,  # type: float
            ref_time,  # type: float
    ):  # type: (...) -> str
        return f"{time / ref_time * 100.0:.2f}%"

    def assertlittletimelost(
            self,
            actual,  # type: float
            reported,  # type: float
            execution_object,  # type: str
            tolerance=TIME_LOST_TOLERANCE,  # type: float
            evidence=False,  # type: bool
    ):  # type: (...) -> None
        _lost = actual - reported  # type: float
        try:
            # First, check with the given tolerance.
            self.assertless(tolerance, 0.10, f"Invalid tolerance {tolerance!r}")
            self.assertnear(
                reported, actual, margin=actual * tolerance,
                evidence=evidence,
            )
        except AssertionError:
            # On failure, try with a 10% tolerance.
            self.assertnear(
                reported, actual, margin=actual * 0.10,
                evidence=evidence,
            )
            # If the assertion above succeeded, track a known-issue.
            self.knownissue(
                level=scenario.test.IssueLevel.SUT, id="#65",
                message=f"More than {int(tolerance * 100)}% time lost when executing {execution_object} ({self.ratio(_lost, actual)})",
            )
        # Eventually track detailed info about the time lost.
        if evidence:
            self.evidence(f"Time lost: {_lost:.3f} seconds ({self.ratio(_lost, actual)})")


class CheckTimes(CheckTimeLostStep):

    def __init__(
            self,
            exec_step,  # type: _ExecScenarioType
            scenario_logs,  # type: _ParseScenarioLogType
    ):  # type: (...) -> None
        CheckTimeLostStep.__init__(self, exec_step)

        self.scenario_logs = scenario_logs  # type: _ParseScenarioLogType

    def step(self):  # type: (...) -> None
        self.STEP("Check times")

        _t1 = 0.0  # type: float
        if self.ACTION(f"Let t1, the actual scenario sub-process execution time taken from {self.exec_step}."):
            _t1 = self.assertisnotnone(
                self.subprocess.time.elapsed,
                evidence="t1",
            )

        _t2 = 0.0  # type: float
        if self.ACTION(f"Let t2, the reported total execution time read in {self.scenario_logs}."):
            _t2 = self.assertisnotnone(
                self.scenario_logs.json_main_scenario["time"]["elapsed"],
                evidence="t2",
            )

        if self.RESULT(f"t2 is near t1 (margin = {int(self.TIME_LOST_TOLERANCE * 100)}%)."):
            self.assertlittletimelost(
                actual=_t1, reported=_t2, tolerance=self.TIME_LOST_TOLERANCE,
                execution_object="a scenario", evidence=True,
            )
