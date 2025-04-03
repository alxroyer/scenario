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
import typing

if True:
    from ._debugclasses import DebugClass as _DebugClassImpl  # @perf
    from ._fastpath import FAST_PATH as _FAST_PATH  # @perf
    from ._logger import Logger as _LoggerImpl  # @inheritance
    from ._reqblobj import ReqBaselineObject as _ReqBaselineObjectImpl  # @inheritance
    from ._reqref import ReqRef as _ReqRefImpl  # @perf
    from ._reqverifier import ReqVerifier as _ReqVerifierImpl  # @perf
    from ._scenariodefinition import ScenarioDefinition as _ScenarioDefinitionImpl  # @perf
    from ._stepdefinition import StepDefinition as _StepDefinitionImpl  # @perf
if typing.TYPE_CHECKING:
    from ._jsondictutils import JsonDictType as _JsonDictType
    from ._path import Path as _PathType
    from ._req import Req as _ReqType
    from ._reqbl import ReqBaseline as _ReqBaselineType
    from ._reqlink import ReqLink as _ReqLinkType
    from ._reqref import ReqRef as _ReqRefType
    from ._reqverifier import ReqVerifier as _ReqVerifierType
    from ._scenariodefinition import ScenarioDefinition as _ScenarioDefinitionType
    from ._stepdefinition import StepDefinition as _StepDefinitionType
    from ._stepexecution import StepExecution as _StepExecutionType


