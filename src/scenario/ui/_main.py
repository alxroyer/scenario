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
User interface launching.
"""

import sys

import scenario


def main():  # type: (...) -> scenario.ErrorCode
    """
    User interface launcher function.

    :return: Error code.
    """
    from ._args import UIArgs
    from ._httpserver import HTTP_SERVER
    from ._reqbl import UI_REQ_BASELINES

    # Analyze program arguments, if not already set.
    if not UIArgs.isset():
        UIArgs.setinstance(UIArgs())
        if not UIArgs.getinstance().parse(sys.argv[1:]):
            return UIArgs.getinstance().error_code

    # Start log features.
    scenario.logging_service.start()

    try:
        # Load default requirements and scenarios from `ScenarioConfig.Key.REQ_DB_FILES` and `TEST_SUITE_FILES` configurations.
        UI_REQ_BASELINES.main = scenario.ReqBaseline.fromfiles(
            name="scenario.ui",
            log_info=True,
        )
        # Load campaign results.
        scenario.campaign_db.load(
            # Don't read scenario logs and reports right now for performance concerns.
            # They will be read later if needed.
            read_scenario_logs=False,
            read_scenario_reports=False,
            log_info=True,
        )

        # Launch the HTTP server.
        scenario.logging.info("")
        HTTP_SERVER.serve()
    except Exception as _err:
        scenario.logging.logexceptiontraceback(_err)
        return scenario.ErrorCode.fromexception(_err)

    # Terminate log features.
    scenario.logging_service.stop()

    return scenario.ErrorCode.SUCCESS
