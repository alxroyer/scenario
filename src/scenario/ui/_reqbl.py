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
Main requirement baseline storage for :mod:`scenario.ui`.
"""

import typing

import scenario


class UIReqBaselines(scenario.Logger):
    """
    Main requirement baseline storage.

    Instantiated once with the :data:`UI_REQ_BASELINES` singleton.
    """

    def __init__(self):  # type: (...) -> None
        """
        Simple initialization of a :class:`scenario._reqblobj.ReqBaselineObject`,
        without requirement baseline at first.
        """
        from ._debugclasses import UIDebugClass

        scenario.Logger.__init__(self, UIDebugClass.REQ_BASELINES)

        #: Main requirement baseline.
        self._main = None  # type: typing.Optional[scenario.ReqBaseline]

    @property
    def main(self):  # type: () -> scenario.ReqBaseline
        """
        Main requirement baseline.

        :raise ValueError: If not set yet.
        """
        if self._main is None:
            raise ValueError("Main baseline not set yet")
        return self._main

    @main.setter
    def main(self, req_baseline):  # type: (scenario.ReqBaseline) -> None
        """
        Sets the main requirement baseline.

        :param req_baseline: Main requirement baseline.
        """
        self._main = req_baseline

    def getdesc(
            self,
            req_baseline,  # type: scenario.ReqBaseline
    ):  # type: (...) -> str
        """
        Computes a textual desription for the given baseline.

        :param req_baseline: Baseline to compute a description for.
        :return: Empty string for the main baseline, baseline name otherwise.
        """
        if req_baseline is self._main:
            return ""
        else:
            return req_baseline.name

    def checkscenarioloaded(
            self,
            scenario_definition,  # type: scenario.ScenarioDefinition
    ):  # type: (...) -> None
        """
        Ensures the given scenario definition to be loaded.

        :param scenario_definition:
            Scenario definition to ensure content for:

            - title,
            - scenario attributes,
            - steps with actions and expected results,
            - traceability,
            - ...

        Used for scenarios of the :attr:`main` baseline, to be read from Python scripts.
        Called by :meth:`._pagescenario.ScenarioPage._getscenario()`.
        """
        # Once the scenario definition has been loaded, a `ScenarioExecution` instance is attached with it.
        # If the scenario definition does not own its `ScenarioExecution` instance yet, try to load it.
        if not scenario_definition.execution:
            if scenario_definition.req_baseline is not self.main:
                raise Exception(f"Unexpected unloaded scenario for non-main baseline {scenario_definition.req_baseline!r}")

            # Load scenario details.
            try:
                # Prepare the scenario for working with `ScenarioRunner` and `ScenarioStack`.
                scenario_definition.execution = scenario.ScenarioExecution(scenario_definition)
                scenario.stack.building.pushscenariodefinition(scenario_definition)

                # Start iterating over the scenario steps.
                scenario_definition.execution.startsteplist()
                while scenario_definition.execution.current_step_definition:
                    # Execute the step in *building* mode.
                    scenario_definition.execution.current_step_definition.step()

                    # Switch to the next step.
                    scenario_definition.execution.nextstep()
            finally:
                scenario.stack.building.popscenariodefinition(scenario_definition)
        else:
            self.debug("%r: Test case %r already loaded", self.main, scenario_definition)

    def checkcampaignloaded(
            self,
            campaign_execution,  # type: scenario.CampaignExecution
    ):  # type: (...) -> None
        """
        Ensures all test cases of the given campaign are fully loaded.

        :param campaign_execution: Campaign to ensure scenario definitions and executions are loaded for all test cases.
        """
        for _test_suite_execution in campaign_execution.test_suite_executions:  # type: scenario.TestSuiteExecution
            for _test_case_execution in _test_suite_execution.test_case_executions:  # type: scenario.TestCaseExecution
                self.checktestcaseloaded(_test_case_execution)

    def checktestcaseloaded(
            self,
            test_case_execution,  # type: scenario.TestCaseExecution
    ):  # type: (...) -> None
        """
        Ensures a campaign test case is fully loaded.

        :param test_case_execution: Test case to load scenario definition and execution.
        """
        if not test_case_execution.report.content:
            if not test_case_execution.report.path:
                self.debug("%r: No scenario report path for test case %r", test_case_execution.req_baseline, test_case_execution)
            elif not test_case_execution.report.path.is_file():
                self.debug("%r: No such scenario report '%s'", test_case_execution.req_baseline, test_case_execution.report.path)
            else:
                try:
                    self.debug("%r: Reading '%s'", test_case_execution.req_baseline, test_case_execution.report.path)
                    test_case_execution.report.read()
                    if test_case_execution.scenario_definition:
                        test_case_execution.req_baseline.scenarios.append(test_case_execution.scenario_definition)
                except Exception as _err:
                    self.warning("%r: Error while reading '%s': %r", test_case_execution.req_baseline, test_case_execution.report.path, _err)
        else:
            self.debug("%r: Test case %r already loaded", test_case_execution.req_baseline, test_case_execution)


#: Main instance of :class:`UIReqBaselines`.
UI_REQ_BASELINES = UIReqBaselines()  # type: UIReqBaselines
