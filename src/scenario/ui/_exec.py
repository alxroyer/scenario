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
User interface action execution handler.
"""
import typing

import scenario

if True:
    from ._httprequesthandler import HttpRequestHandler as _HttpRequestHandlerImpl  # @inheritance
if typing.TYPE_CHECKING:
    from ._htmldoc import HtmlDocument as _HtmlDocumentType
    from ._httprequest import HttpRequest as _HttpRequestType


class Exec(_HttpRequestHandlerImpl):
    """
    Action execution request handler.

    Executes actions and returns a ``{"return_code": int, "title": str, "text": str}`` JSON result.
    """

    #: Base URL for action executions.
    _URL = "/execute"  # type: str

    class Arg(scenario.enum.StrEnum):
        """
        URL argument names.
        """
        #: Action argument.
        #:
        #: See :class:`Exec.Action` for possible values.
        ACTION = "action"

    class Action(scenario.enum.StrEnum):
        """
        :attr:`Exec.Arg.ACTION` values.
        """
        #: Reload the main requirement baseline.
        RELOAD_MAIN_REQ_BASELINE = "reload-main-req-baseline"
        #: Reload the campaign database.
        RELOAD_CAMPAIGN_DB = "reload-campaign-db"

    @staticmethod
    def mkurl(
            action,  # type: Exec.Action
            *,
            req_baseline=None,  # type: typing.Optional[scenario.ReqBaseline]
    ):  # type: (...) -> str
        """
        Builds an action execution URL.

        :param action: Action to create an URL for.
        :param req_baseline: Baseline to execute the action for. Main requirement baseline by default.
        :return: Action execution URL.
        """
        from ._reqbl import UI_REQ_BASELINES
        from ._httprequest import HttpRequest

        return HttpRequest.encodeurl(
            Exec._URL,
            args={
                **HttpRequest.mkurlargs(obj=req_baseline or UI_REQ_BASELINES.main),
                Exec.Arg.ACTION: action,
            },
        )

    @staticmethod
    def execresultdiv2html(
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Generates the hidden ``.exec-result`` popup div.

        Hidden by default.
        Used by '_exec.js' to display execution results.

        :param html: HTML output page to feed.
        """
        from ._htmlgenbuttons import ButtonGenerator

        with html.addnode("div", id="exec-result", classes=["exec-result", "background"], style="display: none;"):
            with html.addnode("div", classes=["exec-result", "foreground"]):
                html.addnode("div", classes=["exec-result", "title"])
                html.addnode("div", classes=["exec-result", "text"])
                ButtonGenerator(html).addbutton(
                    classes=["exec-result", "validate"],
                    text="OK",
                )

    @staticmethod
    def actionbutton2html(
            html,  # type: _HtmlDocumentType
            request,  # type: _HttpRequestType
            action,  # type: Exec.Action
    ):  # type: (...) -> None
        """
        Creates an action execution button.

        :param html: HTML output page to feed.
        :param request: Current request being processed.
        :param action: Action to create a button for.
        """
        from ._htmlgenbuttons import ButtonGenerator
        from ._reqbl import UI_REQ_BASELINES

        _url = ""  # type: str
        _classes = ["exec"]  # type: typing.List[str]
        _text = "..."  # type: str
        _title = None  # type: typing.Optional[str]

        if action == Exec.Action.RELOAD_MAIN_REQ_BASELINE:
            # Don't display the `.reload-main-req-baseline` button if the page is not for it.
            if request.req_baseline is not UI_REQ_BASELINES.main:
                return

            _url = Exec.mkurl(Exec.Action.RELOAD_MAIN_REQ_BASELINE)
            _classes.append(Exec.Action.RELOAD_MAIN_REQ_BASELINE)
            _text = "Reload"
            _title = "Reload the main baseline (tests and requirements)"

        elif action == Exec.Action.RELOAD_CAMPAIGN_DB:
            _url = Exec.mkurl(Exec.Action.RELOAD_CAMPAIGN_DB)
            _classes.append(Exec.Action.RELOAD_CAMPAIGN_DB)
            _text = "Reload campaigns"
            _title = "Relaod the campaign database"

        else:
            raise ValueError(f"Unknown action {action!r}")

        ButtonGenerator(html).addbutton(
            href=_url,
            classes=_classes,
            title=_title,
            text=_text,
        )

    def __init__(self):  # type: (...) -> None
        """
        Configures the logger instance.
        """
        from ._debugclasses import UIDebugClass

        _HttpRequestHandlerImpl.__init__(self, UIDebugClass.EXEC)

    def process(
            self,
            request,  # type: _HttpRequestType
    ):  # type: (...) -> bool
        from .._scenarioconfig import SCENARIO_CONFIG
        from ._reqbl import UI_REQ_BASELINES

        # Filter `request`.
        if not request.base_path.startswith(Exec._URL):
            self.debug("Unexpected base path %r", request.base_path)
            self.debug("%r not processed", request)
            return False

        # Prepare return values.
        _title = ""  # type: str
        _return_code = scenario.ErrorCode.INPUT_MISSING_ERROR  # type: scenario.ErrorCode
        _text = f"'{Exec.Arg.ACTION}' parameter missing."  # type: str

        # Read ACTION parameter.
        _action = request.getarg(Exec.Arg.ACTION, default="")  # type: str

        # Execute actions.
        try:
            if _action == Exec.Action.RELOAD_MAIN_REQ_BASELINE:
                _title = "Reload main requirement baseline"

                UI_REQ_BASELINES.main = scenario.ReqBaseline.fromfiles(
                    name=UI_REQ_BASELINES.main.name,
                    req_db_paths=SCENARIO_CONFIG.reqdbpaths() or None,
                    test_suite_paths=SCENARIO_CONFIG.testsuitepaths() or None,
                    log_info=True,
                )

                _return_code = scenario.ErrorCode.SUCCESS
                _text = "Main requirement baseline reloaded successfully: "
                if UI_REQ_BASELINES.main.req_db.getallreqs():
                    _text += f"{len(UI_REQ_BASELINES.main.req_db.getallreqs())} requirements and "
                _text += f"{len(UI_REQ_BASELINES.main.scenarios)} tests loaded."

            elif _action == Exec.Action.RELOAD_CAMPAIGN_DB:
                _title = "Reload campaigns"

                scenario.campaign_db.load()

                _return_code = scenario.ErrorCode.SUCCESS
                _text = f"{len(scenario.campaign_db.campaign_executions)} campaigns reloaded successfully."

            else:
                _title = "Action error"
                _return_code = scenario.ErrorCode.INPUT_FORMAT_ERROR
                _text = f"Invalid '{Exec.Arg.ACTION}' parameter {_action!r}"

        except Exception as _err:
            _return_code = scenario.ErrorCode.fromexception(_err)
            _text = repr(_err)

        # Return result.
        _res = {
            "return_code": _return_code.value,
            "title": _title,
            "text": _text,
        }  # type: scenario.types.JsonDict
        self.debug("Execution result: %r", _res)
        request.sendjson(_res)
        return True
