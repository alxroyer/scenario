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

    class InputName(_StrEnumImpl):
        """
        Form input names.
        """
        #: Name of the hidden input that gives the id of the form actually executed: either "1" or "2".
        FORM_ID = "form-id"

        #: Form#1: Multiline input text that gives requirement file paths.
        REQ_DB_PATHS = "req-db-path"
        #: Form#1: Multiline input text that gives test suite file paths.
        TEST_SUITE_PATHS = "test-suite-paths"

        #: Form#2: Input text that gives a path for a campaign directory or report file.
        CAMPAIGN_PATH = "campaign-path"

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
        from ._httprequest import HttpRequest

        html.settitle("Configuration")

        # Form application.
        if request.method == HttpRequest.Method.POST:
            self._applyform(request, html)

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

        with html.addcontent('<div id="conf1"></div>'):
            with html.addcontent(f'<form action="{Configuration.URL}" method="post"></form>'):
                # Form id.
                html.addcontent(f'<input type="hidden" name="{Configuration.InputName.FORM_ID}" value="1" />')

                # Requirements file.
                html.addcontent('<p>Requirements:</p>')
                with html.addcontent(
                    f'<textarea name="{Configuration.InputName.REQ_DB_PATHS}" rows="10" '
                    'placeholder="List of requirement files (absolute paths)"></textarea>',
                ):
                    # Ensure a empty text node at least for `<textarea/>` (otherwise HTML fails with empty `<textarea/>`).
                    _text_node = html.current_node.appendchild(html.xml_doc.createtextnode(""))  # type: Xml.TextNode
                    # Then add a line for each requirement file.
                    for _req_db_path in SCENARIO_CONFIG.reqdbfiles():  # type: Path
                        if _text_node.data:
                            _text_node.data += "\n"
                        _text_node.data += _req_db_path.abspath

                # Test suite files.
                html.addcontent('<p>Test suites:</p>')
                with html.addcontent(
                    f'<textarea name="{Configuration.InputName.TEST_SUITE_PATHS}" rows="10" '
                    'placeholder="List of test suite file (absolute paths)"></textarea>',
                ):
                    # Ensure a empty text node at least for `<textarea/>` (otherwise HTML fails with empty `<textarea/>`).
                    _text_node = html.current_node.appendchild(html.xml_doc.createtextnode(""))  # Type already defined above.
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
        with html.addcontent('<div id="conf2"></div>'):
            with html.addcontent('<form action="/configuration" method="post"></form>'):
                # Form id.
                html.addcontent(f'<input type="hidden" name="{Configuration.InputName.FORM_ID}" value="2" />')

                # Campaign path (directory or campaign report).
                html.addcontent('<p>Campaign:</p>')
                html.addcontent(f'<input type="text" name="{Configuration.InputName.CAMPAIGN_PATH}" />')

                # Submit.
                html.addcontent('<input type="submit" value="Apply" />')

    def _applyform(
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

        _req_db_paths = []  # type: typing.List[Path]
        _test_suite_paths = []  # type: typing.List[Path]
        _campaign_path = None  # type: typing.Optional[Path]

        if request.getarg(Configuration.InputName.FORM_ID) == "1":
            for _req_db_path in request.getarg(Configuration.InputName.REQ_DB_PATHS, default="").splitlines():  # type: str
                if _req_db_path.strip():
                    _req_db_paths.append(Path(_req_db_path.strip()))

            for _test_suite_path in request.getarg(Configuration.InputName.TEST_SUITE_PATHS, default="").splitlines():  # type: str
                if _test_suite_path.strip():
                    _test_suite_paths.append(Path(_test_suite_path.strip()))

            REQ_TRACEABILITY.loaddatafromfiles(
                req_db_file_paths=_req_db_paths or None,
                test_suite_paths=_test_suite_paths or None,
                log_info=True,
            )

        elif request.getarg(Configuration.InputName.FORM_ID) == "2":
            if request.getarg(Configuration.InputName.CAMPAIGN_PATH).strip():
                _campaign_path = Path(request.getarg(Configuration.InputName.CAMPAIGN_PATH).strip())

                REQ_TRACEABILITY.loaddatafromcampaignresults(
                    campaign_results=_campaign_path,
                    log_info=True,
                )

        else:
            raise KeyError(f"Unexpected form identifier {request.getarg(Configuration.InputName.FORM_ID)!r}")

        with html.addcontent('<div class="exec-result"></div>'):
            html.addcontent('<h2>Execution result</h2>')
            if _req_db_paths or _campaign_path:
                html.addcontent(f'<p>{len(REQ_DB.getallreqs())} requirements loaded</p>')
            if _test_suite_paths or _campaign_path:
                html.addcontent(f'<p>{len(REQ_TRACEABILITY.scenarios)} scenarios loaded</p>')
