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

import os
import typing

import scenario
import scenario.test
import scenario.text

from steps.common import LogVerificationStep  # `LogVerificationStep` used for inheritance.
if typing.TYPE_CHECKING:
    from campaigns.steps.execution import ExecCampaign as _ExecCampaignType


class Issue46(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from campaigns.steps.execution import ExecCampaign

        scenario.test.TestCase.__init__(
            self,
            title="Issue #46! Campaign halts on errors",
            objective="Check that a campaign does not halt on errors due the scenario scripts being tested.",
            features=[scenario.test.features.CAMPAIGNS, scenario.test.features.ERROR_HANDLING],
        )

        # Campaign execution.
        self.addstep(ExecCampaign([scenario.test.paths.datapath("campaign-errors.suite")]))

        # Error message verifications.
        self.addstep(CheckErrorDisplay(ExecCampaign.getinstance(), scenario.test.paths.SYNTAX_ERROR_SCENARIO, {
            f"File \"{os.fspath(scenario.test.paths.SYNTAX_ERROR_SCENARIO)}\", line 31": 2,  # location: SYNTAX_ERROR_SCENARIO/syntax-error
            "SyntaxError: invalid syntax": 2,
        }))
        self.addstep(CheckErrorDisplay(ExecCampaign.getinstance(), scenario.test.paths.MISSING_SCENARIO_CLASS_SCENARIO, {
            f"LookupError: Could not find scenario class in '{scenario.test.paths.MISSING_SCENARIO_CLASS_SCENARIO}'": 2,
        }))
        self.addstep(CheckErrorDisplay(ExecCampaign.getinstance(), scenario.test.paths.NO_SUCH_FILE_SCENARIO, {
            f"No such file '{scenario.test.paths.NO_SUCH_FILE_SCENARIO}'": 2,
        }))


class CheckErrorDisplay(LogVerificationStep):

    def __init__(
            self,
            exec_step,  # type: _ExecCampaignType
            script_path,  # type: scenario.Path
            error_messages,  # type: typing.Dict[str, int]
    ):  # type: (...) -> None
        LogVerificationStep.__init__(self, exec_step)

        self.script_path = script_path  # type: scenario.Path
        self.error_messages = error_messages  # type: typing.Dict[str, int]

    def step(self):  # type: (...) -> None
        self.STEP(f"'{self.script_path}' error messages")

        for _error_message in self.error_messages:  # type: str
            _count = self.error_messages[_error_message]  # type: int
            if self.RESULT(f"The {_error_message!r} error message is displayed {scenario.text.adverbial(_count)} in the campaign log output."):
                self.assertlinecount(
                    _error_message, _count,
                    evidence=f"'{self.script_path}' error message",
                )
