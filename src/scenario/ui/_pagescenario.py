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
User interface scenario details page.
"""

import typing

import scenario

if True:
    from ._httprequesthandler import HttpRequestHandler as _HttpRequestHandlerImpl  # @inheritance
if typing.TYPE_CHECKING:
    from ._htmldoc import HtmlDocument as _HtmlDocumentType
    from ._htmlgenlists import ListGenerator as _ListGeneratorType
    from ._htmlgentypes import CollapsibleState as _CollapsibleStateType
    from ._httprequest import HttpRequest as _HttpRequestType


class ScenarioPage(_HttpRequestHandlerImpl):
    """
    Scenario details page.
    """

    #: Base URL for the scenario details page.
    _URL = "/scenario"  # type: str

    @staticmethod
    def mkurl(
            req_verifier,  # type: typing.Union[scenario.ScenarioDefinition, scenario.StepDefinition]
    ):  # type: (...) -> str
        """
        Builds a scenario details URL for the given scenario.

        :param req_verifier: Scenario or step to build the URL for.
        :return: Scenario details URL for the given scenario.
        """
        from ._httprequest import HttpRequest

        _scenario = req_verifier if isinstance(req_verifier, scenario.ScenarioDefinition) else req_verifier.scenario  # type: scenario.ScenarioDefinition

        _step_anchor = None  # type: typing.Optional[str]
        if isinstance(req_verifier, scenario.StepDefinition):
            _step_anchor = f"step-{req_verifier.number}"

        return HttpRequest.encodeurl(
            ScenarioPage._URL,
            args={
                **HttpRequest.mkurlargs(obj=_scenario),
                "name": _scenario.name,
            },
            anchor=_step_anchor,
        )

    def __init__(self):  # type: (...) -> None
        """
        Configures the logger instance.
        """
        from ._debugclasses import UIDebugClass

        _HttpRequestHandlerImpl.__init__(self, UIDebugClass.PAGE_SCENARIO)

    def _getscenario(
            self,
            request,  # type: _HttpRequestType
    ):  # type: (...) -> scenario.ScenarioDefinition
        """
        Retrieves the scenario instance with details.

        Ensures steps are executed at once to build actions and expected results.

        :param request: Input request.
        :return: Scenario found from its name.
        """
        from ._reqbl import UI_REQ_BASELINES

        # Retrieve the scenario name from request arguments.
        _scenario_name = request.getarg("name")  # type: str
        self.debug("Scenario name: %r", _scenario_name)

        # Search for the scenario in the loaded scenarios.
        for _scenario_definition in request.req_baseline.scenarios:  # type: scenario.ScenarioDefinition
            if _scenario_definition.name == _scenario_name:
                # Scenario found.
                UI_REQ_BASELINES.checkscenarioloaded(_scenario_definition)
                return _scenario_definition
        raise KeyError(f"No such scenario {_scenario_name!r} in {request.req_baseline!r}")

    def process(
            self,
            request,  # type: _HttpRequestType
    ):  # type: (...) -> bool
        from ._exec import Exec
        from ._htmldoc import HtmlDocument
        from ._htmlgentypes import CollapsibleState

        # Filter `request`.
        if request.base_path != ScenarioPage._URL:
            self.debug("Request base path %r not matching %r", request.base_path, ScenarioPage._URL)
            self.debug("%r not processed", request)
            return False
        self.debug("Processing %r", request)

        # Applicable baseline.
        self.debug("Requirement baseline: %r", request.req_baseline)

        # Find the scenario instance from the URL arguments and requirement baseline.
        _scenario = self._getscenario(request)  # type: scenario.ScenarioDefinition
        self.debug("Scenario: %r", _scenario)

        # HTML content.
        self.debug("Generating HTML content")
        _html = HtmlDocument(request)
        _html.settitle(_scenario.name, campaign_subtitle=True)

        Exec.actionbutton2html(_html, request, Exec.Action.RELOAD_MAIN_REQ_BASELINE)

        with _html.addnode("div", id="scenario"):
            if (_scenario.execution is not None) and (_scenario.execution.time.start is not None):
                self._executionresults2html(_html, _scenario)

            if _scenario.getattributenames():
                self._scenarioattributes2html(_html, _scenario)

            _req_refs = _scenario.getreqrefs(walk_steps=True)  # type: scenario.SetWithReqLinksType[scenario.ReqRef]
            if _req_refs:
                self._reqrefs2html(
                    _html,
                    _scenario, _req_refs,
                    default_state=CollapsibleState.EXPANDED,
                )

            self._steps2html(_html, _scenario)

        request.sendhtml(_html)
        return True

    def _scenarioattributes2html(
            self,
            html,  # type: _HtmlDocumentType
            scenario_definition,  # type: scenario.ScenarioDefinition
    ):  # type: (...) -> None
        """
        Builds the HTML content for scenario attributes.

        :param html: HTML output page to feed.
        :param scenario_definition: Scenario which attributes to build HTML content for.
        """
        from ._htmlgendivs import DivGenerator
        from ._htmlgentypes import CollapsibleState

        _div_generator = DivGenerator(
            html,
            name="Attributes",
            collapsible_cid="attributes",
            default_state=CollapsibleState.EXPANDED,
        )  # type: DivGenerator
        with _div_generator.adddiv(classes=["scenario", "attributes"]):
            with _div_generator.addcollapsiblediv():
                with html.addnode("ul", classes=["attributes"]):
                    for _attr_name in scenario_definition.getattributenames():  # type: str
                        with html.addnode("li", classes=["scenario", "attribute"]):
                            html.addnode("span", classes=["scenario", "attribute", "name"], text=_attr_name)
                            html.addnode("span", classes=["scenario", "attribute", "sep"], text=":")
                            html.addnode("span", classes=["scenario", "attribute", "value"], text=scenario_definition.getattribute(_attr_name))

    def _steps2html(
            self,
            html,  # type: _HtmlDocumentType
            scenario_definition,  # type: scenario.ScenarioDefinition
    ):  # type: (...) -> None
        """
        Builds the HTML content for scenario steps.

        :param html: HTML output page to feed.
        :param scenario_definition: Scenario which steps to build HTML content for.
        """
        from ._htmlgendivs import DivGenerator
        from ._htmlgenlists import ListGenerator

        with DivGenerator(html, name="Steps").adddiv(classes=["scenario", "steps"]):
            _list_generator = ListGenerator(
                html,
                list_cid="steps",
            )  # type: ListGenerator
            _list_generator.addexpandallbutton()
            _list_generator.addcollapseallbutton()
            with _list_generator.addlist():
                for _step in scenario_definition.steps:  # type: scenario.StepDefinition
                    self._step2html(_list_generator, _step)

    def _step2html(
            self,
            list_generator,  # type: _ListGeneratorType
            step,  # type: scenario.StepDefinition
    ):  # type: (...) -> None
        """
        Builds the HTML content for the given step.

        :param list_generator: List generator. Provides the HTML output page to feed.
        :param step: Step to build HTML content for.
        """
        from ._htmlgenanchors import AnchorGenerator
        from ._htmlgendivs import DivGenerator
        from ._htmlgentypes import CollapsibleState

        # Step section descriptions.
        if isinstance(step, scenario.StepSectionDescription):
            # Don't call `ListGenerator.additem()`, add a simple `<li></li>` node with `<h2></h2>` inside.
            with list_generator.html.addnode("li", classes=["step", "section"]):
                list_generator.html.addnode("h2", classes=["step"], text=step.description)

        # Regular steps.
        else:
            with list_generator.additem(
                li1_cid=f"step#{step.number}",
                classes=["step"],
                default_state=CollapsibleState.COLLAPSED,
            ):
                # Step anchor.
                with AnchorGenerator(list_generator.html, name=f"step-{step.number}").addanchor(classes=["step"]):
                    # Step number, description and name.
                    list_generator.html.addnode("span", classes=["step", "number"], text=f"step#{step.number}")
                    if step.description:
                        list_generator.html.addnode("span", classes=["step", "sep"], text=":")
                        list_generator.html.addnode("span", classes=["step", "description"], text=step.description)
                    list_generator.html.addnode("span", classes=["step", "name"], text=step.name)

                # Execution results.
                if step.executions:
                    self._executionresults2html(list_generator.html, step)

                # Collapsible step content.
                with list_generator.addsubitem():
                    # Step requirements coverage.
                    _req_refs = step.getreqrefs()  # type: scenario.SetWithReqLinksType[scenario.ReqRef]
                    if _req_refs:
                        self._reqrefs2html(
                            list_generator.html,
                            step, _req_refs,
                            default_state=CollapsibleState.COLLAPSED,
                        )

                    # Actions & expected results.
                    with DivGenerator(list_generator.html, name="Actions / results").adddiv(classes=["actions-results"]):
                        with list_generator.html.addnode("ul", classes=["actions-results"]):
                            for _action_result in step.actions_results:  # type: scenario.ActionResultDefinition
                                self._actionresult2html(list_generator.html, _action_result)

    def _actionresult2html(
            self,
            html,  # type: _HtmlDocumentType
            action_result,  # type: scenario.ActionResultDefinition
    ):  # type: (...) -> None
        """
        Builds the HTML content for the given action / expected result.

        :param html: HTML output page to feed.
        :param action_result: Action / expected result to build HTML content for.
        """
        from ._htmlgendivs import DivGenerator
        from ._htmlgentypes import CollapsibleState

        # Action/result identifier classes.
        _action_result_id_classes = [
            "action-result",
            action_result.type.lower(),
        ]  # type: typing.Sequence[str]

        with html.addnode("li", classes=[*_action_result_id_classes]):
            # Make action/result content collapsible.
            _div_generator = DivGenerator(
                html,
                collapsible_cid=f"step#{action_result.step.number}-{action_result.type.name.lower()}#{action_result.number}",
                # Don't set default state right now.
                # Set it in the end depending on whether the action/result has collapsible content or not.
                # See `_default_state` local variable defined right after.
                default_state=None,
            )  # type: DivGenerator
            # Default state to set in the end.
            _default_state = None  # type: typing.Optional[CollapsibleState]

            # Main div (adds a toggle button by the way).
            with _div_generator.adddiv(classes=_action_result_id_classes):
                html.addnode("span", classes=[*_action_result_id_classes, "type"], text=action_result.type.upper())
                html.addnode("span", classes=[*_action_result_id_classes, "sep"], text=":")
                html.addnode("span", classes=[*_action_result_id_classes, "text"], text=action_result.description)

                if action_result.executions:
                    # Execution result (before collapsible content, if any).
                    self._executionresults2html(html, action_result)

                    # Add collapsible content only if the action/result has evidence (collapsed by default).
                    if sum([len(_execution.evidence) for _execution in action_result.executions]) > 0:
                        _default_state = CollapsibleState.COLLAPSED
                    if _default_state is not None:
                        with _div_generator.addcollapsiblediv(classes=["action-result"]):
                            self._evidence2html(html, action_result)

                # Set default state for action/result collapsible content.
                _div_generator.setstate(_default_state)

    def _reqrefs2html(
            self,
            html,  # type: _HtmlDocumentType
            req_verifier,  # type: typing.Union[scenario.ScenarioDefinition, scenario.StepDefinition]
            req_refs,  # type: scenario.SetWithReqLinksType[scenario.ReqRef]
            *,
            default_state,  # type: _CollapsibleStateType
    ):  # type: (...) -> None
        """
        Buils the HTML content for requirement coverage.

        :param html: HTML output page to feed.
        :param req_verifier: Scenario or step to process requirement coverage for.
        :param req_refs: Scenario or step requirement coverage.
        :param default_state: Default collapsible state for requirement references.
        """
        from ._htmlgendivs import DivGenerator
        from ._htmlgenlinks import LinkGenerator
        from ._pagereqs import RequirementsPage
        from ._pagereqsdown import DownstreamTraceabilityPage
        from ._pagereqsup import UpstreamTraceabilityPage

        # Determine the HTML object class depending on the type of `req_verifier`.
        _obj_id_classes = ""  # type: str
        _obj_id = ""  # type: str
        if isinstance(req_verifier, scenario.ScenarioDefinition):
            _obj_id_classes = "scenario"
            _obj_id = "scenario"
        if isinstance(req_verifier, scenario.StepDefinition):
            _obj_id_classes = "step"
            _obj_id = f"step#{req_verifier.number}"

        # Build a named collapsible section.
        _div_generator = DivGenerator(
            html,
            name="Requirements",
            collapsible_cid=f"{_obj_id}-reqs",
            default_state=default_state,
        )  # type: DivGenerator

        # Main div with toggle button and section name.
        with _div_generator.adddiv(classes=[_obj_id_classes, "requirements"]):
            # Collapsible content.
            with _div_generator.addcollapsiblediv():
                with html.addnode("ul", classes=["req-refs"]):
                    for _req_ref in req_refs:  # type: scenario.ReqRef
                        with html.addnode("li", classes=[_obj_id_classes, "req-ref"]):
                            # Requirement reference id.
                            with html.addnode("span", classes=[_obj_id_classes, "req-ref", "id"]):
                                LinkGenerator(html).addlink(href=RequirementsPage.mkurl(_req_ref), title="Requirement details", text=_req_ref.id)

                            # Downstream traceability link.
                            with html.addnode("span", classes=[_obj_id_classes, "req-ref", "coverage"]):
                                DownstreamTraceabilityPage.reqref2htmllink(html, _req_ref)

                            # Find out the req-links which comments to display.
                            _req_links = [
                                _req_link for _req_link in req_refs[_req_ref]
                                # Filter on `req_verifier` only.
                                if (req_verifier in _req_link.req_verifiers)
                            ]  # type: typing.Sequence[scenario.ReqLink]
                            # Determine the comments to display from the latter.
                            _comments = ', '.join([_req_link.comments for _req_link in _req_links])  # type: str

                            if _comments:
                                html.addnode("span", classes=[_obj_id_classes, "req-ref", "sep"], text=":")
                                html.addnode("span", classes=[_obj_id_classes, "req-ref", "comments"], text=_comments)

                # Upstream traceability link.
                UpstreamTraceabilityPage.reqverifier2htmllink(html, req_verifier, text="Upstream traceability")

    def _executionresults2html(
            self,
            html,  # type: _HtmlDocumentType
            definition,  # type: typing.Union[scenario.ScenarioDefinition, scenario.StepDefinition, scenario.ActionResultDefinition]
    ):  # type: (...) -> None
        """
        Builds the HTML content for the execution results of the given object.

        Either for a scenario, for a step, an action or expected result.

        :param html: HTML output page to feed.
        :param definition: Scenario, step or action/result which execution results to build HTML content for.
        """
        from ._htmlgendivs import DivGenerator

        _obj_id_classes = []  # type: typing.List[str]
        _executions = []  # type: typing.Sequence[typing.Union[scenario.ScenarioExecution, scenario.StepExecution, scenario.ActionResultExecution]]
        if isinstance(definition, scenario.ScenarioDefinition):
            _obj_id_classes.extend(["scenario-execution"])
            if definition.execution:
                _executions = [definition.execution]
        elif isinstance(definition, scenario.StepDefinition):
            _obj_id_classes.extend(["step-execution"])
            _executions = definition.executions
        elif isinstance(definition, scenario.ActionResultDefinition):
            _obj_id_classes.extend(["action-result-execution", f"{definition.type.lower()}-execution"])
            _executions = definition.executions

        # Make `_obj_id_classes` plural for the main div and list.
        _objs_id_classes = [f"{_}s" for _ in _obj_id_classes]  # type: typing.Sequence[str]

        # `.execution-results` div, with title and list.
        with DivGenerator(html, name="Execution results").adddiv(classes=[*_objs_id_classes, "execution-results"]):
            with html.addnode("ul", classes=[*_objs_id_classes, "execution-results"]):

                # One list item per execution.
                for _execution in _executions:  # type: typing.Union[scenario.ScenarioExecution, scenario.StepExecution, scenario.ActionResultExecution]
                    with html.addnode("li", classes=[*_obj_id_classes, "execution-result"]):

                        # Execution times.
                        self._executionresulttimes2html(html, _execution, obj_id_classes=_obj_id_classes)

                        # Errors.
                        for _error in _execution.errors:  # type: scenario.TestError
                            with html.addnode("div", classes=[*_obj_id_classes, "execution-result", "error"]):
                                html.addnode("span", classes=[*_obj_id_classes, "execution-result", "error", "message"], text=_error.message)
                                if _error.location is not None:
                                    html.addnode(
                                        "span",
                                        classes=[*_obj_id_classes, "execution-result", "error", "location"],
                                        text=_error.location.tolongstring(),
                                    )

                        # Warnings.
                        for _warning in _execution.warnings:  # type: scenario.TestError
                            with html.addnode("div", classes=[*_obj_id_classes, "execution-result", "warning"]):
                                html.addnode("span", classes=[*_obj_id_classes, "execution-result", "warning", "message"], text=_warning.message)
                                if _warning.location is not None:
                                    html.addnode(
                                        "span",
                                        classes=[*_obj_id_classes, "execution-result", "warning", "location"],
                                        text=_warning.location.tolongstring(),
                                    )

                        # Success.
                        if not any([_execution.errors, _execution.warnings]):
                            with html.addnode("div", classes=[*_obj_id_classes, "execution-result", "success"]):
                                html.addnode("span", classes=[*_obj_id_classes, "execution-result", "success", "message"], text="SUCCESS")

    def _evidence2html(
            self,
            html,  # type: _HtmlDocumentType
            action_result,  # type: scenario.ActionResultDefinition
    ):  # type: (...) -> None
        """
        Builds the HTML content for the given action/result evidence.

        :param html: HTML output page to feed.
        :param action_result: Action/result which evidence to build HTML content for.
        """
        from ._htmlgendivs import DivGenerator

        _obj_id_classes = ["action-result-execution", f"{action_result.type.lower()}-execution"]  # type: typing.List[str]

        # Make `_obj_id_classes` plural for the main div and list.
        _objs_id_classes = [f"{_}s" for _ in _obj_id_classes]  # type: typing.Sequence[str]

        # `.evidence` div, with title and list.
        # Memo:
        #   The containing section is tagged with 'evidence', not 'execution-results' as in `_executionresults2html()` to differentiate the two.
        #   Keep 'execution-results' HTML class for subitems inside (easier to style).
        with DivGenerator(html, name="Evidence").adddiv(classes=[*_objs_id_classes, "evidence"]):
            with html.addnode("ul", classes=[*_objs_id_classes, "evidence"]):

                # Add items for executions with evidence only.
                for _execution in action_result.executions:  # type: scenario.ActionResultExecution
                    if _execution.evidence:
                        with html.addnode("li", classes=[*_obj_id_classes, "execution-result"]):

                            # Execution times.
                            self._executionresulttimes2html(html, _execution, obj_id_classes=_obj_id_classes)

                            # Evidence.
                            for _evidence in _execution.evidence:  # type: str
                                with html.addnode("span", classes=[*_obj_id_classes, "execution-result", "evidence"]):
                                    html.addtext(_evidence)

    def _executionresulttimes2html(
            self,
            html,  # type: _HtmlDocumentType
            execution,  # type: typing.Union[scenario.ScenarioExecution, scenario.StepExecution, scenario.ActionResultExecution]
            *,
            obj_id_classes,  # type: typing.Sequence[str]
    ):  # type: (...) -> None
        """
        Build the HTML content for the given Scenario, step or action/result execution times.

        :param html: HTML output page to feed.
        :param execution: Scenario, step or action/result execution which times to build HTML content for.
        :param obj_id_classes: Identifying HTML classes for the given object.
        """
        # Starting time.
        if execution.time.start is not None:
            with html.addnode("span", classes=[*obj_id_classes, "execution-result", "time-start"]):
                html.addtext(scenario.datetime.toiso8601(execution.time.start))

        # Ending time.
        if execution.time.end is not None:
            with html.addnode("span", classes=[*obj_id_classes, "execution-result", "time-end"]):
                html.addtext(scenario.datetime.toiso8601(execution.time.end))

        # Elapsed time.
        if execution.time.elapsed is not None:
            with html.addnode("span", classes=[*obj_id_classes, "execution-result", "time-elapsed"]):
                html.addtext(scenario.datetime.f2strduration(execution.time.elapsed))
