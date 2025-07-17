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
import typing

import scenario
import scenario.inners


class ValidateJsonFiles(abc.ABC):

    class Args(scenario.Args):
        def __init__(self):  # type: (...) -> None
            from .. import _paths

            scenario.Args.__init__(self, class_debugging=False)

            self.setdescription("Validates scenario json files with applicable schemas.")

            self.scenario_reports = []  # type: typing.List[scenario.Path]
            self.addarg("Scenario report file validation", "scenario_reports", scenario.Path).define(
                "--scenario-report", metavar="SCENARIO_REPORT_PATH",
                action="append", type=str, default=[],
                help=f"Validate the given scenario report with '{_paths.SCENARIO_REPORT_SCHEMA_PATH}'.",
            )

            self.req_dbs = []  # type: typing.List[scenario.Path]
            self.addarg("Requirement database file validation", "req_dbs", scenario.Path).define(
                "--req-db", metavar="REQ_DB_PATH",
                action="append", type=str, default=[],
                help=f"Validate the given requirement database with '{_paths.REQ_DB_SCHEMA_PATH}'.",
            )

            self.downstream_traceabilities = []  # type: typing.List[scenario.Path]
            self.addarg("Downstream tracability report validation", "downstream_traceabilities", scenario.Path).define(
                "--downstream-traceability", metavar="DOWNSTREAM_TRACEABILITY_PATH",
                action="append", type=str, default=[],
                help=f"Validate the given downstream traceability report with '{_paths.DOWNSTREAM_TRACEABILITY_SCHEMA_PATH}'",
            )

            self.upstream_traceabilities = []  # type: typing.List[scenario.Path]
            self.addarg("Upstream traceability report validation", "upstream_traceabilities", scenario.Path).define(
                "--upstream-traceability", metavar="UPSTREAM_TRACEABILITY_PATH",
                action="append", type=str, default=[],
                help=f"Validate the given upstream traceability report with '{_paths.UPSTREAM_TRACEABILITY_SCHEMA_PATH}'",
            )

            self.resolve_external_refs = True  # type: bool
            self.addarg("Download external refs", "resolve_external_refs", bool).define(
                "--dont-resolve-external-refs",
                action="store_false", default=True,
                help="Don't resolve external schema references from local files, let the JSON schema validation get them from the Internet.",
            )

            self.harden_schemas = False  # type: bool
            self.addarg("Harden schemas", "harden_schemas", bool).define(
                "--harden-schemas",
                action="store_true", default=False,
                help="Harden schemas for validation. Does not take effect if `--dont-resolve-external-refs` is used.",
            )

            self.debug_recursions = False  # type: bool
            self.addarg("Debug recursions", "debug_recursions", bool).define(
                "--debug-recursions",
                action="store_true", default=False,
                help="Debug schema management recursions: external ref resolution and hardening.",
            )

    _schemas = {}  # type: typing.Dict[scenario.Path, scenario.types.JsonDict]

    @staticmethod
    def execute():  # type: (...) -> None
        from .. import _paths

        for _scenario_report_path in ValidateJsonFiles.Args.getinstance().scenario_reports:  # type: scenario.Path
            scenario.logging.debug("ValidateJsonFiles.execute(): _scenario_report_path='%s'", _scenario_report_path)
            ValidateJsonFiles._validate(_scenario_report_path, _paths.SCENARIO_REPORT_SCHEMA_PATH)

        for _req_db_path in ValidateJsonFiles.Args.getinstance().req_dbs:  # type: scenario.Path
            scenario.logging.debug("ValidateJsonFiles.execute(): _req_db_path='%s'", _req_db_path)
            ValidateJsonFiles._validate(_req_db_path, _paths.REQ_DB_SCHEMA_PATH)

        for _downtream_traceability in ValidateJsonFiles.Args.getinstance().downstream_traceabilities:  # type: scenario.Path
            scenario.logging.debug("ValidateJsonFiles.execute(): _downtream_traceability='%s'", _downtream_traceability)
            ValidateJsonFiles._validate(_downtream_traceability, _paths.DOWNSTREAM_TRACEABILITY_SCHEMA_PATH)

        scenario.logging.warning(f"'{_paths.UPSTREAM_TRACEABILITY_SCHEMA_PATH}' not implemented yet")
        # for _upstream_traceability in CheckSchemasArgs.getinstance().upstream_traceabilities:  # type: scenario.Path
        #     scenario.logging.debug("ValidateJsonFiles.execute(): _upstream_traceability='%s'", _upstream_traceability)
        #     ValidateJsonFiles._validate(_upstream_traceability, UPSTREAM_TRACEABILITY_SCHEMA_PATH)

    @classmethod
    def _validate(
            cls,
            scenario_report_path,  # type: scenario.Path
            schema_path,  # type: scenario.Path
    ):  # type: (...) -> None
        from ._schema import Schema

        # Ensure the schema file is loaded.
        _schema = cls._schemas.get(schema_path)  # type: typing.Optional[scenario.types.JsonDict]
        if _schema is None:
            _schema = cls._schemas[schema_path] = Schema.read(
                schema_path,
                resolve_external_refs=ValidateJsonFiles.Args.getinstance().resolve_external_refs,
                harden=ValidateJsonFiles.Args.getinstance().harden_schemas,
                debug_recursions=ValidateJsonFiles.Args.getinstance().debug_recursions,
            )

        # Schema validation.
        scenario.logging.info(f"Validating '{scenario_report_path}' with '{schema_path}'")
        _validation_error = None  # type: typing.Optional[jsonschema.ValidationError]
        try:
            _json_dict = scenario.inners.JsonDict.File.read(scenario_report_path)  # type: scenario.types.JsonDict
            scenario.logging.debug("ValidateJsonFiles._validate(): _json_dict=%s", scenario.debug.jsondump(_json_dict, indent=2),
                                   extra={scenario.logging.Extra.LONG_TEXT_MAX_LINES: 50})
            jsonschema.validate(_json_dict, _schema)
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
