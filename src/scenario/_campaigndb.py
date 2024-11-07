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
Campaign database.
"""

import typing

if True:
    from ._debugclasses import DebugClass as _DebugClassImpl  # @perf
    from ._fastpath import FAST_PATH as _FAST_PATH  # @perf
    from ._logger import Logger as _LoggerImpl  # @inheritance
if typing.TYPE_CHECKING:
    from ._campaignexecution import CampaignExecution as _CampaignExecutionType
    from ._path import Path as _PathType
    from ._reqbl import ReqBaseline as _ReqBaselineType


class CampaignDatabase(_LoggerImpl):
    """
    Campaign database.
    """

    def __init__(self):  # type: (...) -> None
        """
        Initializes an empty database.
        """
        _LoggerImpl.__init__(self, _DebugClassImpl.CAMPAIGN_DB)

        #: List of campaign executions loaded.
        self.campaign_executions = []  # type: typing.List[_CampaignExecutionType]

    def load(
            self,
            *,
            read_scenario_logs=False,  # type: bool
            read_scenario_reports=False,  # type: bool
            log_info=True,  # type: bool
    ):  # type: (...) -> None
        """
        Relaods the database from the campaign output directory.

        :param read_scenario_logs:
            ``True`` to read automatically scenario log files.
        :param read_scenario_reports:
            ``True`` to read automatically scenario report files, and feed the requirement baseline by the way.

            Feeds the requirement baseline with the scenario definitions read from the reports.
        :param log_info: ``True`` (by default) to generate info logging.

        .. seealso:: :meth:`._scenarioconfig.ScenarioConfig.campaignoutdir()` for campaign output directory configuration.
        """
        from ._campaignexecution import CampaignExecution
        from ._reqbl import ReqBaseline

        if log_info:
            _FAST_PATH.main_logger.info("Loading campaign results")
        with _FAST_PATH.main_logger.pushindentation("  "):
            if self.campaign_executions:
                if log_info:
                    _FAST_PATH.main_logger.info("Resetting campaign result database")
                self.campaign_executions.clear()

            self.debug("Listing directories in '%s'", _FAST_PATH.scenario_config.campaignoutdir())
            for _path in sorted(_FAST_PATH.scenario_config.campaignoutdir().iterdir(), key=lambda path: path.name):  # type: _PathType
                # Check whether the given path corresponds to a faithful campaign output directory.
                if not _path.is_dir():
                    self.debug("Not a directory '%s'", _path)
                    continue
                with ReqBaseline(name="tmp"):  # For tmp `CampaignExecution` instantiation below.
                    _campaign_execution = CampaignExecution(_path)  # type: _CampaignExecutionType
                    if not _campaign_execution.campaign_report_path.is_file():
                        self.debug("No '%s' report file in '%s'", _campaign_execution.campaign_report_path, _path)
                        continue

                try:
                    if log_info:
                        _FAST_PATH.main_logger.info(f"Loading '{_path}'")
                    self.campaign_executions.append(
                        _FAST_PATH.campaign_report.readcampaignreport(
                            _campaign_execution.campaign_report_path,
                            # Let the requirement baseline be automatically instantiated.
                            req_baseline=None,
                            # Save scenario logs and reports as required.
                            read_scenario_logs=read_scenario_logs,
                            read_scenario_reports=read_scenario_reports,
                        ),
                    )
                except Exception as _err:
                    self.warning(f"Error while loading campaign results for '{_path}': {_err!r}")
        if log_info:
            _FAST_PATH.main_logger.info(f"{len(self.campaign_executions)} campaign results loaded")

    def get(
            self,
            *,
            name=None,  # type: str
            path=None,  # type: _PathType
            req_baseline=None,  # type: _ReqBaselineType
    ):  # type: (...) -> _CampaignExecutionType
        """
        Retrieves the campaign execution instance for the given campaign report path.

        :param name: Search a campaign from its name.
        :param path: Search a campaign from a path, either its output directory or its report path.
        :param req_baseline: Search a campaign from a requirement baseline.
        :return: Campaign execution if found.
        :raise KeyError: If not found.
        """
        if not any([
            name is not None,
            path is not None,
            req_baseline is not None,
        ]):
            raise Exception("No campaign criteria provided")

        # Search for a campaign matching all criteria.
        for _campaign_execution in self.campaign_executions:  # type: _CampaignExecutionType
            if (name is not None) and (_campaign_execution.name != name):
                continue
            if (path is not None) and (_campaign_execution.outdir != path) and (_campaign_execution.campaign_report_path != path):
                continue
            if (req_baseline is not None) and (_campaign_execution.req_baseline is not req_baseline):
                continue
            return _campaign_execution

        _criteria = []  # type: typing.List[str]
        if name is not None:
            _criteria.append(f"name {name!r}")
        if path is not None:
            _criteria.append(f"path '{path}'")
        if req_baseline:
            _criteria.append(f"requirement baseline {req_baseline!r}")
        raise KeyError(f"No such campaign with {', '.join(_criteria)}")


#: Main instance of :class:`CampaignDatabase`.
#:
#: Also available as :attr:`._fastpath.FastPath.campaign_db`.
#: Please prefer the latter instead of using local imports of this module.
CAMPAIGN_DB = CampaignDatabase()  # type: CampaignDatabase
