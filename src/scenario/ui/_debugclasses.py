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
`scenario.ui` debugging.

The :class:`UIDebugClass` enum defines the `scenario.ui` debug classes (see: :class:`scenario._logger.Logger`).
"""

import scenario


class UIDebugClass(scenario.enum.StrEnum):
    """
    `scenario.ui` debug classes.
    """
    #: UI configuration database debugging.
    CONFIG_DB = "scenario.ui.UIConfig"
    #: UI file delivery debugging.
    FILE_DELIVERY = "scenario.ui.FileDelivery"
    #: UI HTML document debugging.
    HTML_DOCUMENT = "scenario.ui.HtmlDocument"
    #: UI HTTP server debugging.
    HTTP_SERVER = "scenario.ui.HttpServer"
    #: UI campaign page debugging.
    PAGE_CAMPAIGN = "scenario.ui.CampaignPage"
    #: UI campaign list page debugging.
    PAGE_CAMPAIGNS = "scenario.ui.CampaignListPage"
    #: UI configuration page debugging.
    PAGE_CONFIG = "scenario.ui.ConfigurationPage"
    #: UI homepage debugging.
    PAGE_HOME = "scenario.ui.Homepage"
    #: UI requirements page debugging.
    PAGE_REQS = "scenario.ui.RequirementsPage"
    #: UI downstream traceability page debugging.
    PAGE_REQS_DOWN = "scenario.ui.DownstreamTraceabilityPage"
    #: UI upstream traceability page debugging.
    PAGE_REQS_UP = "scenario.ui.UpstreamTraceabilityPage"
    #: UI scenario page debugging.
    PAGE_SCENARIO = "scenario.ui.ScenarioPage"
    #: UI scenario list page debugging.
    PAGE_SCENARIOS = "scenario.ui.ScenarioListPage"
    #: UI requirement baselines debugging.
    REQ_BASELINES = "scenario.ui.UIReqBaselines"
