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
    from ._requesthandler import RequestHandler as _RequestHandlerImpl  # @inheritance
if typing.TYPE_CHECKING:
    from ._htmldoc import HtmlDocument as _HtmlDocumentType
    from ._httprequest import HttpRequest as _HttpRequestType


class ScenarioPage(_RequestHandlerImpl):
    """
    Scenario details page.
    """

    #: Base URL for the scenario details page.
    URL = "/scenario"  # type: str

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
            _step_anchor = f"step#{req_verifier.number}"

        return HttpRequest.encodeurl(ScenarioPage.URL, args={"name": _scenario.name}, anchor=_step_anchor)

    def __init__(self):  # type: (...) -> None
        """
        Configures the logger instance.
        """
        from ._debugclasses import UIDebugClass

        _RequestHandlerImpl.__init__(self, UIDebugClass.PAGE_SCENARIO)

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
        # Retrieve the scenario name from request arguments.
        _scenario_name = request.getarg("name")  # type: str
        self.debug("Scenario name: %r", _scenario_name)

        # Search for the scenario in the loaded scenarios.
        for _scenario_definition in request.req_baseline.scenarios:  # type: scenario.ScenarioDefinition
            if _scenario_definition.name == _scenario_name:
                # Scenario found.
                if not _scenario_definition.execution:
                    # Load scenario details.
                    try:
                        # Prepare the scenario for working with `ScenarioRunner` and `ScenarioStack`.
                        _scenario_definition.execution = scenario.ScenarioExecution(_scenario_definition)
                        scenario.stack.building.pushscenariodefinition(_scenario_definition)

                        # Start iterating over the scenario steps.
                        _scenario_definition.execution.startsteplist()
                        while _scenario_definition.execution.current_step_definition:
                            # Execute the step in *building* mode.
                            _scenario_definition.execution.current_step_definition.step()

                            # Switch to the next step.
                            _scenario_definition.execution.nextstep()
                    finally:
                        scenario.stack.building.popscenariodefinition(_scenario_definition)
                return _scenario_definition
        raise KeyError(f"No such scenario {_scenario_name!r}")

    def process(
            self,
            request,  # type: _HttpRequestType
    ):  # type: (...) -> bool
        from ._htmldoc import HtmlDocument

        # Filter `request`.
        if request.base_path != ScenarioPage.URL:
            self.debug("Request base path %r not matching %r", request.base_path, ScenarioPage.URL)
            self.debug("%r not processed", request)
            return False
        self.debug("Processing %r", request)

        # Then find the scenario instance from the loaded scenarios.
        _scenario = self._getscenario(request)  # type: scenario.ScenarioDefinition
        self.debug("Scenario: %r", _scenario)

        # HTML content.
        self.debug("Generating HTML content")
        _html = HtmlDocument()
        _html.settitle(_scenario.name)

        with _html.addcontent('<div id="scenario"></div>'):
            if _scenario.getattributenames():
                self._scenarioattributes2html(_scenario, _html)

            _req_refs = _scenario.getreqrefs(walk_steps=True)  # type: scenario.SetWithReqLinksType[scenario.ReqRef]
            if _req_refs:
                self._reqrefs2html(_scenario, _req_refs, _html)

            self._steps2html(_scenario, _html)

        request.sendhtml(_html)
        return True

    def _scenarioattributes2html(
            self,
            scenario_definition,  # type: scenario.ScenarioDefinition
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Builds the HTML content for scenario attributes.

        :param scenario_definition: Scenario which attributes to build HTML content for.
        :param html: HTML output page to feed.
        """
        with html.addcontent('<div class="scenario attributes"></div>'):
            html.addcontent('<p>Attributes:</p>')
            with html.addcontent('<ul></ul>'):
                for _attr_name in scenario_definition.getattributenames():  # type: str
                    with html.addcontent('<li class="scenario attribute"></li>'):
                        html.addcontent(f'<span class="scenario attribute name">{html.encode(_attr_name)}</span>')
                        html.addcontent('<span class="scenario attribute sep">:</span>')
                        html.addcontent(f'<span class="scenario attribute value">{html.encode(scenario_definition.getattribute(_attr_name))}</span>')

    def _steps2html(
            self,
            scenario_definition,  # type: scenario.ScenarioDefinition
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Builds the HTML content for scenario steps.

        :param scenario_definition: Scenario which steps to build HTML content for.
        :param html: HTML output page to feed.
        """
        with html.addcontent('<div id="steps"></div>'):
            html.addcontent('<p>Steps:</p>')
            with html.addcontent('<ul></ul>'):
                for _step in scenario_definition.steps:  # type: scenario.StepDefinition
                    self._step2html(_step, html)

    def _step2html(
            self,
            step,  # type: scenario.StepDefinition
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Builds the HTML content for the given step.

        :param step: Step to build HTML content for.
        :param html: HTML output page to feed.
        """
        with html.addcontent('<li class="step"></li>'):
            if isinstance(step, scenario.StepSectionDescription) and step.description:
                html.addcontent(f'<h2 class="step">{html.encode(step.description)}</h2>')
            else:
                # Step anchor.
                html.addcontent(f'<a name="step#{step.number}" />')

                # Step number, description and name.
                html.addcontent(f'<span class="step number">step#{step.number}</span>')
                if step.description:
                    html.addcontent('<span class="step sep">:</span>')
                    html.addcontent(f'<span class="step description">{step.description}</span>')
                html.addcontent(f'<span class="step name">({step.name})</span>')

                # Step requirements coverage.
                _req_refs = step.getreqrefs()  # type: scenario.SetWithReqLinksType[scenario.ReqRef]
                if _req_refs:
                    self._reqrefs2html(step, _req_refs, html)

                # Actions & expected results.
                with html.addcontent(f'<div class="actions-results"></div>'):
                    with html.addcontent('<ul></ul>'):
                        for _action_result in step.actions_results:  # type: scenario.ActionResultDefinition
                            self._actionresult2html(_action_result, html)

    def _actionresult2html(
            self,
            action_result,  # type: scenario.ActionResultDefinition
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Builds the HTML content for the given action / expected result.

        :param action_result: Action / expected result to build HTML content for.
        :param html: HTML output page to feed.
        """
        with html.addcontent(f'<li class="{action_result.type.lower()}"></li>'):
            html.addcontent(f'<span class="{action_result.type.lower()} type">{action_result.type.upper()}</span>')
            html.addcontent(f'<span class="{action_result.type.lower()} sep">:</span>')
            html.addcontent(f'<span class="{action_result.type.lower()} text">{html.encode(action_result.description)}</span>')

    def _reqrefs2html(
            self,
            req_verifier,  # type: typing.Union[scenario.ScenarioDefinition, scenario.StepDefinition]
            req_refs,  # type: scenario.SetWithReqLinksType[scenario.ReqRef]
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Buils the HTML content for a scenario or step requirement coverage.

        :param req_verifier: Scenario or step to process requirement coverage for.
        :param req_refs: Scenario or step requirement coverage.
        :param html: HTML output page to feed.
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

        with html.addcontent(f'<div class="{_obj_class} requirements"></div>'):
            html.addcontent('<p>Requirements:</p>')
            with html.addcontent('<ul></ul>'):
                for _req_ref in req_refs:  # type: scenario.ReqRef
                    with html.addcontent(f'<li class="{_obj_class} req-ref"></li>'):
                        # Requirement reference id.
                        with html.addcontent(f'<span class="{_obj_class} req-ref id"></span>'):
                            with html.addcontent(f'<a href="{RequirementsPage.mkurl(_req_ref)}"></a>'):
                                html.addtext(_req_ref.id)

                        # Downstream traceability link.
                        with html.addcontent(f'<span class="{_obj_class} req-ref coverage"></span>'):
                            DownstreamTraceabilityPage.reqref2unnamedhtmllink(_req_ref, html)

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

                        html.addcontent(f'<span class="{_obj_class} req-ref sep">:</span>')
                        html.addcontent(f'<span class="{_obj_class} req-ref comments">{html.encode(_comments)}</span>')

            # Upstream traceability link.
            if isinstance(req_verifier, scenario.ScenarioDefinition):
                UpstreamTraceabilityPage.scenario2unnamedhtmllink(req_verifier, html)
