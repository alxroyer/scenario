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

# Path management.
MAIN_PATH = pathlib.Path(__file__).parents[1]  # type: pathlib.Path
sys.path.append(str(MAIN_PATH / "src"))
sys.path.append(str(MAIN_PATH / "test" / "cases"))
sys.path.append(str(MAIN_PATH / "test" / "src"))

# `scenario` imports.
try:
    # Avoid "Module level import not at top of file" PEP8 warnings.
    import scenario
    import scenario.test
finally:
    pass


# Command line arguments.
class UnitTestArgs(scenario.ScenarioArgs):

    def __init__(self):  # type: (...) -> None
        scenario.ScenarioArgs.__init__(self, def_scenario_paths_arg=False)

        self.setdescription("Unit test scenario launcher.")

        self._test_exec_group.add_argument(
            "--skip-attributes",
            dest="check_expected_attributes", action="store_false", default=True,
            help="Do not check expected attributes",
        )

        # Redefine positional arguments after the option added above.
        self._defscenariopathsarg()

    @property
    def check_expected_attributes(self):  # type: () -> bool
        return bool(self._args.check_expected_attributes)


if __name__ == "__main__":
    from scenario.scenarioconfig import SCENARIO_CONFIG

    # Configure issue level names and URL builder.
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
    scenario.Args.setinstance(UnitTestArgs())
    if not UnitTestArgs.getinstance().parse(sys.argv[1:]):
        sys.exit(int(UnitTestArgs.getinstance().error_code))

    # Set main path after arguments have been parsed.
    scenario.Path.setmainpath(scenario.test.paths.MAIN_PATH)

    # Declare expected attributes.
    if UnitTestArgs.getinstance().check_expected_attributes:
        # Memo: Enum definitions are stored as lists in the configuration database.
        scenario.conf.set(scenario.ConfigKey.EXPECTED_ATTRIBUTES, scenario.test.ScenarioAttribute)
    # Configure test titles to be displayed as extra info (if nothing already configured).
    if not SCENARIO_CONFIG.resultsextrainfo():
        scenario.conf.set(scenario.ConfigKey.RESULTS_EXTRA_INFO, [scenario.test.ScenarioAttribute.TEST_TITLE])

    # Scenario execution.
    _res = scenario.runner.main()  # type: scenario.ErrorCode
    sys.exit(int(_res))