class ReqTraceability(_LoggerImpl, _ReqBaselineObjectImpl):
    """
    Requirement traceability computation.
    """

    def __init__(
            self,
            req_baseline,  # type: _ReqBaselineType
    ):  # type: (...) -> None
        """
        Stores the related baseline reference and configures logging for :class:`ReqTraceability`.

        :param req_baseline: Requirement baseline to compute traceability for.
        """
        _LoggerImpl.__init__(self, _DebugClassImpl.REQ_TRACEABILITY)
        _ReqBaselineObjectImpl.__init__(self, req_baseline)

    class Downstream(abc.ABC):
        """
        Classes that describe a downstream traceability.

        Downstream traceability is a matrix starting with requirement references, verified by scenarios and steps.
        """

        #: JSON schema subpath from :attr:`._pkginfo.PackageInfo.repo_url`, for downstream traceability reports.
        JSON_SCHEMA_SUBPATH = "schemas/downstream-traceability.schema.json"  # type: str

        @staticmethod
        def tojson(
                downstream_traceability,  # type: ReqDownstreamTraceabilityType
                *,
                allow_results=True,  # type: bool
        ):  # type: (...) -> _JsonDictType
            """
            JSON content generation for a downstream traceability.

            :param downstream_traceability: Downstream traceability to generate JSON content for.
            :param allow_results: ``False`` to prevent test results in the JSON content.
            :return: Downstream traceability JSON content.
            """
            _json = {}  # type: _JsonDictType
            for _downstream_req_ref in downstream_traceability:  # type: ReqTraceability.Downstream.ReqRef
                _json[_downstream_req_ref.req_ref.id] = _downstream_req_ref.tojson(allow_results=allow_results)
                # Remove `ReqTraceability.Downstream.ReqRef` id field, already given as the key entry.
                del _json[_downstream_req_ref.req_ref.id]["id"]
            return _json

        class ReqRef:
            """
            Main entry for downstream traceability.

            Either a main requirement reference, or a subreference.
            """

            def __init__(
                    self,
                    req_ref,  # type: _ReqRefType
            ):  # type: (...) -> None
                """
                Builds a :class:`ReqTraceability.Downstream.ReqRef` instance with related information.

                :param req_ref: Starting requirement reference.
                """
                #: Starting requirement reference, verified by scenarios or not.
                self.req_ref = req_ref  # type: _ReqRefType
                #: Scenarios verifying this requirement reference.
                self.scenarios = []  # type: typing.List[ReqTraceability.Downstream.Scenario]

            def tojson(
                    self,
                    *,
                    allow_results,  # type: bool
            ):  # type: (...) -> _JsonDictType
                """
                Downstream traceability JSON content generation for this requirement reference.

                :param allow_results: ``False`` to prevent test results in the JSON content generated.
                :return: Downstream traceability JSON content.
                """
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
                    _json_req_ref["scenarios"][_downstream_scenario.id] = _downstream_scenario.tojson(allow_results=allow_results)
                    # Remove `ReqTraceability.Downstream.Scenario` name field, already given as the key entry.
                    del _json_req_ref["scenarios"][_downstream_scenario.id]["name"]

                return _json_req_ref

        class Scenario:
            """
            Scenario verifying a :class:`ReqTraceability.Downstream.ReqRef`.

            .. note::
                Several instances of :class:`ReqTraceability.Downstream.Scenario` may exist for a single :class:`._scenariodefinition.ScenarioDefinition`.
                One for each requirement reference verified by the scenario (directly or through one of the scenario steps).
            """

            def __init__(
                    self,
                    downstream_req_ref,  # type: ReqTraceability.Downstream.ReqRef
                    scenario,  # type: _ScenarioDefinitionType
                    req_link,  # type: typing.Optional[_ReqLinkType]
            ):  # type: (...) -> None
                """
                Builds a :class:`ReqTraceability.Downstream.Scenario` instance with related information.

                :param downstream_req_ref:
                    Requirement reference verified.
                :param scenario:
                    Scenario definition.
                :param req_link:
                    Related requirement link.

                    May be ``None`` when the requirement reference is verified indirectly through steps only.
                """
                #: Requirement reference verified by the scenario.
                self.downstream_req_ref = downstream_req_ref  # type: ReqTraceability.Downstream.ReqRef
                #: Scenario verifying the given requirement reference.
                self.scenario = scenario  # type: _ScenarioDefinitionType
                #: Optional direct link between the scenario and the requirement reference.
                #:
                #: May be ``None`` when the scenario verifies the requirement reference through one of its steps only.
                self.req_link = req_link  # type: typing.Optional[_ReqLinkType]
                #: Steps owned by the scenario, and verifying the given requirement reference.
                self.steps = []  # type: typing.List[ReqTraceability.Downstream.Step]

                self.downstream_req_ref.scenarios.append(self)

            @property
            def id(self):  # type: () -> str
                """
                Scenario identifier in traceability results.

                .. seealso:: :meth:`ReqTraceabilityHelper.mkscenarioid()`
                """
                return ReqTraceabilityHelper.mkscenarioid(self.scenario)

            @property
            def name(self):  # type: () -> str
                """
                Scenario display name in traceability results.

                .. seealso:: :meth:`ReqTraceabilityHelper.mkscenarioid()`
                """
                return ReqTraceabilityHelper.mkscenarioname(self.scenario)

            @property
            def explicit_comments(self):  # type: () -> str
                """
                Explicit requirement coverage comments, if defined by the requirement link.
                """
                if self.req_link:
                    return self.req_link.comments
                return ""

            @property
            def display_comments(self):  # type: () -> str
                """
                Comments explaining the requirement coverage made by this scenario.

                Empty when no requirement link is provided,
                to let steps explain the requirement coverage.

                When the requirement link provided does not define explicit comments,
                the scenario title is taken into account by default.
                """
                # Let steps explain the coverage when no requirement link is provided.
                if self.req_link is None:
                    return ""

                # Explicit comments if provided.
                if self.req_link.comments:
                    return self.req_link.comments

                # Default to scenario title.
                return self.scenario.title

            def tojson(
                    self,
                    *,
                    allow_results,  # type: bool
            ):  # type: (...) -> _JsonDictType
                """
                Downstream traceability JSON content generation for this scenario.

                :param allow_results: ``False`` to prevent test results in the JSON content generated.
                :return: Downstream traceability JSON content.
                """
                _json_scenario = {
                    "id": self.id,
                    "name": self.name,
                    "title": self.scenario.title,
                    "comments": self.explicit_comments,
                    "steps": {},
                }  # type: _JsonDictType

                if allow_results and (self.scenario.execution is not None):
                    _json_scenario["results"] = {
                        "status": str(self.scenario.execution.status),
                        "errors": [str(_error) for _error in self.scenario.execution.errors],
                        "warnings": [str(_warning) for _warning in self.scenario.execution.warnings],
                    }

                for _downstream_step in self.steps:  # type: ReqTraceability.Downstream.Step
                    _json_scenario["steps"][f"step#{_downstream_step.step.number}"] = _downstream_step.tojson(allow_results=allow_results)
                    # Remove `ReqTraceability.Downstream.Step` number field, already given with the key entry.
                    del _json_scenario["steps"][f"step#{_downstream_step.step.number}"]["number"]

                # Remove optional information when empty.
                ReqTraceabilityHelper.removeemptyjsonfields(
                    _json_scenario,
                    ["title", "comments", "steps"],
                )

                return _json_scenario

        class Step:
            """
            Scenario verifying an initial :class:`ReqTraceability.Downstream.ReqRef`.

            .. note::
                Several instances of :class:`ReqTraceability.Downstream.Step` may exist for a single :class:`._stepdefinition.StepDefinition`.
                One for each requirement reference verified by the step.
            """

            def __init__(
                    self,
                    downstream_scenario,  # type: ReqTraceability.Downstream.Scenario
                    step,  # type: _StepDefinitionType
                    req_link,  # type: _ReqLinkType
            ):  # type: (...) -> None
                """
                Builds a :class:`ReqTraceability.Downstream.Step` instance with related information.

                :param downstream_scenario: Owner scenario.
                :param step: Step definition.
                :param req_link: Related requirement link.
                """
                #: Scenario owning this step.
                self.downstream_scenario = downstream_scenario  # type: ReqTraceability.Downstream.Scenario
                #: Step verifying the requirement reference verified by :attr:`downstream_scenario`.
                self.step = step  # type: _StepDefinitionType
                #: Link between the step and the requirement reference.
                self.req_link = req_link  # type: _ReqLinkType

                self.downstream_scenario.steps.append(self)

            @property
            def id(self):  # type: () -> str
                """
                Step identifier in traceability results.

                .. seealso:: :meth:`ReqTraceabilityHelper.mkstepid()`
                """
                return ReqTraceabilityHelper.mkstepid(self.step)

            @property
            def name(self):  # type: () -> str
                """
                Step display name in traceability results.

                .. seealso:: :meth:`ReqTraceabilityHelper.mkstepname()`
                """
                return ReqTraceabilityHelper.mkstepname(self.step)

            @property
            def explicit_comments(self):  # type: () -> str
                """
                Explicit requirement coverage comments, if defined by the requirement link.
                """
                return self.req_link.comments

            @property
            def display_comments(self):  # type: () -> str
                """
                Comments explaining the requirement coverage made by this step.

                When the requirement link does not define explicit comments,
                the owner scenario title and/or step description are taken into account by default.
                """
                # Explicit comments if provided.
                if self.req_link.comments:
                    return self.req_link.comments

                # Compute default comments from scenario title and/or step description.
                _comments = []  # type: typing.List[str]
                if self.downstream_scenario.scenario.title:
                    _comments.append(self.downstream_scenario.scenario.title)
                if self.step.description:
                    _comments.append(self.step.description)
                return " - ".join(_comments)

            def tojson(
                    self,
                    *,
                    allow_results,  # type: bool
            ):  # type: (...) -> _JsonDictType
                """
                Downstream traceability JSON content generation for this step.

                :param allow_results: ``False`` to prevent test results in the JSON content generated.
                :return: Downstream traceability JSON content.
                """
                _json_step = {
                    "id": self.id,
                    "number": self.step.number,
                    "name": self.name,
                    "comments": self.explicit_comments,
                }  # type: _JsonDictType

                # Note:
                #  Don't generate test results for an empty step execution list
                #  if the scenario has not been executed at all.
                if allow_results and (self.step.scenario.execution is not None):
                    _json_step["results"] = []
                    for _step_execution in self.step.executions:  # type: _StepExecutionType
                        _json_step["results"].append({
                            "status": str(_step_execution.status),
                            "errors": [str(_error) for _error in _step_execution.errors],
                            "warnings": [str(_warning) for _warning in _step_execution.warnings],
                        })

                # Remove optional information when empty.
                ReqTraceabilityHelper.removeemptyjsonfields(
                    _json_step,
                    ["comments"],
                )

                return _json_step

    def getdownstream(
            self,
            *,
            walk_subrefs,  # type: bool
    ):  # type: (...) -> ReqDownstreamTraceabilityType
        """
        Computes downstream traceability from the related baseline.

        :param walk_subrefs:
            ``True`` to include subreference verifiers for main requirements.
        :return:
            Downstream traceability.

            Main and subreference requirement entries given whatever they are verified or not.
        """
        if typing.TYPE_CHECKING:
            from ._reqtypes import SetWithReqLinksType

        _all_req_refs = self.req_db.getallrefs()  # type: typing.Sequence[_ReqRefType]
        self.debug("ReqTraceability.getdownstream(): Computing downstream traceability from %d requirement references", len(_all_req_refs))
        _downstream_req_refs = []  # type: typing.List[ReqTraceability.Downstream.ReqRef]
        for _req_ref in _all_req_refs:  # type: _ReqRefType
            _downstream_req_ref = ReqTraceability.Downstream.ReqRef(req_ref=_req_ref)  # type: ReqTraceability.Downstream.ReqRef

            _downstream_scenario = None  # type: typing.Optional[ReqTraceability.Downstream.Scenario]

            _req_verifiers_set = (
                _req_ref.req.getverifiers(walk_subrefs=walk_subrefs) if _req_ref.ismain()
                else _req_ref.getverifiers()
            )  # type: SetWithReqLinksType[_ReqVerifierType]
            for _req_verifier in _ReqVerifierImpl.orderedset(_req_verifiers_set):  # type: _ReqVerifierType
                for _req_link in _req_verifiers_set[_req_verifier]:  # type: _ReqLinkType
                    if isinstance(_req_verifier, _ScenarioDefinitionImpl):
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
                    elif isinstance(_req_verifier, _StepDefinitionImpl):
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

            # Save requirement reference entry in any case, even though no downstream traceability information.
            _downstream_req_refs.append(_downstream_req_ref)

        self.debug("ReqTraceability.downstream() -> %d %s objects",
                   len(_downstream_req_refs), _FAST_PATH.reflection.qualname(ReqTraceability.Downstream.ReqRef))
        return _downstream_req_refs

    def writedownstream(
            self,
            outfile,  # type: _PathType
            downstream_traceability=None,  # type: ReqDownstreamTraceabilityType
            *,
            log_info=True,  # type: bool
            allow_results=True,  # type: bool
    ):  # type: (...) -> None
        """
        Writes downstream tracebility to a file.

        :param outfile:
            Path of the file to write.
        :param downstream_traceability:
            Downtream traceability to save into a file.

            Automatically computed when not set.
        :param log_info:
            ``True`` (by default) to generate info logging.
        :param allow_results:
            ``False`` to prevent test results in the downstream traceability report.
        """
        from ._jsondictutils import JsonDict

        if log_info:
            _FAST_PATH.main_logger.info(f"Saving downstream traceability in '{outfile}'")

        # Automatically compute upstream tracebility if needed.
        if downstream_traceability is None:
            downstream_traceability = self.getdownstream(walk_subrefs=False)

        JsonDict.writefile(
            # Build a JSON content from the computed traceability.
            schema_subpath=ReqTraceability.Downstream.JSON_SCHEMA_SUBPATH,
            content=ReqTraceability.Downstream.tojson(downstream_traceability, allow_results=allow_results),
            # Save it to the given outfile.
            output_path=outfile,
        )

    class Upstream(abc.ABC):
        """
        Classes that describe an upstream traceability.

        Upstream traceability is a matrix starting with scenarios and steps, verifying requirements and/or subreferences.
        """

        #: JSON schema subpath from :attr:`._pkginfo.PackageInfo.repo_url`, for upstream traceability reports.
        JSON_SCHEMA_SUBPATH = "schemas/upstream-traceability.schema.json"  # type: str

        @staticmethod
        def tojson(
                upstream_traceability,  # type: ReqUpstreamTraceabilityType
        ):  # type: (...) -> _JsonDictType
            """
            JSON content generation for an upstream traceability.

            :param upstream_traceability: Upstream traceability to generate JSON content for.
            :return: Upstream traceability JSON content.
            """
            _json = {}  # type: _JsonDictType
            for _upstream_req_verifier in upstream_traceability:  # type: ReqTraceability.Upstream.ReqVerifier
                _json[_upstream_req_verifier.id] = _upstream_req_verifier.tojson()
            return _json

        class ReqVerifier:
            """
            Main entry for upstream traceability.
            """

            def __init__(
                    self,
                    req_verifier,  # type: typing.Union[_ScenarioDefinitionType, _StepDefinitionType]
            ):  # type: (...) -> None
                """
                Builds a :class:`ReqTraceability.Upstream.ReqVerifier` instance with related information.

                :param req_verifier: Starting scenario or step.
                """
                #: Starting scenario or step, verifying requirements or not.
                self.req_verifier = req_verifier  # type: typing.Union[_ScenarioDefinitionType, _StepDefinitionType]
                #: Requirements verified by the scenario.
                self.reqs = []  # type: typing.List[ReqTraceability.Upstream.Req]

            @property
            def id(self):  # type: () -> str
                """
                Identifier in traceability results.

                .. seealso:: :meth:`ReqTraceabilityHelper.mkscenarioid()`
                .. seealso:: :meth:`ReqTraceabilityHelper.mkstepid()`
                """
                if isinstance(self.req_verifier, _ScenarioDefinitionImpl):
                    return ReqTraceabilityHelper.mkscenarioid(self.req_verifier)
                else:
                    return ReqTraceabilityHelper.mkstepid(self.req_verifier)

            @property
            def name(self):  # type: () -> str
                """
                Display name in traceability results.

                .. seealso:: :meth:`ReqTraceabilityHelper.mkscenarioname()`
                .. seealso:: :meth:`ReqTraceabilityHelper.mkstepname()`
                """
                if isinstance(self.req_verifier, _ScenarioDefinitionImpl):
                    return ReqTraceabilityHelper.mkscenarioname(self.req_verifier)
                else:
                    return ReqTraceabilityHelper.mkstepname(self.req_verifier)

            def tojson(self):  # type: (...) -> _JsonDictType
                """
                Upstream traceability JSON content generation for this scenario or step.

                :return: Upstream traceability JSON content.
                """
                _json_req_verifier = {
                    "id": self.id,
                    "name": self.name,
                    "reqs": {},
                }  # type: _JsonDictType

                if isinstance(self.req_verifier, _ScenarioDefinitionImpl):
                    _json_req_verifier["type"] = "scenario"

                    if self.req_verifier.title:
                        _json_req_verifier["title"] = self.req_verifier.title

                if isinstance(self.req_verifier, _StepDefinitionImpl):
                    _json_req_verifier["type"] = "step"

                    if self.req_verifier.description:
                        _json_req_verifier["description"] = self.req_verifier.description

                for _upstream_req in self.reqs:  # type: ReqTraceability.Upstream.Req
                    _json_req_verifier["reqs"][_upstream_req.req.id] = _upstream_req.tojson()
                    # Remove `ReqTraceability.Upstream.Req` id field, already given as the key entry.
                    del _json_req_verifier["reqs"][_upstream_req.req.id]["id"]

                return _json_req_verifier

        class Req:
            """
            Main requirement verified by a :class:`ReqTraceability.Upstream.ReqVerifier`.

            Either directly, or through the scenario steps.

            .. note::
                Several instances of :class:`ReqTraceability.Upstream.Req` may exist for a single :class:`._req.Req`.
                One for each scenario verifying the requirement (directly or through one of the requirement subreferences).
            """

            def __init__(
                    self,
                    upstream_req_verifier,  # type: ReqTraceability.Upstream.ReqVerifier
                    req,  # type: _ReqType
                    req_link,  # type: typing.Optional[_ReqLinkType]
            ):  # type: (...) -> None
                """
                Builds a :class:`ReqTraceability.Upstream.Req` instance with related information.

                :param upstream_req_verifier:
                    Scenario or step verifying this requirement.
                :param req:
                    Requirement.
                :param req_link:
                    Related requirement link.

                    May be ``None`` when the verifies subreferences of the requirement only, but not the main part.
                """
                #: Scenario or step verifying the requirement.
                self.upstream_req_verifier = upstream_req_verifier  # type: ReqTraceability.Upstream.ReqVerifier
                #: Requirement (main part) verified by the scenario.
                self.req = req  # type: _ReqType
                #: Optional direct link between the scenario (or one of its steps) and the requirement.
                #:
                #: May be ``None`` when the scenario verifies subreferences only, but not the main part of the requirement.
                self.req_link = req_link  # type: typing.Optional[_ReqLinkType]
                #: Subreferences of the requirement, verified by the given scenario.
                self.req_subrefs = []  # type: typing.List[ReqTraceability.Upstream.ReqSubref]

                self.upstream_req_verifier.reqs.append(self)

            @property
            def explicit_comments(self):  # type: () -> str
                """
                Explicit requirement coverage comments, if defined by the requirement link.
                """
                if self.req_link:
                    return self.req_link.comments
                return ""

            @property
            def display_comments(self):  # type: () -> str
                """
                Comments explaining the coverage of this requirement.

                Empty when no requirement link is provided,
                to let subrefs explain the requirement coverage.

                When the requirement link provided does not define explicit comments,
                the requirement title is taken into account by default.
                """
                # Let subrefs explain the coverage when no requirement link is provided.
                if self.req_link is None:
                    return ""

                # Explicit comments if provided.
                if self.req_link.comments:
                    return self.req_link.comments

                # Default to requirement title.
                return self.req.title

            def tojson(self):  # type: (...) -> _JsonDictType
                """
                Upstream traceability JSON content generation for this requirement.

                :return: Upstream traceability JSON content.
                """
                _json_req = {
                    "id": self.req.id,
                    "title": self.req.title,
                    # Don't repeat text with requirements in upstream traceability reports.
                    # "text": self.req.text,
                    "comments": self.explicit_comments,
                    "subrefs": {},
                }  # type: _JsonDictType

                for _upstream_req_subref in self.req_subrefs:  # type: ReqTraceability.Upstream.ReqSubref
                    _json_req["subrefs"][_upstream_req_subref.req_subref.id] = _upstream_req_subref.tojson()
                    # Remove `ReqTraceability.Upstream.ReqSubref` id field, already given as the key entry.
                    del _json_req["subrefs"][_upstream_req_subref.req_subref.id]["id"]

                # Remove optional information when empty.
                ReqTraceabilityHelper.removeemptyjsonfields(
                    _json_req,
                    ["title", "text", "comments", "subrefs"],
                )

                return _json_req

        class ReqSubref:
            """
            Requirement subreference verified by an initial :class:`ReqTraceability.Upstream.ReqVerifier`.

            .. note::
                Several instances of :class:`ReqTraceability.Upstream.ReqSubref` may exist for a single :class:`._reqref.ReqRef`.
                One for each scenario verifying the requirement subreference.
            """

            def __init__(
                    self,
                    upstream_req,  # type: ReqTraceability.Upstream.Req
                    req_subref,  # type: _ReqRefType
                    req_link,  # type: _ReqLinkType
            ):  # type: (...) -> None
                """
                Builds a :class:`ReqTraceability.Upstream.ReqSubref` instance with related information.

                :param upstream_req: Owner requirement.
                :param req_subref: Requirement subreference.
                :param req_link: Related requirement link.
                """
                #: Requirement owning this subreference.
                self.upstream_req = upstream_req  # type: ReqTraceability.Upstream.Req
                if not req_subref.issubref():
                    raise ValueError(f"Invalid requirement subreference {req_subref!r}")
                #: Requirement subreference verified by the scenario verifying :attr:`upstream_req`.
                self.req_subref = req_subref  # type: _ReqRefType
                #: Link between the scenario (or one of its steps) and the requirement subreference.
                self.req_link = req_link  # type: _ReqLinkType

                self.upstream_req.req_subrefs.append(self)

            @property
            def explicit_comments(self):  # type: () -> str
                """
                Explicit requirement subref coverage comments, if defined by the requirement link.
                """
                return self.req_link.comments

            @property
            def display_comments(self):  # type: () -> str
                """
                Comments explaining the coverage of this requirement subref.

                When the requirement link does not define explicit comments,
                the requirement subref title is taken into account by default.
                """
                # Explicit comments if provided.
                if self.req_link.comments:
                    return self.req_link.comments

                # Default to requirement subref title.
                return self.req_subref.title

            def tojson(self):  # type: (...) -> _JsonDictType
                """
                Upstream traceability JSON content generation for this requirement subreference.

                :return: Upstream traceability JSON content.
                """
                _json_req_subref = {
                    "id": self.req_subref.id,
                    # In the future, requirement subrefs may hold their own title and text.
                    # Currently, title is just computed from the main requirement title.
                    # Whatever, let's save it in reports as is to avoid subref dictionaries.
                    "title": self.req_subref.title,
                    # "text": ...,
                    "comments": self.explicit_comments,
                }  # type: _JsonDictType

                # Remove optional information when empty.
                ReqTraceabilityHelper.removeemptyjsonfields(
                    _json_req_subref,
                    ["title", "text", "comments"],
                )

                return _json_req_subref

    def getupstream(
            self,
            *,
            walk_steps,  # type: bool
    ):  # type: (...) -> ReqUpstreamTraceabilityType
        """
        Computes upstream traceability for the related baseline.

        :param walk_steps:
            ``True`` to include step requirement references for scenarios.
        :return:
            Upstream traceability.

            Scenario entries given even when verifying no requirement.
            Step entries given only when verifying requirements.
        """
        if typing.TYPE_CHECKING:
            from ._reqtypes import SetWithReqLinksType

        self.debug("ReqTraceability.upstream(): Computing upstream traceability from %d scenarios", len(self.req_baseline.scenarios))

        _all_req_verifiers = []  # type: typing.List[typing.Union[_ScenarioDefinitionType, _StepDefinitionType]]
        for _scenario in self.req_baseline.scenarios:  # type: _ScenarioDefinitionType
            _all_req_verifiers.append(_scenario)
            _all_req_verifiers.extend(_scenario.steps)

        _upstream_req_verifiers = []  # type: typing.List[ReqTraceability.Upstream.ReqVerifier]
        for _req_verifier in _all_req_verifiers:  # type: typing.Union[_ScenarioDefinitionType, _StepDefinitionType]
            _upstream_req_verifier = ReqTraceability.Upstream.ReqVerifier(req_verifier=_req_verifier)  # type: ReqTraceability.Upstream.ReqVerifier

            _upstream_req = None  # type: typing.Optional[ReqTraceability.Upstream.Req]

            _req_ref_set = (
                _req_verifier.getreqrefs(walk_steps=walk_steps) if isinstance(_req_verifier, _ScenarioDefinitionImpl)
                else _req_verifier.getreqrefs()
            )  # type: SetWithReqLinksType[_ReqRefType]
            for _req_ref in _ReqRefImpl.orderedset(_req_ref_set):  # type: _ReqRefType
                for _req_link in _req_ref_set[_req_ref]:  # type: _ReqLinkType
                    if _req_ref.ismain():
                        if (not _upstream_req) or (_upstream_req.req is not _req_ref.req):
                            _upstream_req = ReqTraceability.Upstream.Req(
                                _upstream_req_verifier,  # Memo: `_upstream_req` automatically added to `_upstream_req_verifier`.
                                req=_req_ref.req, req_link=_req_link,
                            )
                        else:
                            self.debug(
                                "%s -> %s already known through [%s], [%s] ignored",
                                _req_verifier, _req_ref.req, _upstream_req.req_link, _req_link,
                            )
                    else:
                        # Ensure the main requirement is set.
                        if (not _upstream_req) or (_upstream_req.req is not _req_ref.req):
                            _upstream_req = ReqTraceability.Upstream.Req(
                                _upstream_req_verifier,  # Memo: `_upstream_req` automatically added to `_upstream_req_verifier`.
                                req=_req_ref.req, req_link=None,
                            )
                        # Check the main requirement does not already have the given subref.
                        # This may happen when both the scenario and one of its steps cover the same subref.
                        if _req_ref not in [_upstream_req_subref.req_subref for _upstream_req_subref in _upstream_req.req_subrefs]:
                            _upstream_req_subref = ReqTraceability.Upstream.ReqSubref(
                                _upstream_req,  # Memo: `_upstream_req_subref` automatically added to `_upstream_req`.
                                req_subref=_req_ref, req_link=_req_link,
                            )  # type: ReqTraceability.Upstream.ReqSubref

            # Avoid step entries without upstream traceability information.
            if isinstance(_req_verifier, _ScenarioDefinitionImpl) or _upstream_req_verifier.reqs:
                _upstream_req_verifiers.append(_upstream_req_verifier)

        self.debug("ReqTraceability.upstream() -> %d %s objects",
                   len(_upstream_req_verifiers), _FAST_PATH.reflection.qualname(ReqTraceability.Upstream.ReqVerifier))
        return _upstream_req_verifiers

    def writeupstream(
            self,
            outfile,  # type: _PathType
            upstream_traceability=None,  # type: ReqUpstreamTraceabilityType
            *,
            log_info=True,  # type: bool
    ):  # type: (...) -> None
        """
        Writes upstream tracebility to a file.

        :param outfile:
            Path of the file to write.
        :param upstream_traceability:
            Upstream traceability to save into a file.

            Automatically computed when not set.
        :param log_info:
            ``True`` (by default) to generate info logging.
        """
        from ._jsondictutils import JsonDict

        if log_info:
            _FAST_PATH.main_logger.info(f"Saving upstream traceability in '{outfile}'")

        # Automatically compute upstream tracebility if needed.
        if upstream_traceability is None:
            upstream_traceability = self.getupstream(walk_steps=False)

        JsonDict.writefile(
            # Build a JSON content from the computed traceability.
            schema_subpath=ReqTraceability.Upstream.JSON_SCHEMA_SUBPATH,
            content=ReqTraceability.Upstream.tojson(upstream_traceability),
            # Save it to the given outfile.
            output_path=outfile,
        )


