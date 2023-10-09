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

import scenario


ROOT_SCENARIO_PATH = scenario.Path(__file__).parents[4]  # type: scenario.Path
BIN_PATH = ROOT_SCENARIO_PATH / "bin"  # type: scenario.Path
DEMO_PATH = ROOT_SCENARIO_PATH / "demo"  # type: scenario.Path
DOC_DATA_PATH = ROOT_SCENARIO_PATH / "doc" / "data"  # type: scenario.Path
DOC_OUT_PATH = ROOT_SCENARIO_PATH / "doc" / "html"  # type: scenario.Path
DOC_SRC_PATH = ROOT_SCENARIO_PATH / "doc" / "src"  # type: scenario.Path
SRC_PATH = ROOT_SCENARIO_PATH / "src"  # type: scenario.Path
TEST_PATH = ROOT_SCENARIO_PATH / "test"  # type: scenario.Path
TEST_CASES_PATH = ROOT_SCENARIO_PATH / "test" / "cases"  # type: scenario.Path
TEST_DATA_PATH = ROOT_SCENARIO_PATH / "test" / "data"  # type: scenario.Path
TEST_SRC_PATH = ROOT_SCENARIO_PATH / "test" / "src"  # type: scenario.Path
TEST_SRC_DATA_PATH = ROOT_SCENARIO_PATH / "test" / "src" / "scenario" / "test" / "_data.py"  # type: scenario.Path
TEST_TOOLS_PATH = ROOT_SCENARIO_PATH / "test" / "tools"  # type: scenario.Path
TOOLS_PATH = ROOT_SCENARIO_PATH / "tools"  # type: scenario.Path
TOOLS_CONF_PATH = ROOT_SCENARIO_PATH / "tools" / "conf"  # type: scenario.Path
TOOLS_LIB_PATH = ROOT_SCENARIO_PATH / "tools" / "lib"  # type: scenario.Path
TOOLS_SRC_PATH = ROOT_SCENARIO_PATH / "tools" / "src"  # type: scenario.Path
UTILS_SRC_PATH = ROOT_SCENARIO_PATH / "utils" / "src"  # type: scenario.Path
