#!/usr/bin/env python
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

import pathlib
import sys
import typing

# Path management.
_root_scenario_path = pathlib.Path(__file__).parents[1].resolve()  # type: pathlib.Path
sys.path.append(str(_root_scenario_path / "src"))
sys.path.append(str(_root_scenario_path / "test" / "cases"))
sys.path.append(str(_root_scenario_path / "test" / "src"))

if True:
    import scenario  # @after-path-management
    import scenario.reqs  # @after-path-management
    import scenario.test  # @after-path-management


# Command line arguments.
class ScenarioCampaignArgs(scenario.CampaignArgs):

    def __init__(self):  # type: (...) -> None
        scenario.CampaignArgs.__init__(self)
        self.setdescription("Scenario tests campaign launcher.")

    def _checkargs(
            self,
            args,  # type: typing.Any
    ):  # type: (...) -> bool
        if not self.outdir:
            self.debug("Using --dt-subdir option by default")
            self.create_dt_subdir = True

        if not super()._checkargs(args):
            return False

        return True


if __name__ == "__main__":
    from scenario._scenarioconfig import SCENARIO_CONFIG  # noqa  ## Access to protected module

    # General configurations:
    # - Have the neighbour `SCENARIO_TEST_LAUNCHER` script be used as the scenario runner script.
    scenario.conf.set(scenario.ConfigKey.RUNNER_SCRIPT_PATH, scenario.test.paths.SCENARIO_TEST_LAUNCHER)
    # - Default test suite files.
    scenario.conf.set(scenario.ConfigKey.TEST_SUITE_FILES, list(scenario.test.paths.SCENARIO_TESTS_PATH.glob("*/*.suite")))
    # - Default output directory.
    scenario.conf.set(scenario.ConfigKey.CAMPAIGN_OUTDIR, scenario.test.paths.SCENARIO_RESULTS_PATH)
    # - Issue level names and URL builder.
    scenario.IssueLevel.definenames(scenario.test.IssueLevel)
    scenario.KnownIssue.seturlbuilder(lambda issue_id: (
        f"https://github.com/alxroyer/scenario/issues/{issue_id.lstrip('#')}"
        if (
            # Defensive condition.
            isinstance(issue_id, str)  # type: ignore[redundant-expr]  ## Left operand of "and" is always true
            and issue_id.startswith("#")
        )
        else None
    ))

    # Parse arguments.
    scenario.Args.setinstance(ScenarioCampaignArgs())
    if not ScenarioCampaignArgs.getinstance().parse(sys.argv[1:]):
        sys.exit(int(ScenarioCampaignArgs.getinstance().error_code))

    # Set main path after arguments have been parsed.
    scenario.Path.setmainpath(scenario.test.paths.ROOT_SCENARIO_PATH)

    # Load requirements.
    scenario.reqs.load()

    # Campaign execution.
    _res = scenario.campaign_runner.main()  # type: scenario.ErrorCode
    sys.exit(int(_res))
