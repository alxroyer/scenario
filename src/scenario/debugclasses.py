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
`scenario` debugging.

The :class:`DebugClass` enum defines the `scenario` debug classes (see: :class:`.logger.Logger`).
"""

from .enumutils import StrEnum  # `StrEnum` used for inheritance.


class DebugClass(StrEnum):
    """
    `scenario` debug classes.
    """
    #: Program arguments debugging.
    ARGS = "scenario.Args"
    #: Campaign report debugging.
    CAMPAIGN_REPORT = "scenario.CampaignReport"
    #: Campaign runner debugging.
    CAMPAIGN_RUNNER = "scenario.CampaignRunner"
    #: Configuration database debugging.
    CONFIG_DATABASE = "scenario.ConfigDatabase"
    #: Execution location debugging.
    EXECUTION_LOCATIONS = "scenario.ExecutionLocations"
    #: Handlers.
    HANDLERS = "scenario.Handlers"
    #: Logging statistics.
    LOG_STATS = "scenario.LogStats"
    #: Reflexive programmation debugging.
    REFLEX = "scenario.reflex"
    #: Scenario report debugging.
    SCENARIO_REPORT = "scenario.ScenarioReport"
    #: Scenario results debugging.
    SCENARIO_RESULTS = "scenario.ScenarioResults"
    #: Scenario runner debugging.
    SCENARIO_RUNNER = "scenario.ScenarioRunner"
    #: Scenario stack debugging.
    SCENARIO_STACK = "scenario.ScenarioStack"
    #: Test suite file debugging.
    TEST_SUITE_FILE = "scenario.TestSuiteFile"

    #: Issue#65 debugging: execution times.
    EXECUTION_TIMES = "scenario.#65.exec-times"
