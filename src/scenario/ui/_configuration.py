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

if True:
    from .._enumutils import StrEnum as _StrEnumImpl  # `StrEnum` used for inheritance.
    from ._requesthandler import RequestHandler as _RequestHandlerImpl  # `RequestHandler` used for inheritance.
if typing.TYPE_CHECKING:
    from ._htmldoc import HtmlDocument as _HtmlDocumentType
    from ._httprequest import HttpRequest as _HttpRequestType


class Configuration(_RequestHandlerImpl):
    """
    Configuration page.
    """

    #: Base URL for the configuration page.
    URL = "/configuration"

    @staticmethod
    def mkreloaddefaulturl():  # type: (...) -> str
        """
        Builds an URL to reload default data.

        :return: URL to reload default data.
        """
        from ._httprequest import HttpRequest

        return HttpRequest.encodeurl(Configuration.URL, args={Configuration.Arg.ACTION: Configuration.Action.RELOAD_DEFAULT})

    class Arg(_StrEnumImpl):
        """
        GET parameter or form input names.
        """
        #: GET action parameter or hidden POST input that gives the id of the form executed.
        #:
        #: See :class:`Configuration.Action` for possible values.
        ACTION = "action"

        #: Form#1: Multiline input text that gives requirement file paths.
        REQ_DB_PATHS = "req-db-path"
        #: Form#1: Multiline input text that gives test suite file paths.
        TEST_SUITE_PATHS = "test-suite-paths"

        #: Form#2: Input text that gives a path for a campaign directory or report file.
        CAMPAIGN_PATH = "campaign-path"

    class Action(_StrEnumImpl):
        """
        :attr:`Configuration.Arg.ACTION` values.
        """
        #: Reload default data.
        RELOAD_DEFAULT = "reload-default"
        #: Execute form#1.
        FORM1 = "form#1"
        #: Execute form#2.
        FORM2 = "form#2"

    def matches(
            self,
            request,  # type: _HttpRequestType
    ):  # type: (...) -> bool
        return request.base_path == Configuration.URL

    def process(
            self,
            request,  # type: _HttpRequestType
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        html.settitle("Configuration")

        # Execution.
        if request.getarg(Configuration.Arg.ACTION, default=""):
            self._loaddata(request, html)

        # General page content.
        self._form1html(html)
        self._form2html(html)

    def _form1html(
            self,
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Form #1: Requirements & test suites.

        :param html: Output HTML document.
        """
        from .._path import Path
        from .._scenarioconfig import SCENARIO_CONFIG
        from .._xmlutils import Xml

        with html.addcontent(f'<div id="{html.encode(Configuration.Action.FORM1)}"></div>'):
            with html.addcontent(f'<form action="{Configuration.URL}" method="post"></form>'):
                # Form id.
                html.addcontent(f'<input type="hidden" name="{Configuration.Arg.ACTION}" value="{html.encode(Configuration.Action.FORM1)}" />')

                # Requirements file.
                html.addcontent('<p>Requirements:</p>')
                with html.addcontent(
                    f'<textarea name="{Configuration.Arg.REQ_DB_PATHS}" rows="10" '
                    'placeholder="List of requirement files (absolute paths)"></textarea>',
                ):
                    # Ensure a empty text node at least for `<textarea/>` (otherwise HTML fails with empty `<textarea/>`).
                    _text_node = html.addtext("")  # type: Xml.TextNode
                    # Then add a line for each requirement file.
                    for _req_db_path in SCENARIO_CONFIG.reqdbfiles():  # type: Path
                        if _text_node.data:
                            _text_node.data += "\n"
                        _text_node.data += _req_db_path.abspath

                # Test suite files.
                html.addcontent('<p>Test suites:</p>')
                with html.addcontent(
                    f'<textarea name="{Configuration.Arg.TEST_SUITE_PATHS}" rows="10" '
                    'placeholder="List of test suite file (absolute paths)"></textarea>',
                ):
                    # Ensure a empty text node at least for `<textarea/>` (otherwise HTML fails with empty `<textarea/>`).
                    _text_node = html.addtext("")  # Type already defined above.
                    # Then add a line for each test suite.
                    for _test_suite_path in SCENARIO_CONFIG.testsuitefiles():  # type: Path
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
        with html.addcontent(f'<div id="{html.encode(Configuration.Action.FORM2)}"></div>'):
            with html.addcontent('<form action="/configuration" method="post"></form>'):
                # Form id.
                html.addcontent(f'<input type="hidden" name="{Configuration.Arg.ACTION}" value="{html.encode(Configuration.Action.FORM2)}" />')

                # Campaign path (directory or campaign report).
                html.addcontent('<p>Campaign:</p>')
                html.addcontent(f'<input type="text" name="{Configuration.Arg.CAMPAIGN_PATH}" />')

                # Submit.
                html.addcontent('<input type="submit" value="Apply" />')

    def _loaddata(
            self,
            request,  # type: _HttpRequestType
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Executes form data.

        :param request: Input request with form data.
        :param html: Output HTML document.
        """
        from .._path import Path
        from .._reqdb import REQ_DB
        from .._reqtraceability import REQ_TRACEABILITY
        from .._scenarioconfig import SCENARIO_CONFIG

        _req_db_paths = []  # type: typing.List[Path]
        _test_suite_paths = []  # type: typing.List[Path]
        _campaign_path = None  # type: typing.Optional[Path]

        # Determine the data to reload.
        if request.getarg(Configuration.Arg.ACTION) == Configuration.Action.RELOAD_DEFAULT:
            _req_db_paths = list(SCENARIO_CONFIG.reqdbfiles())
            _test_suite_paths = list(SCENARIO_CONFIG.testsuitefiles())

        elif request.getarg(Configuration.Arg.ACTION) == Configuration.Action.FORM1:
            for _req_db_path in request.getarg(Configuration.Arg.REQ_DB_PATHS, default="").splitlines():  # type: str
                if _req_db_path.strip():
                    _req_db_paths.append(Path(_req_db_path.strip()))

            for _test_suite_path in request.getarg(Configuration.Arg.TEST_SUITE_PATHS, default="").splitlines():  # type: str
                if _test_suite_path.strip():
                    _test_suite_paths.append(Path(_test_suite_path.strip()))

        elif request.getarg(Configuration.Arg.ACTION) == Configuration.Action.FORM2:
            if request.getarg(Configuration.Arg.CAMPAIGN_PATH).strip():
                _campaign_path = Path(request.getarg(Configuration.Arg.CAMPAIGN_PATH).strip())

        else:
            raise KeyError(f"Unexpected action {request.getarg(Configuration.Arg.ACTION)!r}")

        # Reload data.
        if _req_db_paths or _test_suite_paths:
            REQ_TRACEABILITY.loaddatafromfiles(
                req_db_file_paths=_req_db_paths or None,
                test_suite_paths=_test_suite_paths or None,
                log_info=True,
            )
        elif _campaign_path:
            REQ_TRACEABILITY.loaddatafromcampaignresults(
                campaign_results=_campaign_path,
                log_info=True,
            )

        # Execution results.
        with html.addcontent('<div class="exec-result"></div>'):
            html.addcontent('<h2>Execution result</h2>')
            if _req_db_paths or _campaign_path:
                html.addcontent(f'<p>{len(REQ_DB.getallreqs())} requirements loaded</p>')
            if _test_suite_paths or _campaign_path:
                html.addcontent(f'<p>{len(REQ_TRACEABILITY.scenarios)} scenarios loaded</p>')
