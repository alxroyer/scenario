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
User interface configuration page.
"""

import typing

import scenario

if True:
    from ._httprequesthandler import HttpRequestHandler as _HttpRequestHandlerImpl  # @inheritance
if typing.TYPE_CHECKING:
    from ._htmldoc import HtmlDocument as _HtmlDocumentType
    from ._httprequest import HttpRequest as _HttpRequestType


class ConfigurationPage(_HttpRequestHandlerImpl):
    """
    Configuration page.
    """

    #: Base URL for the configuration page.
    _URL = "/configuration"  # type: str

    class Arg(scenario.enum.StrEnum):
        """
        GET argument or form input names.
        """
        #: GET action argument or hidden POST input that gives the id of the form executed.
        #:
        #: See :class:`ConfigurationPage.Action` for possible values.
        ACTION = "action"

        #: Form#1: Multiline input text that gives requirement file paths.
        REQ_DB_PATHS = "req-db-path"
        #: Form#1: Multiline input text that gives test suite file paths.
        TEST_SUITE_PATHS = "test-suite-paths"

        #: Form#2: Input text that gives a path for a campaign directory or report file.
        CAMPAIGN_PATH = "campaign-path"

    class Action(scenario.enum.StrEnum):
        """
        :attr:`ConfigurationPage.Arg.ACTION` values.
        """
        #: Execute form#1.
        FORM1 = "form1"
        #: Execute form#2.
        FORM2 = "form2"

    @staticmethod
    def mkurl(
            *,
            html_escape=True,  # type: bool
    ):  # type: (...) -> str
        """
        Builds a configuration page URL.

        :param html_escape: ``True`` (default) to get HTML escaped text.
        :return: Configuration page URL.
        """
        from ._httprequest import HttpRequest

        return HttpRequest.encodeurl(
            ConfigurationPage._URL,
            args=HttpRequest.mkurlargs(obj=None),
            html_escape=html_escape,
        )

    def __init__(self):  # type: (...) -> None
        """
        Configures the logger instance.
        """
        from ._debugclasses import UIDebugClass

        _HttpRequestHandlerImpl.__init__(self, UIDebugClass.PAGE_CONFIG)

    def process(
            self,
            request,  # type: _HttpRequestType
    ):  # type: (...) -> bool
        from ._htmldoc import HtmlDocument

        # Filter `request`.
        if request.base_path != ConfigurationPage._URL:
            self.debug("Request base path %r not matching %r", request.base_path, ConfigurationPage._URL)
            self.debug("%r not processed", request)
            return False
        self.debug("Processing %r", request)

        self.debug("Generating HTML content")
        _html = HtmlDocument(request)
        _html.settitle("Configuration", campaign_subtitle=False)

        # Execution.
        if request.getarg(ConfigurationPage.Arg.ACTION, default=""):
            self._processaction(request, _html)

        # General page content.
        self._form1html(_html)
        self._form2html(_html)

        request.sendhtml(_html)
        return True

    def _form1html(
            self,
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Form #1: Requirements & test suites.

        :param html: Output HTML document.
        """
        from .._scenarioconfig import SCENARIO_CONFIG  # Access `scenario` inner symbols.
        from .._xmlutils import Xml  # Access `scenario` inner symbols.

        with html.addcontent(f'<div id="{ConfigurationPage.Action.FORM1}"></div>'):
            with html.addcontent(f'<form action="{ConfigurationPage.mkurl()}" method="post"></form>'):
                # Form id.
                html.addcontent(f'<input type="hidden" name="{ConfigurationPage.Arg.ACTION}" value="{ConfigurationPage.Action.FORM1}" />')

                # Requirements file.
                html.addcontent('<p>Requirements:</p>')
                with html.addcontent(
                    f'<textarea name="{ConfigurationPage.Arg.REQ_DB_PATHS}" rows="10" '
                    'placeholder="List of requirement files (absolute paths)"></textarea>',
                ):
                    # Ensure a empty text node at least for `<textarea/>` (otherwise HTML fails with empty `<textarea/>`).
                    _text_node = html.addtext("")  # type: Xml.TextNode
                    # Then add a line for each requirement file.
                    for _req_db_path in SCENARIO_CONFIG.reqdbpaths():  # type: scenario.Path
                        if _text_node.data:
                            _text_node.data += "\n"
                        _text_node.data += _req_db_path.abspath

                # Test suite files.
                html.addcontent('<p>Test suites:</p>')
                with html.addcontent(
                    f'<textarea name="{ConfigurationPage.Arg.TEST_SUITE_PATHS}" rows="10" '
                    'placeholder="List of test suite file (absolute paths)"></textarea>',
                ):
                    # Ensure a empty text node at least for `<textarea/>` (otherwise HTML fails with empty `<textarea/>`).
                    _text_node = html.addtext("")  # Type already defined above.
                    # Then add a line for each test suite.
                    for _test_suite_path in SCENARIO_CONFIG.testsuitepaths():  # type: scenario.Path
                        if _text_node.data:
                            _text_node.data += "\n"
                        _text_node.data += _test_suite_path.abspath

                # Submit.
                html.addcontent('<input type="submit" value="Apply" />')

    def _form2html(
            self,
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Form #2: Campaign.

        :param html: Output HTML document.
        """
        with html.addcontent(f'<div id="{ConfigurationPage.Action.FORM2}"></div>'):
            with html.addcontent(f'<form action="{ConfigurationPage.mkurl()}" method="post"></form>'):
                # Form id.
                html.addcontent(f'<input type="hidden" name="{ConfigurationPage.Arg.ACTION}" value="{ConfigurationPage.Action.FORM2}" />')

                # Campaign path (directory or campaign report).
                html.addcontent('<p>Campaign:</p>')
                html.addcontent(f'<input type="text" name="{ConfigurationPage.Arg.CAMPAIGN_PATH}" />')

                # Submit.
                html.addcontent('<input type="submit" value="Apply" />')

    def _processaction(
            self,
            request,  # type: _HttpRequestType
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Process the :attr:`ConfigurationPage.Arg.ACTION` argument.

        Executes form data, or reloads default data.

        :param request: Input request with form data.
        :param html: Output HTML document.
        """
        from ._reqbl import UI_REQ_BASELINES

        # Read ACTION parameter.
        _action = request.getarg(ConfigurationPage.Arg.ACTION)  # type: str
        _req_db_paths = []  # type: typing.List[scenario.Path]
        _test_suite_paths = []  # type: typing.List[scenario.Path]
        _campaign_path = scenario.Path()  # type: scenario.Path

        if _action == ConfigurationPage.Action.FORM1:
            for _req_db_path in request.getarg(ConfigurationPage.Arg.REQ_DB_PATHS, default="").splitlines():  # type: str
                if _req_db_path.strip():
                    _req_db_paths.append(scenario.Path(_req_db_path.strip()))

            for _test_suite_path in request.getarg(ConfigurationPage.Arg.TEST_SUITE_PATHS, default="").splitlines():  # type: str
                if _test_suite_path.strip():
                    _test_suite_paths.append(scenario.Path(_test_suite_path.strip()))

            UI_REQ_BASELINES.main = scenario.ReqBaseline.fromfiles(
                # Use file names for baseline name.
                name=(
                    ", ".join([_path.prettypath for _path in [*_req_db_paths, *_test_suite_paths]])
                    or "(default requirement and test suite files)"
                ),
                req_db_paths=_req_db_paths or None,
                test_suite_paths=_test_suite_paths or None,
                log_info=True,
            )

        elif _action == ConfigurationPage.Action.FORM2:
            _campaign_path = scenario.Path(request.getarg(ConfigurationPage.Arg.CAMPAIGN_PATH).strip())

            UI_REQ_BASELINES.main = scenario.ReqBaseline.fromcampaignresults(
                _campaign_path,
                name=_campaign_path.prettypath,
                log_info=True,
            )

        else:
            raise KeyError(f"Unexpected action {_action!r}")

        # Execution results.
        with html.addcontent(f'<div class="{ConfigurationPage.Arg.ACTION} result"></div>'):
            html.addcontent('<h2>Execution result</h2>')
            if _req_db_paths or _campaign_path:
                html.addcontent(f'<p>{len(UI_REQ_BASELINES.main.req_db.getallreqs())} requirements loaded</p>')
            if _test_suite_paths or _campaign_path:
                html.addcontent(f'<p>{len(UI_REQ_BASELINES.main.scenarios)} scenarios loaded</p>')
