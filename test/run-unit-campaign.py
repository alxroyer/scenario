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
MAIN_PATH = pathlib.Path(__file__).parents[1]  # type: pathlib.Path
sys.path.append(str(MAIN_PATH / "src"))
sys.path.append(str(MAIN_PATH / "test" / "cases"))
sys.path.append(str(MAIN_PATH / "test" / "data"))
sys.path.append(str(MAIN_PATH / "test" / "src"))

# :mod:`scenario` imports.
import scenario  # noqa: E402  ## Module level import not at top of file
from scenario.scenarioconfig import SCENARIO_CONFIG  # noqa: E402  ## Module level import not at top of file
import scenario.test  # noqa: E402  ## Module level import not at top of file


# Command line arguments.
class UnitCampaignArgs(scenario.CampaignArgs):

    def __init__(self):  # type: (...) -> None

        scenario.CampaignArgs.__init__(
            self,
            def_test_suite_paths_arg=False,  # So that we can set our own positional arguments below.
            default_outdir_cwd=False,  # Do not use the current directory as the default output directory.
        )

        self.setdescription("Unit test campaign launcher.")

        # Redefine positional arguments, so that they are optional.
        self._deftestsuitepathsarg(
            nargs="*",
            help=(
                "Test suite file(s) to execute. "
                "Optional: when not set, the default test suite file is used."
            ),
        )

    def _checkargs(self):  # type: (...) -> bool
        # Pre-check test suite paths.
        if not self._args.test_suite_paths:
            for _test_suite_path in scenario.test.paths.UNIT_TESTS_PATH.glob("*/*.suite"):  # type: scenario.Path
                self.debug("Using default test suite file '%s'", _test_suite_path)
                self._args.test_suite_paths.append(_test_suite_path.abspath)

        # Pre-check output directory.
        if self._args.outdir is None:
            self.debug("Using output directory '%s' with --dt-subdir option", scenario.test.paths.UNIT_RESULTS_PATH)
            self.outdir = scenario.test.paths.UNIT_RESULTS_PATH
            self._args.create_dt_subdir = True

        # Call base campaign argument checking.
        if not super()._checkargs():
            return False

        return True


if __name__ == "__main__":
    # Configure issue level names and URL builder.
    scenario.IssueLevel.definenames(scenario.test.IssueLevel)
    scenario.KnownIssue.seturlbuilder(lambda issue_id: (
        f"https://github.com/alxroyer/scenario/issues/{issue_id.lstrip('#')}"
        if isinstance(issue_id, str) and issue_id.startswith("#")
        else None
    ))

    # Parse arguments.
    scenario.Args.setinstance(UnitCampaignArgs())
    if not UnitCampaignArgs.getinstance().parse(sys.argv[1:]):
        sys.exit(int(UnitCampaignArgs.getinstance().error_code))

    # Set main path after arguments have been parsed.
    scenario.Path.setmainpath(scenario.test.paths.MAIN_PATH)

    # Campaign execution:
    # - Have the neighbour `UNIT_TEST_LAUNCHER` script be used as the scenario runner script.
    scenario.conf.set(scenario.ConfigKey.RUNNER_SCRIPT_PATH, scenario.test.paths.UNIT_TEST_LAUNCHER)
    # - Make test titles be displayed as extra info (if nothing already configured).
    if not SCENARIO_CONFIG.resultsextrainfo():
        scenario.conf.set(scenario.ConfigKey.RESULTS_EXTRA_INFO, [scenario.test.ScenarioAttribute.TEST_TITLE])
    # - Eventually launch the campaign execution.
    _res = scenario.campaign_runner.main()  # Type already defined above.
    sys.exit(int(_res))
