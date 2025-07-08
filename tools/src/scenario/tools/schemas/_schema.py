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
import typing

import scenario
import scenario.inners


class Schema(abc.ABC):

    @staticmethod
    def read(
            path,  # type: scenario.Path
            *,
            harden=False,  # type: bool
            debug_recursions=False,  # type: bool
    ):  # type: (...) -> scenario.types.JsonDict
        scenario.logging.debug("Schema.read(): Reading '%s'", path)
        _schema = scenario.inners.JsonDict.File.read(path)  # type: scenario.types.JsonDict

        if harden:
            scenario.logging.debug("Schema.read(): Hardening '%s'", path)
            Schema._harden(_schema, debug_recursion=debug_recursions)

        # Debug the resulting schema content.
        scenario.logging.debug("Schema.read('%s') -> %s", path, scenario.debug.jsondump(_schema, indent=2),
                               extra={scenario.logging.Extra.LONG_TEXT: True})

        return _schema

    @staticmethod
    def _harden(
            schema,  # type: scenario.types.JsonDict
            *,
            debug_recursion,  # type: bool
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
        def _walkdict(
                names,  # type: typing.Sequence[str]
                json_dict,  # type: scenario.types.JsonDict
        ):  # type: (...) -> None
            Schema._debugrecursivecall(debug_recursion, "_harden", "_walkdict", {
                "names": ("%r", names),
                "json_dict": ("%s", scenario.debug.jsondump(json_dict, indent=2)),
            })

            # Check whether `json` is a JSON Schema object definition.
            # Add `"unevaluatedProperties": false` configurations when applicable.
            if names and names[-1] and any([
                "properties" in json_dict,
                "allOf" in json_dict,
                "anyOf" in json_dict,
                ("$ref" in json_dict) and json_dict["$ref"].startswith("#/$defs/_"),
            ]):
                # Memo: When the name starts with '_', we consider by design that this is a non-final object (see 'schemasREADME.md').
                # Don't set `"unevaluatedProperties": false` for non-final objects.
                if names[-1].startswith("_"):
                    scenario.logging.debug("Schema._harden(): Base %r not strengthened", names[-1])

                # Don't overwrite an existing `"unevaluatedProperties"` configuration.
                elif "unevaluatedProperties" in json_dict:
                    scenario.logging.debug("Schema._harden(): %r => `\"unevaluatedProperties\": %r` already defined",
                                           names[-1], json_dict["unevaluatedProperties"])

                # Don't conflict with an existing `"unevaluatedProperties"` configuration.
                elif "additionalProperties" in json_dict:
                    scenario.logging.debug("Schema._harden(): %r, 'additionalProperties' set "
                                           "=> `\"unevaluatedProperties\": false` not added", names[-1])

                # Add an `"unevaluatedProperties": false` configuration.
                else:
                    scenario.logging.debug("Schema._harden(): %r => `\"unevaluatedProperties\": false` added", names[-1])
                    json_dict["unevaluatedProperties"] = False

            # Spread cross-recursivity.
            for _name, _value in json_dict.items():  # type: str, typing.Any
                if isinstance(_value, dict):
                    with scenario.logging.pushindentation("  "):
                        _walkdict([*names, _name], _value)
                elif isinstance(_value, list):
                    with scenario.logging.pushindentation("  "):
                        _walklist([*names, _name], _value)

        def _walklist(
                names,  # type: typing.Sequence[str]
                json_list,  # type: typing.List[typing.Any]
        ):  # type: (...) -> None
            Schema._debugrecursivecall(debug_recursion, "_harden", "_walklist", {
                "names": ("%r", names),
                "json_list": ("%s", scenario.debug.saferepr(json_list)),
            })

            # Spread cross-recursivity.
            for _item in json_list:  # type: typing.Any
                if isinstance(_item, dict):
                    with scenario.logging.pushindentation("  "):
                        _walkdict([*names, ""], _item)
                elif isinstance(_item, list):
                    with scenario.logging.pushindentation("  "):
                        _walklist([*names, ""], _item)

        # Launch the cross-recursivity process.
        _walkdict([], schema)

    @staticmethod
    def _debugrecursivecall(
            do_debug,  # type: bool
            main_method_name,  # type: str
            inner_function_name,  # type: str
            args,  # type: typing.Dict[str, typing.Any]
    ):  # type: (...) -> None
        if do_debug:
            scenario.logging.debug(
                "Schema.%s(): %s(%s)" % (
                    main_method_name,
                    inner_function_name,
                    ", ".join([
                        f"{_name}={_fmt}"
                        for _name, (_fmt, _) in args.items()
                    ]),
                ),
                *[_value for _fmt, _value in args.values()],
                extra={scenario.logging.Extra.LONG_TEXT_MAX_LINES: 3},
            )