if typing.TYPE_CHECKING:
    #: Downstream traceability type.
    #:
    #: Sequence of :class:`ReqTraceability.Downstream.ReqRef` instances,
    #: each owning a sequence of :class:`ReqTraceability.Downstream.Scenario` instances,
    #: each possibly owning :class:`ReqTraceability.Downstream.Step` instances.
    ReqDownstreamTraceabilityType = typing.Sequence[ReqTraceability.Downstream.ReqRef]

    #: Upstream traceability type.
    #:
    #: Sequence of :class:`ReqTraceability.Upstream.ReqVerifier` instances,
    #: each owning a sequence of :class:`ReqTraceability.Upstream.Req` instances,
    #: each possibly owning :class:`ReqTraceability.Upstream.ReqSubref` instances.
    ReqUpstreamTraceabilityType = typing.Sequence[ReqTraceability.Upstream.ReqVerifier]


class ReqTraceabilityHelper(abc.ABC):
    """
    Requirement traceability helper methods.

    Avoids the public exposition of methods for internal implementation only.
    """

    @staticmethod
    def mkscenarioid(
            scenario,  # type: _ScenarioDefinitionType
    ):  # type: (...) -> str
        """
        Common implementation for :attr:`ReqTraceability.Downstream.Scenario.id` and :attr:`ReqTraceability.Upstream.ReqVerifier.id` properties.

        Scenario name.

        :param scenario: Scenario definition to compute an identifier for.
        :return: Identifier for the scenario in tracebility results.
        """
        return scenario.name

    @staticmethod
    def mkscenarioname(
            scenario,  # type: _ScenarioDefinitionType
    ):  # type: (...) -> str
        """
        Common implementation for :attr:`ReqTraceability.Downstream.Scenario.name` and :attr:`ReqTraceability.Upstream.ReqVerifier.name` properties.

        Scenario name.

        :param scenario: Scenario definition to compute a name for.
        :return: Name for the scenario in tracebility results.
        """
        return scenario.name

    @staticmethod
    def mkstepid(
            step,  # type: _StepDefinitionType
    ):  # type: (...) -> str
        """
        Common implementation for :attr:`ReqTraceability.Downstream.Step.id` and :attr:`ReqTraceability.Upstream.ReqVerifier.id` properties.

        "<scenario name>step#<number>" pattern.

        :param step: Step definition to compute an identifier for.
        :return: Identifier for the step in tracebility results.
        """
        return f"{ReqTraceabilityHelper.mkscenarioid(step.scenario)}/step#{step.number}"

    @staticmethod
    def mkstepname(
            step,  # type: _StepDefinitionType
    ):  # type: (...) -> str
        """
        Common implementation for :attr:`ReqTraceability.Downstream.Step.name` and :attr:`ReqTraceability.Upstream.ReqVerifier.name` properties.

        "step#<number> (<class>)" pattern.

        :param step: Step definition to compute a name for.
        :return: Name for the step in tracebility results.
        """
        return f"step#{step.number} ({step.name})"

    @staticmethod
    def removeemptyjsonfields(
            json,  # type: _JsonDictType
            fields,  # type: typing.Sequence[str]
    ):  # type: (...) -> None
        """
        Removes empty fields from a JSON dictionary.

        :param json: JSON dictionary to remove fields from.
        :param fields: Field names to remove if empty. Field names may be not existing in ``json``.
        """
        for _key in fields:  # type: str
            if (_key in json) and (not json[_key]):
                del json[_key]
