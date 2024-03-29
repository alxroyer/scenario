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

"""
Scenario test launcher.
"""

import pathlib
import sys


try:
    import scenario
except ImportError:
    _home_path = pathlib.Path(__file__).parents[1]  # type: pathlib.Path
    _src_path = _home_path / "src"  # type: pathlib.Path
    _init_path = _src_path / "scenario" / "__init__.py"  # type: pathlib.Path
    if _init_path.is_file():
        try:
            sys.path.append(str(_src_path))
            import scenario
        except ImportError:
            scenario = None  # type: ignore
    else:
        scenario = None  # type: ignore
if "scenario" not in sys.modules:
    print("Could not import scenario. Please adjust PYTHONPATH environment variable.")
    sys.exit(40)  # ErrorCodes.ENVIRONMENT_ERROR

# Main script => redirect to TestRunner.main()
_res = scenario.runner.main()  # type: scenario.ErrorCode
sys.exit(int(_res))
