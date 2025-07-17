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

import abc
import pathlib
import sys
import typing

# Path management.
_root_scenario_path = pathlib.Path(__file__).parents[1].resolve()  # type: pathlib.Path
sys.path.append(str(_root_scenario_path / "src"))
sys.path.append(str(_root_scenario_path / "tools" / "src"))
sys.path.append(str(_root_scenario_path / "utils" / "src"))

if True:
    import scenario  # @after-path-management
    import scenario.inners  # @after-path-management
    import scenario.tools  # @after-path-management
    import scenario.tools.schemas  # @after-path-management


class CheckSchemasArgs(scenario.tools.schemas.ValidateJsonFiles.Args):
    def __init__(self):  # type: (...) -> None
        scenario.tools.schemas.ValidateJsonFiles.Args.__init__(self)

        self.setdescription("Schema checker. "
                            "Updates .json schemas from .yml files, then apply options.")

        self.validate_test_data = False  # type: bool
        self.addarg("Validate test data", "validate_test_data", bool).define(
            "--validate-test-data",
            action="store_true", default=False,
            help=f"Validate test data: .json and .yml files from '{scenario.tools.paths.TEST_PATH}' and '{scenario.tools.paths.TEST_DATA_PATH}'.",
        )


class ConvertYaml2JsonSchema(abc.ABC):

    @staticmethod
    def convertall():  # type: (...) -> None
        for _path in scenario.tools.paths.SCHEMAS_PATH.glob("*.schema.yml"):  # type: scenario.Path
            scenario.logging.debug("ConvertYaml2JsonSchema.convertall(): _path='%s'", _path)
            ConvertYaml2JsonSchema._convertyaml2json(_path)

    @staticmethod
    def _convertyaml2json(
            yaml_path,  # type: scenario.Path
    ):  # type: (...) -> None
        _json_path = yaml_path.with_suffix(".json")  # type: scenario.Path
        scenario.logging.info(f"Updating '{_json_path}' from '{yaml_path}'")

        # Read from the input YAML file.
        _json_schema = scenario.inners.JsonDict.File.read(yaml_path)  # type: scenario.types.JsonDict

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
            _json_schema, _json_path,
            # Force UTF-8.
            encoding="utf-8",
        )


class ValidateJsonFiles(scenario.tools.schemas.ValidateJsonFiles):

    @staticmethod
    def listtestdatafiles():  # type: (...) -> None
        def _addtestfile(
                path,  # type: scenario.Path
                list_of_paths,  # type: typing.List[scenario.Path]
        ):  # type: (...) -> None
            assert path.is_file(), f"No such file '{path}'"
            assert path not in list_of_paths, f"'{path}' already known"
            scenario.logging.debug(f"ValidateJsonFiles.listtestdatafiles(): '{path}'")
            list_of_paths.append(path)

        def _skiptestfile(
                path,  # type: scenario.Path
        ):  # type: (...) -> None
            scenario.logging.debug(f"ValidateJsonFiles.listtestdatafiles(): '{path}' skipped")

        # List test files from the 'test/' directory.
        _addtestfile(scenario.tools.paths.TEST_PATH / "req-db.yml", CheckSchemasArgs.getinstance().req_dbs)
        _addtestfile(scenario.tools.paths.TEST_PATH / "downstream-traceability.yml", CheckSchemasArgs.getinstance().downstream_traceabilities)
        _addtestfile(scenario.tools.paths.TEST_PATH / "upstream-traceability.yml", CheckSchemasArgs.getinstance().upstream_traceabilities)

        # List test files from the 'test/data/' directory.
        for _json_path in scenario.tools.paths.TEST_DATA_PATH.rglob("*.json"):  # type: scenario.Path
            if _json_path.name.endswith(".doc-only.json") or _json_path.name.endswith(".executed.json"):
                _addtestfile(_json_path, CheckSchemasArgs.getinstance().scenario_reports)
            elif _json_path in [scenario.tools.paths.TEST_DATA_PATH / "req-db.json"]:
                _addtestfile(_json_path, CheckSchemasArgs.getinstance().req_dbs)
            elif _json_path in [scenario.tools.paths.TEST_DATA_PATH / "conf.json"]:
                _skiptestfile(_json_path)
            else:
                raise ValueError(f"Unknwon JSON file type '{_json_path}'")
        for _yaml_path in scenario.tools.paths.TEST_DATA_PATH.rglob("*.yml"):  # type: scenario.Path
            if _yaml_path in [scenario.tools.paths.TEST_DATA_PATH / "conf.yml"]:
                _skiptestfile(_yaml_path)
            else:
                raise ValueError(f"Unknwon YAML file type '{_yaml_path}'")


if __name__ == "__main__":
    # Command line arguments.
    scenario.Args.setinstance(CheckSchemasArgs())
    if not CheckSchemasArgs.getinstance().parse(sys.argv[1:]):
        sys.exit(int(CheckSchemasArgs.getinstance().error_code))

    scenario.Path.setmainpath(scenario.tools.paths.ROOT_SCENARIO_PATH)

    # Convert all YAML to JSON schemas.
    ConvertYaml2JsonSchema.convertall()

    # Scenario reports and reqdb files validation.
    if CheckSchemasArgs.getinstance().validate_test_data:
        ValidateJsonFiles.listtestdatafiles()
    ValidateJsonFiles.execute()
