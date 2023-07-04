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


class LoggingIndentationScenario(scenario.Scenario):

    def __init__(self):  # type: (...) -> None
        scenario.Scenario.__init__(
            self,
            title="Logging indentation scenario sample",
        )

    def step200(self):  # type: (...) -> None
        self.STEP("Logging indentation")

        if self.ACTION("#0: Log something with the main logger."):
            scenario.logging.info("#0: Main logger info line")
        if self.ACTION("#0: Log something with this scenario logger."):
            self.info("#0: Class logger info line")
        if self.ACTION("#0: Display an evidence line."):
            self.evidence("#0: Evidence.")

        if self.ACTION("#1: Add indentation with this scenario class logger."):
            self.pushindentation()
        if self.ACTION("#1: Log something with the main logger."):
            scenario.logging.info("#1: Main logger info line")
        if self.ACTION("#1: Log something with this scenario logger."):
            self.info("#1: Class logger info line")
        if self.ACTION("#1: Display an evidence line."):
            self.evidence("#1: Evidence.")

        if self.ACTION("#2: Add indentation with this scenario class logger again."):
            self.pushindentation()
        if self.ACTION("#2: Log something with the main logger."):
            scenario.logging.info("#2: Main logger info line")
        if self.ACTION("#2: Log something with this scenario logger."):
            self.info("#2: Class logger info line")
        if self.ACTION("#2: Display an evidence line."):
            self.evidence("#2: Evidence.")

        if self.ACTION("#3: Add indentation with the main logger."):
            scenario.logging.pushindentation()
        if self.ACTION("#3: Log something with the main logger."):
            scenario.logging.info("#3: Main logger info line")
        if self.ACTION("#3: Log something with this scenario logger."):
            self.info("#3: Class-logger info line")
        if self.ACTION("#3: Display an evidence line."):
            self.evidence("#3: Evidence.")

        if self.ACTION("#4: Add indentation with the main logger again."):
            scenario.logging.pushindentation()
        if self.ACTION("#4: Log something with the main logger."):
            scenario.logging.info("#4: Main logger info line")
        if self.ACTION("#4: Log something with this scenario logger."):
            self.info("#4: Class-logger info line")
        if self.ACTION("#4: Display an evidence line."):
            self.evidence("#4: Evidence.")

        if self.ACTION("#5: Remove indentation with this scenario class logger."):
            self.popindentation()
        if self.ACTION("#5: Log something with the main logger."):
            scenario.logging.info("#5: Main logger info line")
        if self.ACTION("#5: Log something with this scenario logger."):
            self.info("#5: Class-logger info line")
        if self.ACTION("#5: Display an evidence line."):
            self.evidence("#5: Evidence")

        if self.ACTION("#6: Reset indentation with the main logger."):
            scenario.logging.resetindentation()
        if self.ACTION("#6: Log something with the main logger."):
            scenario.logging.info("#6: Main logger info line")
        if self.ACTION("#6: Log something with this scenario logger."):
            self.info("#6: Class-logger info line")
        if self.ACTION("#6: Display an evidence line."):
            self.evidence("#6: Evidence")

        if self.ACTION("#7: Reset indentation with this scenario class logger."):
            self.resetindentation()
        if self.ACTION("#7: Log something with the main logger."):
            scenario.logging.info("#7: Main logger info line")
        if self.ACTION("#7: Log something with this scenario logger."):
            self.info("#7: Class-logger info line")
        if self.ACTION("#7: Display an evidence line."):
            self.evidence("#7: Evidence")
