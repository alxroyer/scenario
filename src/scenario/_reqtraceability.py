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
Requirement traceability reports.
"""

import abc
import json
import typing

if True:
    from ._logger import Logger as _LoggerImpl  # `Logger` used for inheritance.
if typing.TYPE_CHECKING:
    from ._path import Path as _PathType
    from ._req import Req as _ReqType
    from ._reqlink import ReqLink as _ReqLinkType
    from ._reqref import ReqRef as _ReqRefType
    from ._scenariodefinition import ScenarioDefinition as _ScenarioDefinitionType
    from ._stepdefinition import StepDefinition as _StepDefinitionType
    from ._typingutils import JsonDictType as _JsonDictType


class ReqTraceability(_LoggerImpl):

    def __init__(self):  # type: (...) -> None
        from ._debugclasses import DebugClass

        _LoggerImpl.__init__(self, DebugClass.REQ_TRACEABILITY)

        self.scenarios = []  # type: typing.List[_ScenarioDefinitionType]

    def loaddata(
            self,
            *,
            reqdb_file_paths=None,  # type: typing.Iterable[_PathType]
            test_suite_paths=None,  # type: typing.Iterable[_PathType]
            campaign_dir_path=None,  # type: _PathType
    ):  # type: (...) -> None
        from ._reqdb import REQ_DB
        from ._scenarioconfig import SCENARIO_CONFIG
        from ._scenariodefinition import ScenarioDefinition, ScenarioDefinitionHelper
        from ._testsuitefile import TestSuiteFile

        self.debug(
            "ReqTraceability.loaddata(reqdb_file_paths=%r, test_suite_paths=%r, campaign_dir_path=%r)",
            reqdb_file_paths, test_suite_paths, campaign_dir_path,
        )

        # Ensure persistent and countable input lists.
        if reqdb_file_paths:
            reqdb_file_paths = list(reqdb_file_paths)
        if test_suite_paths:
            test_suite_paths = list(test_suite_paths)

        self.info("Loading requirements")
        with self.pushindentation("  "):
            REQ_DB.clear()

            if reqdb_file_paths is not None:
                for _reqdb_file_path in reqdb_file_paths:  # type: _PathType
                    self.info(f"Loading '{_reqdb_file_path}'")
                    REQ_DB.load(_reqdb_file_path)
            else:
                for _reqdb_file_path in SCENARIO_CONFIG.reqdbfiles():  # Type already declared above.
                    self.info(f"Loading '{_reqdb_file_path}'")
                    REQ_DB.load(_reqdb_file_path)

            _req_ref_count = len(REQ_DB.getallrefs())  # type: int
            self.info(f"{_req_ref_count} requirement reference{'' if (_req_ref_count == 1) else 's'} loaded")

        self.info("Loading scenarios")
        with self.pushindentation("  "):
            self.scenarios.clear()

            if test_suite_paths is not None:
                self.debug("Reading %d test suite file(s)", len(list(test_suite_paths)))
                for _test_suite_path in test_suite_paths:  # type: _PathType
                    self.info("Loading '%s'", _test_suite_path)
                    with self.pushindentation("  "):
                        _test_suite_file = TestSuiteFile(_test_suite_path)  # type: TestSuiteFile
                        _test_suite_file.read()
                        for _test_script_path in _test_suite_file.script_paths:  # type: _PathType
                            self.info("Loading '%s'", _test_script_path)
                            _scenario_definition_class = ScenarioDefinitionHelper.getscenariodefinitionclassfromscript(
                                _test_script_path,
                                # Avoid loaded module being saved in `sys.modules`,
                                # so that the function can be called again, and traceability refreshed.
                                sys_modules_cache=False,
                            )  # type: typing.Type[ScenarioDefinition]
                            self.debug("_scenario_definition_class=%r", _scenario_definition_class)
                            _scenario = _scenario_definition_class()  # type: ScenarioDefinition
                            self.debug("_scenario=%r", _scenario)
                            self.scenarios.append(_scenario)

            _scenario_count = len(self.scenarios)  # type: int
            self.info(f"{_scenario_count} scenario{'' if (_scenario_count == 1) else 's'} loaded")

    class Downstream(abc.ABC):

        @staticmethod
        def tojson(
                downstream_traceability,  # type: ReqDownstreamTraceabilityType
        ):  # type: (...) -> _JsonDictType
            _json = {}  # type: _JsonDictType
            for _downstream_req_ref in downstream_traceability:  # type: ReqTraceability.Downstream.ReqRef
                _json[_downstream_req_ref.req_ref.id] = _downstream_req_ref.tojson()
            return _json

        class ReqRef:
            def __init__(
                    self,
                    req_ref,  # type: _ReqRefType
            ):  # type: (...) -> None
                self.req_ref = req_ref  # type: _ReqRefType
                self.scenarios = []  # type: typing.List[ReqTraceability.Downstream.Scenario]

            def tojson(self):  # type: (...) -> _JsonDictType
                _json_req_ref = {
                    "id": self.req_ref.id,
                    "scenarios": {},
                }  # type: _JsonDictType

                if self.req_ref.ismain():
                    if self.req_ref.req.title:
                        _json_req_ref["title"] = self.req_ref.req.title
                    if self.req_ref.req.text:
                        _json_req_ref["text"] = self.req_ref.req.text

                for _downstream_scenario in self.scenarios:  # type: ReqTraceability.Downstream.Scenario
                    _json_req_ref["scenarios"][_downstream_scenario.scenario.name] = _downstream_scenario.tojson()

                return _json_req_ref

        class Scenario:
            def __init__(
                    self,
                    downstream_req_ref,  # type: ReqTraceability.Downstream.ReqRef
                    scenario,  # type: _ScenarioDefinitionType
                    req_link,  # type: typing.Optional[_ReqLinkType]
            ):  # type: (...) -> None
                self.downstream_req_ref = downstream_req_ref  # type: ReqTraceability.Downstream.ReqRef
                self.scenario = scenario  # type: _ScenarioDefinitionType
                self.req_link = req_link  # type: typing.Optional[_ReqLinkType]
                self.comments = ""  # type: str
                self.steps = []  # type: typing.List[ReqTraceability.Downstream.Step]

                if req_link:
                    self.comments = req_link.comments or scenario.title

                self.downstream_req_ref.scenarios.append(self)

            def tojson(self):  # type: (...) -> _JsonDictType
                _json_scenario = {
                    "name": self.scenario.name,
                    "comments": self.comments,
                    "steps": {},
                }  # type: _JsonDictType

                if self.scenario.title:
                    _json_scenario["title"] = self.scenario.title

                for _downstream_step in self.steps:  # type: ReqTraceability.Downstream.Step
                    _json_scenario["steps"][f"step#{_downstream_step.step.number}"] = _downstream_step.tojson()

                return _json_scenario

        class Step:
            def __init__(
                    self,
                    downstream_scenario,  # type: ReqTraceability.Downstream.Scenario
                    step,  # type: _StepDefinitionType
                    req_link,  # type: _ReqLinkType
            ):  # type: (...) -> None
                self.downstream_scenario = downstream_scenario  # type: ReqTraceability.Downstream.Scenario
                self.step = step  # type: _StepDefinitionType
                self.req_link = req_link  # type: _ReqLinkType
                self.comments = req_link.comments or self.downstream_scenario.scenario.title  # type: str

                self.downstream_scenario.steps.append(self)

            def tojson(self):  # type: (...) -> _JsonDictType
                return {
                    "number": self.step.number,
                    "name": self.step.name,
                    "comments": self.comments,
                }

    def getdownstream(self):  # type: (...) -> ReqDownstreamTraceabilityType
        from ._reflection import qualname
        from ._reqdb import REQ_DB
        if typing.TYPE_CHECKING:
            from ._reqtypes import SetWithReqLinksType
        from ._reqverifier import ReqVerifier
        from ._scenariodefinition import ScenarioDefinition
        from ._stepdefinition import StepDefinition

        self.debug("ReqTraceability.getdownstream(): Computing downstream traceability from %d requirement references in database", len(REQ_DB.getallrefs()))
        _downstream_req_refs = []  # type: typing.List[ReqTraceability.Downstream.ReqRef]
        for _req_ref in REQ_DB.getallrefs():  # type: _ReqRefType
            _downstream_req_ref = ReqTraceability.Downstream.ReqRef(req_ref=_req_ref)  # type: ReqTraceability.Downstream.ReqRef
            _downstream_req_refs.append(_downstream_req_ref)

            _downstream_scenario = None  # type: typing.Optional[ReqTraceability.Downstream.Scenario]

            _req_verifiers_set = _req_ref.getverifiers()  # type: SetWithReqLinksType[ReqVerifier]
            for _req_verifier in ReqVerifier.orderedset(_req_verifiers_set):  # type: ReqVerifier
                for _req_link in _req_verifiers_set[_req_verifier]:  # type: _ReqLinkType
                    if isinstance(_req_verifier, ScenarioDefinition):
                        if (not _downstream_scenario) or (_downstream_scenario.scenario is not _req_verifier):
                            _downstream_scenario = ReqTraceability.Downstream.Scenario(
                                _downstream_req_ref,  # Memo: `_downstream_scenario` automatically added to `_downstream_req_ref`.
                                scenario=_req_verifier, req_link=_req_link,
                            )
                        else:
                            self.debug(
                                f"{_req_ref!r} -> {_req_verifier!r} already known through {_downstream_scenario.req_link!r}, "
                                f"{_req_link!r} ignored"
                            )
                    elif isinstance(_req_verifier, StepDefinition):
                        # Ensure the owner scenario is set.
                        if (not _downstream_scenario) or (_downstream_scenario.scenario is not _req_verifier.scenario):
                            _downstream_scenario = ReqTraceability.Downstream.Scenario(
                                _downstream_req_ref,  # Memo: `_downstream_scenario` automatically added to `_downstream_req_ref`.
                                scenario=_req_verifier.scenario, req_link=None,
                            )
                        _downstream_step = ReqTraceability.Downstream.Step(
                            _downstream_scenario,  # Memo: `_downstream_step` automatically added to `_downstream_scenario`.
                            step=_req_verifier, req_link=_req_link,
                        )  # type: ReqTraceability.Downstream.Step
                    else:
                        raise ValueError(f"Unexpected verifier {_req_verifier!r}")

        self.debug("ReqTraceability.downstream() -> %d %s objects", len(_downstream_req_refs), qualname(ReqTraceability.Downstream.ReqRef))
        return _downstream_req_refs

    def writedownstream(
            self,
            downstream_traceability,  # type: ReqDownstreamTraceabilityType
            outfile,  # type: _PathType
    ):  # type: (...) -> None
        self.info(f"Saving downstream traceability in '{outfile}'")

        self._writejson(
            # Build a JSON content from the computed traceability.
            json_content=ReqTraceability.Downstream.tojson(downstream_traceability),
            # Save it to the given outfile.
            schema_subpath="schema/downstream-traceability.schema.json",
            outfile=outfile,
        )

    class Upstream(abc.ABC):

        @staticmethod
        def tojson(
                upstream_traceability,  # type: ReqUpstreamTraceabilityType
        ):  # type: (...) -> _JsonDictType
            _json = {}  # type: _JsonDictType
            for _upstream_scenario in upstream_traceability:  # type: ReqTraceability.Upstream.Scenario
                _json[_upstream_scenario.scenario.name] = _upstream_scenario.tojson()
            return _json

        class Scenario:
            def __init__(
                    self,
                    scenario,  # type: _ScenarioDefinitionType
            ):  # type: (...) -> None
                self.scenario = scenario  # type: _ScenarioDefinitionType
                self.reqs = []  # type: typing.List[ReqTraceability.Upstream.Req]

            def tojson(self):  # type: (...) -> _JsonDictType
                _json_scenario = {
                    "name": self.scenario.name,
                    "reqs": {},
                }  # type: _JsonDictType

                if self.scenario.title:
                    _json_scenario["title"] = self.scenario.title

                for _upstream_req in self.reqs:  # type: ReqTraceability.Upstream.Req
                    _json_scenario["reqs"][_upstream_req.req.id] = _upstream_req.tojson()

                return _json_scenario

        class Req:
            def __init__(
                    self,
                    upstream_scenario,  # type: ReqTraceability.Upstream.Scenario
                    req,  # type: _ReqType
                    req_link,  # type: typing.Optional[_ReqLinkType]
            ):  # type: (...) -> None
                self.upstream_scenario = upstream_scenario  # type: ReqTraceability.Upstream.Scenario
                self.req = req  # type: _ReqType
                self.req_link = req_link  # type: typing.Optional[_ReqLinkType]
                self.req_subrefs = []  # type: typing.List[ReqTraceability.Upstream.ReqSubref]
                self.comments = ""  # type: str

                if req_link:
                    self.comments = req_link.comments or self.upstream_scenario.scenario.title

                self.upstream_scenario.reqs.append(self)

            def tojson(self):  # type: (...) -> _JsonDictType
                _json_req = {
                    "id": self.req.id,
                    "comments": self.comments,
                    "subrefs": {},
                }  # type: _JsonDictType

                if self.req.title:
                    _json_req["title"] = self.req.title
                # Don't repeat text with requirements in upstream traceability reports.
                # if self.req.text:
                #     _json_req["text"] = self.req.text

                for _upstream_req_subref in self.req_subrefs:  # type: ReqTraceability.Upstream.ReqSubref
                    _json_req["subrefs"][_upstream_req_subref.req_subref.id] = _upstream_req_subref.tojson()

                return _json_req

        class ReqSubref:
            def __init__(
                    self,
                    upstream_req,  # type: ReqTraceability.Upstream.Req
                    req_subref,  # type: _ReqRefType
                    req_link,  # type: _ReqLinkType
            ):  # type: (...) -> None
                self.upstream_req = upstream_req  # type: ReqTraceability.Upstream.Req
                if not req_subref.issubref():
                    raise ValueError(f"Invalid requirement subreference {req_subref!r}")
                self.req_subref = req_subref  # type: _ReqRefType
                self.req_link = req_link  # type: _ReqLinkType
                self.comments = req_link.comments or self.upstream_req.upstream_scenario.scenario.title  # type: str

                self.upstream_req.req_subrefs.append(self)

            def tojson(self):  # type: (...) -> _JsonDictType
                return {
                    "id": self.req_subref.id,
                    "comments": self.comments,
                }

    def getupstream(self):  # type: (...) -> ReqUpstreamTraceabilityType
        from ._reflection import qualname
        from ._reqref import ReqRef
        if typing.TYPE_CHECKING:
            from ._reqtypes import SetWithReqLinksType

        self.debug("ReqTraceability.upstream(): Computing upstream traceability from %d loaded scenarios", len(self.scenarios))
        _upstream_scenarios = []  # type: typing.List[ReqTraceability.Upstream.Scenario]
        for _scenario in self.scenarios:  # type: _ScenarioDefinitionType
            _upstream_scenario = ReqTraceability.Upstream.Scenario(scenario=_scenario)  # type: ReqTraceability.Upstream.Scenario
            _upstream_scenarios.append(_upstream_scenario)

            _upstream_req = None  # type: typing.Optional[ReqTraceability.Upstream.Req]

            _req_ref_set = _scenario.getreqrefs(walk_steps=True)  # type: SetWithReqLinksType[_ReqRefType]
            for _req_ref in ReqRef.orderedset(_req_ref_set):  # type: _ReqRefType
                for _req_link in _req_ref_set[_req_ref]:  # type: _ReqLinkType
                    if _req_ref.ismain():
                        if (not _upstream_req) or (_upstream_req.req is not _req_ref.req):
                            _upstream_req = ReqTraceability.Upstream.Req(
                                _upstream_scenario,  # Memo: `_upstream_req` automatically added to `_upstream_scenario`.
                                req=_req_ref.req, req_link=_req_link,
                            )
                        else:
                            self.debug(
                                "%s -> %s already known through [%s], [%s] ignored",
                                _scenario, _req_ref.req, _upstream_req.req_link, _req_link,
                            )
                    else:
                        # Ensure the main requirement is set.
                        if (not _upstream_req) or (_upstream_req.req is not _req_ref.req):
                            _upstream_req = ReqTraceability.Upstream.Req(
                                _upstream_scenario,  # Memo: `_upstream_req` automatically added to `_upstream_scenario`.
                                req=_req_ref.req, req_link=None,
                            )
                        _upstream_req_subref = ReqTraceability.Upstream.ReqSubref(
                            _upstream_req,  # Memo: `_upstream_req_subref` automatically added to `_upstream_req`.
                            req_subref=_req_ref, req_link=_req_link,
                        )  # type: ReqTraceability.Upstream.ReqSubref

        self.debug("ReqTraceability.upstream() -> %d %s objects", len(_upstream_scenarios), qualname(ReqTraceability.Upstream.Scenario))
        return _upstream_scenarios

    def writeupstream(
            self,
            upstream_traceability,  # type: ReqUpstreamTraceabilityType
            outfile,  # type: _PathType
    ):  # type: (...) -> None
        self.info(f"Saving upstream traceability in '{outfile}'")

        self._writejson(
            # Build a JSON content from the computed traceability.
            json_content=ReqTraceability.Upstream.tojson(upstream_traceability),
            # Save it to the given outfile.
            schema_subpath="schema/upstream-traceability.schema.json",
            outfile=outfile,
        )

    def _writejson(
            self,
            json_content,  # type: _JsonDictType
            schema_subpath,  # type: str
            outfile,  # type: _PathType
    ):  # type: (...) -> None
        from ._pkginfo import PKG_INFO

        # Add meta information.
        json_content = dict(json_content)
        json_content.update({
            "$encoding": "utf-8",
            "$schema": f"https://github.com/alxroyer/scenario/blob/v{PKG_INFO.version}/{schema_subpath}",
            "$version": PKG_INFO.version,
        })

        outfile.parent.mkdir(parents=True, exist_ok=True)
        if outfile.suffix.lower() in (".json",):
            outfile.write_text(json.dumps(json_content, indent=2), encoding="utf-8")
        elif outfile.suffix.lower() in (".yml", ".yaml",):
            try:
                import yaml
            except ImportError as _err:
                raise EnvironmentError(_err)
            outfile.write_text(yaml.safe_dump(json_content), encoding="utf-8")
        else:
            raise ValueError(f"Unknown extension {outfile.suffix!r}")


if typing.TYPE_CHECKING:
    ReqDownstreamTraceabilityType = typing.Sequence[ReqTraceability.Downstream.ReqRef]
    ReqUpstreamTraceabilityType = typing.Sequence[ReqTraceability.Upstream.Scenario]


REQ_TRACEABILITY = ReqTraceability()  # type: ReqTraceability
