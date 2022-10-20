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
        self.STEP("'%s' logger logging" % LoggerScenario.LOGGER_DEBUG_CLASS)

        if self.ACTION("Generate an error line with the '%s' logger." % LoggerScenario.LOGGER_DEBUG_CLASS):
            self.sample_logger.error("'%s' logger error line" % LoggerScenario.LOGGER_DEBUG_CLASS)
        if self.ACTION("Generate a warning line with the '%s' logger." % LoggerScenario.LOGGER_DEBUG_CLASS):
            self.sample_logger.warning("'%s' logger warning line" % LoggerScenario.LOGGER_DEBUG_CLASS)
        if self.ACTION("Generate an info line with the '%s' logger." % LoggerScenario.LOGGER_DEBUG_CLASS):
            self.sample_logger.info("'%s' logger info line" % LoggerScenario.LOGGER_DEBUG_CLASS)
        if self.ACTION("Generate a debug line with the '%s' logger." % LoggerScenario.LOGGER_DEBUG_CLASS):
            self.sample_logger.debug("'%s' logger debug line" % LoggerScenario.LOGGER_DEBUG_CLASS)
