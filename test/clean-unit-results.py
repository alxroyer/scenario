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
import shutil
import sys

# Path management.
_root_scenario_path = pathlib.Path(__file__).parents[1]  # type: pathlib.Path
sys.path.append(str(_root_scenario_path / "src"))
sys.path.append(str(_root_scenario_path / "test" / "src"))


if __name__ == "__main__":
    import scenario
    import scenario.test

    scenario.Args.setinstance(scenario.Args(class_debugging=False))
    if not scenario.Args.getinstance().parse(sys.argv[1:]):
        sys.exit(int(scenario.Args.getinstance().error_code))

    if scenario.test.paths.UNIT_RESULTS_PATH.is_dir():
        for _subpath in scenario.test.paths.UNIT_RESULTS_PATH.iterdir():  # type: scenario.Path
            if _subpath.is_dir():
                scenario.logging.info(f"Removing '{_subpath}'")
                shutil.rmtree(_subpath)
