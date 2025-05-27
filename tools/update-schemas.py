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
sys.path.append(str(_root_scenario_path / "tools" / "src"))
sys.path.append(str(_root_scenario_path / "utils" / "src"))


if __name__ == '__main__':
    import scenario
    import scenario.inners
    import scenario.tools

    # Command line arguments.
    scenario.Args.setinstance(scenario.Args(class_debugging=False))
    scenario.Args.getinstance().setdescription("Schema files update.")
    if not scenario.Args.getinstance().parse(sys.argv[1:]):
        sys.exit(int(scenario.Args.getinstance().error_code))

    scenario.Path.setmainpath(scenario.tools.paths.ROOT_SCENARIO_PATH)

    for _input_path in scenario.tools.paths.SCHEMAS_PATH.iterdir():  # type: scenario.Path
        scenario.logging.debug("_input_path='%s', suffix=%r", _input_path, _input_path.suffix)
        if _input_path.name.endswith(".schema.yml"):
            _output_path = _input_path.with_suffix(".json")  # type: scenario.Path
            scenario.logging.info(f"Updating '{_output_path}' from '{_input_path}'")

            # Read from the input YAML file.
            _json_schema = scenario.inners.JsonDict.File.read(_input_path)  # type: scenario.types.JsonDict

            # Add the license header, as a first JSON '$license' property.
            _json_schema = {
                "$license": [
                    "Copyright 2020-2023 Alexis Royer <https://github.com/alxroyer/scenario>",
                    "",
                    "Licensed under the Apache License, Version 2.0 (the \"License\");",
                    "you may not use this file except in compliance with the License.",
                    "You may obtain a copy of the License at",
                    "",
                    "    http://www.apache.org/licenses/LICENSE-2.0",
                    "",
                    "Unless required by applicable law or agreed to in writing, software",
                    "distributed under the License is distributed on an \"AS IS\" BASIS,",
                    "WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.",
                    "See the License for the specific language governing permissions and",
                    "limitations under the License."
                ],
                **_json_schema,
            }

            # Write the output JSON file.
            scenario.inners.JsonDict.File.write(
                _json_schema, _output_path,
                # Force UTF-8.
                encoding="utf-8",
            )
