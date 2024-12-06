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
            _step_anchor = f"step{req_verifier.number}"

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
            if _scenario.getattributenames():
                self._scenarioattributes2html(_html, _scenario)

            _req_refs = _scenario.getreqrefs(walk_steps=True)  # type: scenario.SetWithReqLinksType[scenario.ReqRef]
            if _req_refs:
                self._reqrefs2html(_html, _scenario, _req_refs)

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
        with html.addnode("div", classes=["scenario", "attributes"]):
            html.addnode("p", text="Attributes:")
            with html.addnode("ul"):
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
        with html.addnode("div", id="steps"):
            html.addnode("p", text="Steps:")
            with html.addnode("ul"):
                for _step in scenario_definition.steps:  # type: scenario.StepDefinition
                    self._step2html(html, _step)

    def _step2html(
            self,
            html,  # type: _HtmlDocumentType
            step,  # type: scenario.StepDefinition
    ):  # type: (...) -> None
        """
        Builds the HTML content for the given step.

        :param html: HTML output page to feed.
        :param step: Step to build HTML content for.
        """
        from ._anchors import Anchor

        with html.addnode("li", classes=["step"]):
            if isinstance(step, scenario.StepSectionDescription) and step.description:
                html.addnode("h2", classes=["step"], text=step.description)
            else:
                # Step anchor.
                with Anchor.add(html, name=f"step{step.number}"):
                    # Step number, description and name.
                    html.addnode("span", classes=["step", "number"], text=f"step#{step.number}")
                    if step.description:
                        html.addnode("span", classes=["step", "sep"], text=":")
                        html.addnode("span", classes=["step", "description"], text=step.description)
                    html.addnode("span", classes=["step", "name"], text=step.name)

                # Step requirements coverage.
                _req_refs = step.getreqrefs()  # type: scenario.SetWithReqLinksType[scenario.ReqRef]
                if _req_refs:
                    self._reqrefs2html(html, step, _req_refs)

                # Actions & expected results.
                with html.addnode("div", classes=["actions-results"]):
                    with html.addnode("ul"):
                        for _action_result in step.actions_results:  # type: scenario.ActionResultDefinition
                            self._actionresult2html(html, _action_result)

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
        with html.addnode("li", classes=[action_result.type.lower()]):
            html.addnode("span", classes=[action_result.type.lower(), "type"], text=action_result.type.upper())
            html.addnode("span", classes=[action_result.type.lower(), "sep"], text=":")
            html.addnode("span", classes=[action_result.type.lower(), "text"], text=action_result.description)

    def _reqrefs2html(
            self,
            html,  # type: _HtmlDocumentType
            req_verifier,  # type: typing.Union[scenario.ScenarioDefinition, scenario.StepDefinition]
            req_refs,  # type: scenario.SetWithReqLinksType[scenario.ReqRef]
    ):  # type: (...) -> None
        """
        Buils the HTML content for a scenario or step requirement coverage.

        :param html: HTML output page to feed.
        :param req_verifier: Scenario or step to process requirement coverage for.
        :param req_refs: Scenario or step requirement coverage.
        """
        from ._pagereqs import RequirementsPage
        from ._pagereqsdown import DownstreamTraceabilityPage
        from ._pagereqsup import UpstreamTraceabilityPage

        # Determine the HTML object class depending on the type of `req_verifier`.
        _obj_class = ""  # type: str
        if isinstance(req_verifier, scenario.ScenarioDefinition):
            _obj_class = "scenario"
        if isinstance(req_verifier, scenario.StepDefinition):
            _obj_class = "step"

        with html.addnode("div", classes=[_obj_class, "requirements"]):
            html.addnode("p", text="Requirements:")

            with html.addnode("ul"):
                for _req_ref in req_refs:  # type: scenario.ReqRef
                    with html.addnode("li", classes=[_obj_class, "req-ref"]):
                        # Requirement reference id.
                        with html.addnode("span", classes=[_obj_class, "req-ref", "id"]):
                            html.addlink(href=RequirementsPage.mkurl(_req_ref), title="Requirement details", text=_req_ref.id)

                        # Downstream traceability link.
                        with html.addnode("span", classes=[_obj_class, "req-ref", "coverage"]):
                            DownstreamTraceabilityPage.reqref2htmllink(html, _req_ref)

                        # Find out the req-links which comments to display.
                        _req_links = list(filter(
                            # Filter on `obj` only.
                            lambda req_link: req_verifier in req_link.req_verifiers,
                            req_refs[_req_ref],
                        ))  # type: typing.Sequence[scenario.ReqLink]
                        # Determine the comments to display from the latter.
                        _comments = ', '.join(map(lambda req_link: req_link.comments, _req_links))  # type: str
                        if not _comments:
                            _comments = "(see steps)"

                        html.addnode("span", classes=[_obj_class, "req-ref", "sep"], text=":")
                        html.addnode("span", classes=[_obj_class, "req-ref", "comments"], text=_comments)

            # Upstream traceability link.
            if isinstance(req_verifier, scenario.ScenarioDefinition):
                UpstreamTraceabilityPage.scenario2htmllink(html, req_verifier, text="Upstream traceability")
