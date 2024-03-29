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


class LoggerScenario(scenario.Scenario):

    LOGGER_DEBUG_CLASS = "sample-log"  # type: str

    def __init__(self):  # type: (...) -> None
        scenario.Scenario.__init__(self)

        self.setattribute("TITLE", "Logger scenario sample")

        self.sample_logger = scenario.Logger(log_class=LoggerScenario.LOGGER_DEBUG_CLASS)
        self.sample_logger.setlogcolor(scenario.Console.Color.LIGHTBLUE36)

    def step110(self):  # type: (...) -> None
        self.STEP("Main logger logging")

        if self.ACTION("Generate an error line with the main logger."):
            scenario.logging.error("Main logger error line")
        if self.ACTION("Generate a warning line with the main logger."):
            scenario.logging.warning("Main logger warning line")
        if self.ACTION("Generate an info line with the main logger."):
            scenario.logging.info("Main logger info line")
        if self.ACTION("Generate a debug line with the main logger."):
            scenario.logging.debug("Main logger debug line")

    def step120(self):  # type: (...) -> None
        self.STEP(f"'{LoggerScenario.LOGGER_DEBUG_CLASS}' logger logging")

        if self.ACTION(f"Generate an error line with the '{LoggerScenario.LOGGER_DEBUG_CLASS}' logger."):
            self.sample_logger.error(f"'{LoggerScenario.LOGGER_DEBUG_CLASS}' logger error line")
        if self.ACTION(f"Generate a warning line with the '{LoggerScenario.LOGGER_DEBUG_CLASS}' logger."):
            self.sample_logger.warning(f"'{LoggerScenario.LOGGER_DEBUG_CLASS}' logger warning line")
        if self.ACTION(f"Generate an info line with the '{LoggerScenario.LOGGER_DEBUG_CLASS}' logger."):
            self.sample_logger.info(f"'{LoggerScenario.LOGGER_DEBUG_CLASS}' logger info line")
        if self.ACTION(f"Generate a debug line with the '{LoggerScenario.LOGGER_DEBUG_CLASS}' logger."):
            self.sample_logger.debug(f"'{LoggerScenario.LOGGER_DEBUG_CLASS}' logger debug line")
