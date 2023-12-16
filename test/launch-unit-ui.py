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
_root_scenario_path = pathlib.Path(__file__).parents[1]  # type: pathlib.Path
sys.path.append(str(_root_scenario_path / "src"))
sys.path.append(str(_root_scenario_path / "test" / "cases"))
sys.path.append(str(_root_scenario_path / "test" / "src"))

if True:
    import scenario
    import scenario.test
    import scenario.ui


if __name__ == "__main__":
    # Parse arguments.
    scenario.Args.setinstance(scenario.Args(class_debugging=True))
    if not scenario.Args.getinstance().parse(sys.argv[1:]):
        sys.exit(int(scenario.Args.getinstance().error_code))

    # Set main path after arguments have been parsed.
    scenario.Path.setmainpath(scenario.test.paths.ROOT_SCENARIO_PATH)

    # Load requirements (no requirement file configuration).
    scenario.test.reqs.load()
    # Configure default test suites.
    scenario.conf.set(scenario.ConfigKey.TEST_SUITE_FILES, list(scenario.test.paths.UNIT_TESTS_PATH.glob("*/*.suite")))

    # UI execution.
    _res = scenario.ui.main()  # type: scenario.ErrorCode
    sys.exit(int(_res))
