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

import scenario.test

if True:
    from steps.logverifications import LogVerificationStep as _LogVerificationStepImpl  # `LogVerificationStep` used for inheritance.


class CheckConfigValueScenarioLog(_LogVerificationStepImpl):

    def __init__(
            self,
            exec_step,  # type: scenario.test.AnyExecutionStepType
            key,  # type: str
            origin,  # type: str
            value,  # type: str
    ):  # type: (...) -> None
        _LogVerificationStepImpl.__init__(self, exec_step)

        self.key = key  # type: str
        self.origin = origin  # type: str
        self.value = value  # type: str

    def step(self):  # type: (...) -> None
        self.STEP("Configuration value verification")

        if self.RESULT(f"{self.value!r} is read for the '{self.key}' configuration value with '{self.origin}' for origin."):
            self.assertline(
                f"{self.key} ({self.origin}): {self.value}",
                evidence=True,
            )
