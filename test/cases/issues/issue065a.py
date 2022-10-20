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

import scenario
import scenario.test

# Steps:
from steps.common import ExecScenario
from steps.common import ParseScenarioLog


class Issue65a(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        scenario.test.TestCase.__init__(
            self,
            title="Issue #65! Scenario execution lost time",
            objective="Avoid untracked time when executing a scenario.",
            features=[scenario.test.features.STATISTICS],
        )

        self.addstep(ExecScenario(
            scenario.test.paths.WAITING_SCENARIO,
            # Activate log datetimes in order to be able to track what actually takes time.
            config_values={scenario.ConfigKey.LOG_DATETIME: "1"},
            # Activate issue#65 special debugging.
            debug_classes=["scenario.#65.exec-times"],
        ))
        self.addstep(ParseScenarioLog(ExecScenario.getinstance()).enabledebug(False))
        self.addstep(CheckTimes(ExecScenario.getinstance(), ParseScenarioLog.getinstance()))


def ratio(
        time,  # type: float
        ref_time,  # type: float
):  # type: (...) -> str
    return f"{time / ref_time * 100.0:.2f}%"


class CheckTimes(scenario.test.VerificationStep):

    def __init__(
            self,
            exec_step,  # type: ExecScenario
            scenario_logs,  # type: ParseScenarioLog
    ):  # type: (...) -> None
        scenario.test.VerificationStep.__init__(self, exec_step)

        self.scenario_logs = scenario_logs  # type: ParseScenarioLog

    def step(self):  # type: (...) -> None
        self.STEP("Check times")

        _t1 = 0.0  # type: float
        if self.ACTION(f"Let t1, the scenario sub-process execution time taken from {self.exec_step}."):
            _t1 = self.assertisnotnone(
                self.subprocess.time.elapsed,
                evidence="t1",
            )

        _t2 = 0.0  # type: float
        if self.ACTION(f"Let t2, the total execution time read in {self.scenario_logs}."):
            _t2 = self.assertisnotnone(
                self.scenario_logs.json_main_scenario["time"]["elapsed"],
                evidence="t2",
            )

        if self.RESULT(f"t2 is near t1 (margin = 5%)."):
            self.assertnear(
                _t2, _t1, margin=_t1 * 0.05,
                evidence=True,
            )
            self.evidence(f"Error: {_t1 - _t2} ({ratio(_t1 - _t2, _t1)})")
