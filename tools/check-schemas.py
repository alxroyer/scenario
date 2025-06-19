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
import jsonschema  # type: ignore[import]  ## Library stubs not installed for "jsonschema"
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


SCENARIO_REPORT_SCHEMA_PATH = scenario.tools.paths.ROOT_SCENARIO_PATH / scenario.report.JSON_SCHEMA_SUBPATH  # type: scenario.Path
REQ_DB_SCHEMA_PATH = scenario.tools.paths.ROOT_SCENARIO_PATH / scenario.ReqDatabase.JSON_SCHEMA_SUBPATH  # type: scenario.Path


class CheckSchemasArgs(scenario.Args):
    def __init__(self):  # type: (...) -> None
        scenario.Args.__init__(self, class_debugging=False)

        self.setdescription("Schema checker. "
                            "Updates .json schemas from .yml files, then apply options.")

        self.scenario_reports = []  # type: typing.List[scenario.Path]
        self.addarg("Scenario report file validation", "scenario_reports", scenario.Path).define(
            "--scenario-report", metavar="SCENARIO_REPORT_PATH",
            action="append", type=str, default=[],
            help=f"Validate the given scenario report with '{SCENARIO_REPORT_SCHEMA_PATH}'.",
        )

        self.req_dbs = []  # type: typing.List[scenario.Path]
        self.addarg("Requirement database file validation", "req_dbs", scenario.Path).define(
            "--req-db", metavar="REQ_DB_PATH",
            action="append", type=str, default=[],
            help=f"Validate the given requirement database with '{REQ_DB_SCHEMA_PATH}'.",
        )

        self.strengthen_schema = False  # type: bool
        self.addarg("Schema strengthening", "strengthen_schema", bool).define(
            "--strengthen-schema",
            action="store_true", default=False,
            help="Strengthen schema for validation.",
        )

        self.validate_test_data = False  # type: bool
        self.addarg("Validate test data", "validate_test_data", bool).define(
            "--validate-test-data",
            action="store_true", default=False,
            help=f"Validate test data: .json and .yml files from '{scenario.tools.paths.TEST_DATA_PATH}'.",
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


class ValidateJsonFiles(abc.ABC):

    _schemas = {}  # type: typing.Dict[scenario.Path, scenario.types.JsonDict]

    @staticmethod
    def listtestdatafiles():  # type: (...) -> None
        for _json_path in scenario.tools.paths.TEST_DATA_PATH.rglob("*.json"):  # type: scenario.Path
            scenario.logging.debug("ValidateJsonFiles.listtestdatafiles(): _json_path='%s'", _json_path)

            if _json_path.name.endswith(".doc-only.json") or _json_path.name.endswith(".executed.json"):
                if _json_path not in CheckSchemasArgs.getinstance().scenario_reports:
                    CheckSchemasArgs.getinstance().scenario_reports.append(_json_path)
            elif _json_path in [scenario.tools.paths.TEST_DATA_PATH / "req-db.json"]:
                if _json_path not in CheckSchemasArgs.getinstance().req_dbs:
                    CheckSchemasArgs.getinstance().req_dbs.append(_json_path)
            elif _json_path in [scenario.tools.paths.TEST_DATA_PATH / "conf.json"]:
                pass
            else:
                raise ValueError(f"Unknwon JSON file type '{_json_path}'")

        for _yaml_path in scenario.tools.paths.TEST_DATA_PATH.rglob("*.yml"):  # type: scenario.Path
            scenario.logging.debug("ValidateJsonFiles.listtestdatafiles(): _yaml_path='%s'", _yaml_path)
            if _yaml_path in [scenario.tools.paths.TEST_DATA_PATH / "conf.yml"]:
                pass
            else:
                raise ValueError(f"Unknwon YAML file type '{_yaml_path}'")

    @staticmethod
    def execute():  # type: (...) -> None
        for _scenario_report_path in CheckSchemasArgs.getinstance().scenario_reports:  # type: scenario.Path
            scenario.logging.debug("ValidateJsonFiles.execute(): _scenario_report_path='%s'", _scenario_report_path)
            ValidateJsonFiles._validate(_scenario_report_path, SCENARIO_REPORT_SCHEMA_PATH)

        for _req_db_path in CheckSchemasArgs.getinstance().req_dbs:  # type: scenario.Path
            scenario.logging.debug("ValidateJsonFiles.execute(): _req_db_path='%s'", _req_db_path)
            ValidateJsonFiles._validate(_req_db_path, REQ_DB_SCHEMA_PATH)

    @classmethod
    def _validate(
            cls,
            scenario_report_path,  # type: scenario.Path
            schema_path,  # type: scenario.Path
    ):  # type: (...) -> None
        # Ensure the schema file is loaded.
        _schema = cls._schemas.get(schema_path)  # type: typing.Optional[scenario.types.JsonDict]
        if _schema is None:
            scenario.logging.debug("ValidateJsonFiles._validate(): Reading '%s'", schema_path)
            _schema = scenario.inners.JsonDict.File.read(schema_path)

            if CheckSchemasArgs.getinstance().strengthen_schema:
                scenario.logging.debug("ValidateJsonFiles._validate(): Strengthening '%s'",
                                       scenario.debug.jsondump(_schema, indent=2),
                                       extra={scenario.logging.Extra.LONG_TEXT_MAX_LINES: 10})
                cls._strengthenschema(_schema)

            cls._schemas[schema_path] = _schema

        scenario.logging.info(f"Validating '{scenario_report_path}' with '{schema_path}'")
        _validation_error = None  # type: typing.Optional[jsonschema.ValidationError]
        try:
            jsonschema.validate(
                scenario.inners.JsonDict.File.read(scenario_report_path),
                _schema,
            )
        except jsonschema.ValidationError as _err:
            # `str(_err)` displays the details of the validation error.
            #
            # This output is interesting, but very long.
            # And it is better finishing with the `repr(_err)` information for the synthesis of the error.
            #
            # Let's juste save the error in this context, and raise another exception out of this `except` block
            # to avoid `_err` be chained and displayed when the exception reaches the *main*.
            _validation_error = _err

        if _validation_error is not None:
            # `jsonscehma` long error display.
            scenario.logging.error(f"{_validation_error}", extra={scenario.logging.Extra.LONG_TEXT: True})

            # Error synthesis.
            scenario.logging.error("")
            scenario.logging.error(f"Error while validating '{scenario_report_path}' with '{schema_path}':")
            scenario.logging.error(f"  {_validation_error!r}")
            scenario.logging.error("  (see details above)")

            # End with error.
            raise scenario.ErrorCodeError(
                scenario.ErrorCode.INPUT_FORMAT_ERROR,
                f"Error while validating '{scenario_report_path}' with '{schema_path}'",
            )

    @staticmethod
    def _strengthenschema(
            schema,  # type: scenario.types.JsonDict
    ):  # type: (...) -> None
        """
        Ensures ``"unevaluatedProperties": false`` configurations in the ``schema`` JSON schema dictionary.

        Cross-recursive implementation.

        .. warning::
            May probably add ``"unevaluatedProperties": false`` configurations on nodes that don't require it.

            For instance, if a property actually resolves in a non-object type due to ``$ref`` and/or ``anyOf`` that resolves to basic types,
            this function does not handle this situation, and applies ``"unevaluatedProperties": false`` whatever.

            Nevertheless, these extra configurations do not make the JSON validation fail,
            so we keep it that way.
        """
        def _check_dict(
                names,  # type: typing.Sequence[str]
                json,  # type: scenario.types.JsonDict
        ):  # type: (...) -> None
            # scenario.logging.debug("ValidateJsonFiles._strengthenschema(): _check_dict(names=%r, json=%s)",
            #                        names, scenario.debug.jsondump(json, indent=2),
            #                        extra={scenario.logging.Extra.LONG_TEXT_MAX_LINES: 3})

            # Check whether `json` is a JSON Schema object definition.
            # Add `"unevaluatedProperties": false` configurations when applicable.
            if names and names[-1] and any([
                "properties" in json,
                "allOf" in json,
                "anyOf" in json,
                ("$ref" in json) and json["$ref"].startswith("#/$defs/_"),
            ]):
                # Memo: When the name starts with '_', we consider by design that this is a non-final object (see 'schemasREADME.md').
                # Don't set `"unevaluatedProperties": false` for non-final objects.
                if names[-1].startswith("_"):
                    scenario.logging.debug("ValidateJsonFiles._strengthenschema(): Base %r not strengthened", names[-1])

                # Don't overwrite an existing `"unevaluatedProperties"` configuration.
                elif "unevaluatedProperties" in json:
                    scenario.logging.debug("ValidateJsonFiles._strengthenschema(): %r => `\"unevaluatedProperties\": %r` already defined",
                                           names[-1], json["unevaluatedProperties"])

                # Don't conflict with an existing `"unevaluatedProperties"` configuration.
                elif "additionalProperties" in json:
                    scenario.logging.debug("ValidateJsonFiles._strengthenschema(): %r, 'additionalProperties' set "
                                           "=> `\"unevaluatedProperties\": false` not added", names[-1])

                # Add an `"unevaluatedProperties": false` configuration.
                else:
                    scenario.logging.debug("ValidateJsonFiles._strengthenschema(): %r => `\"unevaluatedProperties\": false` added", names[-1])
                    json["unevaluatedProperties"] = False

            # Spread cross-recursivity.
            with scenario.logging.pushindentation("  "):
                for _name, _value in json.items():  # type: str, typing.Any
                    if isinstance(_value, dict):
                        _check_dict([*names, _name], _value)
                    elif isinstance(_value, list):
                        _check_list([*names, _name], _value)

        def _check_list(
                names,  # type: typing.Sequence[str]
                json_list,  # type: typing.List[typing.Any]
        ):  # type: (...) -> None
            # scenario.logging.debug("ValidateJsonFiles._strengthenschema(): _check_list(json_list=%r)",
            #                        scenario.debug.jsondump(json_list, indent=2),
            #                        extra={scenario.logging.Extra.LONG_TEXT_MAX_LINES: 3})

            # Spread cross-recursivity.
            with scenario.logging.pushindentation("  "):
                for _item in json_list:  # type: typing.Any
                    if isinstance(_item, dict):
                        _check_dict([*names, ""], _item)
                    elif isinstance(_item, list):
                        _check_list([*names, ""], _item)

        # Launch the cross-recursivity process.
        _check_dict([], schema)


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
