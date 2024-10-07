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
_root_scenario_path = pathlib.Path(__file__).parents[1].resolve()  # type: pathlib.Path
sys.path.append(str(_root_scenario_path / "src"))
sys.path.append(str(_root_scenario_path / "test" / "cases"))
sys.path.append(str(_root_scenario_path / "test" / "src"))

if True:
    import scenario  # @after-path-management
    import scenario.reqs  # @after-path-management
    import scenario.test  # @after-path-management
    import scenario.ui  # @after-path-management


if __name__ == "__main__":
    # General configurations:
    # - Default test suites.
    scenario.reqs.setdefaulttestsuites()
    # - Campaign output directory.
    scenario.conf.set(scenario.ConfigKey.CAMPAIGN_OUTDIR, scenario.test.paths.SCENARIO_RESULTS_PATH)

    # Parse arguments.
    scenario.Args.setinstance(scenario.ui.Args())
    if not scenario.Args.getinstance().parse(sys.argv[1:]):
        sys.exit(int(scenario.Args.getinstance().error_code))

    # Set main path after arguments have been parsed.
    scenario.Path.setmainpath(scenario.test.paths.ROOT_SCENARIO_PATH)

    # Ensure requirement database update and configure as default.
    scenario.reqs.load(set_default_req_file=True)

    # UI execution.
    _res = scenario.ui.main()  # type: scenario.ErrorCode
    sys.exit(int(_res))
