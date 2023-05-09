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


class Logging210(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from logutils.logging200 import CheckClassLoggerLogLevels
        from steps.common import ExecScenario

        scenario.test.TestCase.__init__(
            self,
            title="Class logger debugging enabling",
            objective="Check that debugging is disabled by default for class loggers, and that it can be enabled.",
            features=[scenario.test.features.DEBUG_LOGGING],
        )

        self.section("Default behaviour")
        self.addstep(ExecScenario(
            scenario.test.paths.LOGGER_SCENARIO,
            # 'sample-log' debugging by default.
            debug_classes=[],
            # Explicitely disable log date/time for verification purposes in `CheckClassLoggerLogLevels`.
            config_values={scenario.ConfigKey.LOG_DATETIME: False},
        ))
        self.addstep(CheckClassLoggerLogLevels(ExecScenario.getinstance(0)))

        self.section("Class logger debugging activated")
        self.addstep(ExecScenario(
            scenario.test.paths.LOGGER_SCENARIO,
            # 'sample-log' explicitly not activated.
            debug_classes=[scenario.test.data.scenarios.LoggerScenario.LOGGER_DEBUG_CLASS],
            # Explicitely disable log date/time for verification purposes in `CheckClassLoggerLogLevels`.
            config_values={scenario.ConfigKey.LOG_DATETIME: False},
        ))
        self.addstep(CheckClassLoggerLogLevels(ExecScenario.getinstance(1)))
