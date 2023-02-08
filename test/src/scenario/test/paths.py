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


# Directories.
MAIN_PATH = scenario.Path(__file__).parents[4]  # type: scenario.Path
DEMO_PATH = MAIN_PATH / "demo"  # type: scenario.Path
DATA_PATH = MAIN_PATH / "test" / "data"  # type: scenario.Path
UNIT_TESTS_PATH = MAIN_PATH / "test" / "cases"  # type: scenario.Path
UNIT_RESULTS_PATH = MAIN_PATH / "test" / "results"  # type: scenario.Path

# Launchers.
TEST_LAUNCHER = MAIN_PATH / "bin" / "run-test.py"  # type: scenario.Path
CAMPAIGN_LAUNCHER = MAIN_PATH / "bin" / "run-campaign.py"  # type: scenario.Path
UNIT_TEST_LAUNCHER = MAIN_PATH / "test" / "run-unit-test.py"  # type: scenario.Path
UNIT_CAMPAIGN_LAUNCHER = MAIN_PATH / "test" / "run-unit-campaign.py"  # type: scenario.Path

# Data scenarios.
ACTION_RESULT_LOOP_SCENARIO = DATA_PATH / "actionresultloopscenario.py"  # type: scenario.Path
CONFIG_DB_SCENARIO = DATA_PATH / "configdbscenario.py"  # type: scenario.Path
FAILING_SCENARIO = DATA_PATH / "failingscenario.py"  # type: scenario.Path
GOTO_SCENARIO = DATA_PATH / "gotoscenario.py"  # type: scenario.Path
INHERITING_SCENARIO = DATA_PATH / "inheritingscenario.py"  # type: scenario.Path
KNOWN_ISSUE_DETAILS_SCENARIO = DATA_PATH / "knownissuedetailsscenario.py"  # type: scenario.Path
KNOWN_ISSUES_SCENARIO = DATA_PATH / "knownissuesscenario.py"  # type: scenario.Path
LOGGER_SCENARIO = DATA_PATH / "loggerscenario.py"  # type: scenario.Path
LOGGING_INDENTATION_SCENARIO = DATA_PATH / "loggingindentationscenario.py"  # type: scenario.Path
MISSING_SCENARIO_CLASS_SCENARIO = DATA_PATH / "errors" / "missingscenarioclassscenario.py"  # type: scenario.Path
NO_SUCH_FILE_SCENARIO = DATA_PATH / "errors" / "nosuchfilescenario.py"  # type: scenario.Path
PACKAGE_SCENARIO = DATA_PATH / "xyz" / "packagescenario.py"  # type: scenario.Path
SCENARIO_LOGGING_SCENARIO = DATA_PATH / "scenariologgingscenario.py"  # type: scenario.Path
SIMPLE_SCENARIO = DATA_PATH / "simplescenario.py"  # type: scenario.Path
SUPERSCENARIO_SCENARIO = DATA_PATH / "superscenario.py"  # type: scenario.Path
SYNTAX_ERROR_SCENARIO = DATA_PATH / "errors" / "syntaxerrorscenario.py"  # type: scenario.Path
WAITING_SCENARIO = DATA_PATH / "waitingscenario.py"  # type: scenario.Path

DEMO_TEST_SUITE = DEMO_PATH / "demo.suite"  # type: scenario.Path
TEST_DATA_TEST_SUITE = DATA_PATH / "test-data.suite"  # type: scenario.Path


def datapath(
        basename,  # type: str
):  # type: (...) -> scenario.Path
    return DATA_PATH / basename
