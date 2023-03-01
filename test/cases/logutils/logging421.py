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

import scenario
from scenario.scenariologging import ScenarioLogging
import scenario.test

# Steps:
from .logging420 import ExecUserIndentation, CheckUserIndentation


class Logging421(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        scenario.test.TestCase.__init__(
            self,
            title="Additional user indentation in subscenario",
            objective="Check that additional user indentation still works in subscenarios.",
            features=[scenario.test.features.LOGGING, scenario.test.features.SUBSCENARIOS],
        )

        self.addstep(ExecUserIndentation(
            scenario.test.paths.SUPERSCENARIO_SCENARIO, subscenario=scenario.test.paths.LOGGING_INDENTATION_SCENARIO,
            scenario_stack_indentation=ScenarioLogging.SCENARIO_STACK_INDENTATION_PATTERN,
        ))
        self.addstep(CheckUserIndentation(ExecUserIndentation.getinstance()))


