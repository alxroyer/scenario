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
Scenario user interface launcher.

Launches a HTTP server on localhost.
"""

import pathlib
import sys


if __name__ == "__main__":
    try:
        import scenario
        import scenario.ui
    except ImportError:
        _root_scenario_path = pathlib.Path(__file__).parents[1]  # type: pathlib.Path
        sys.path.append(str(_root_scenario_path / "src"))
        import scenario
        import scenario.ui
    finally:
        if "scenario" not in sys.modules:
            print("Could not import scenario. Please adjust PYTHONPATH environment variable.")
            sys.exit(40)  # ErrorCodes.ENVIRONMENT_ERROR

    # Main script => redirect to `scenario.ui.main()`.
    _res = scenario.ui.main()  # type: scenario.ErrorCode
    sys.exit(int(_res))
