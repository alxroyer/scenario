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
sys.path.append(str(MAIN_PATH / "tools" / "src"))

# `scenario` imports.
try:
    # Avoid "Module level import not at top of file" PEP8 warnings.
    import scenario
    import scenario.tools
finally:
    pass


if __name__ == "__main__":
    _res = scenario.tools.CheckTypes(
        main_path=scenario.tools.paths.MAIN_PATH,
        mypy_conf_path=scenario.tools.paths.TOOLS_CONF_PATH / "mypy.ini",
    ).run()  # type: scenario.ErrorCode
    sys.exit(int(_res))
