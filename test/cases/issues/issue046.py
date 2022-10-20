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

import os
import typing

import scenario
import scenario.test

# Steps:
from campaigns.steps.execution import ExecCampaign
from steps.common import LogVerificationStep


class Issue46(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
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
            "File \"%s\", line 31" % os.fspath(scenario.test.paths.SYNTAX_ERROR_SCENARIO): 2,  # location: SYNTAX_ERROR_SCENARIO/syntax-error
            "SyntaxError: invalid syntax": 2,
        }))
        self.addstep(CheckErrorDisplay(ExecCampaign.getinstance(), scenario.test.paths.MISSING_SCENARIO_CLASS_SCENARIO, {
            "LookupError: Could not find scenario class in '%s'" % scenario.test.paths.MISSING_SCENARIO_CLASS_SCENARIO: 2,
        }))
        self.addstep(CheckErrorDisplay(ExecCampaign.getinstance(), scenario.test.paths.NO_SUCH_FILE_SCENARIO, {
            "No such file '%s'" % scenario.test.paths.NO_SUCH_FILE_SCENARIO: 2,
        }))


class CheckErrorDisplay(LogVerificationStep):

    def __init__(
            self,
            exec_step,  # type: ExecCampaign
            script_path,  # type: scenario.Path
            error_messages,  # type: typing.Dict[str, int]
    ):  # type: (...) -> None
        LogVerificationStep.__init__(self, exec_step)

        self.script_path = script_path  # type: scenario.Path
        self.error_messages = error_messages  # type: typing.Dict[str, int]

    def step(self):  # type: (...) -> None
        self.STEP("'%s' error messages" % self.script_path)

        for _error_message in self.error_messages:  # type: str
            _count = self.error_messages[_error_message]  # type: int
            if self.RESULT("The %s error message is displayed %d time(s) in the campaign log output." % (repr(_error_message), _count)):
                self.assertlinecount(
                    _error_message, _count,
                    evidence="'%s' error message" % self.script_path,
                )
