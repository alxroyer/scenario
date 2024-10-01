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

The :class:`DebugClass` enum defines the `scenario` debug classes (see: :class:`._logger.Logger`).
"""

if True:
    from . import _enumutils as _enumutils  # @inheritance


class DebugClass(_enumutils.StrEnum):
    """
    `scenario` debug classes.
    """
    #: Program arguments debugging.
    ARGS = "scenario.Args"
    #: Campaign database debugging.
    CAMPAIGN_DB = "scenario.CampaignDatabase"
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
    #: Reflective programmation debugging.
    REFLECTION = "scenario.Reflection"
    #: Requirement database debugging.
    REQ_DATABASE = "scenario.ReqDatabase"
    #: Requirement management runner debugging.
    REQ_MANAGEMENT = "scenario.ReqManagement"
    #: Requirement traceability debugging.
    REQ_TRACEABILITY = "scenario.ReqTraceability"
    #: Scenario configuration debugging.
    SCENARIO_CONFIG = "scenario.ScenarioConfig"
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

    #: UI file delivery debugging.
    UI_FILE_DELIVERY = "scenario.ui.FileDelivery"
    #: UI HTML document debugging.
    UI_HTML_DOCUMENT = "scenario.ui.HtmlDocument"
    #: UI HTTP server debugging.
    UI_HTTP_SERVER = "scenario.ui.HttpServer"
    #: UI campaign page debugging.
    UI_PAGE_CAMPAIGN = "scenario.ui.CampaignPage"
    #: UI campaign list page debugging.
    UI_PAGE_CAMPAIGNS = "scenario.ui.CampaignListPage"
    #: UI configuration page debugging.
    UI_PAGE_CONFIG = "scenario.ui.ConfigurationPage"
    #: UI homepage debugging.
    UI_PAGE_HOME = "scenario.ui.Homepage"
    #: UI requirements page debugging.
    UI_PAGE_REQS = "scenario.ui.RequirementsPage"
    #: UI downstream traceability page debugging.
    UI_PAGE_REQS_DOWN = "scenario.ui.DownstreamTraceabilityPage"
    #: UI upstream traceability page debugging.
    UI_PAGE_REQS_UP = "scenario.ui.UpstreamTraceabilityPage"
    #: UI scenario page debugging.
    UI_PAGE_SCENARIO = "scenario.ui.ScenarioPage"
    #: UI scenario list page debugging.
    UI_PAGE_SCENARIOS = "scenario.ui.ScenarioListPage"
