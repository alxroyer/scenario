# -*- coding: utf-8 -*-

# Copyright 2020-2022 Alexis Royer <https://github.com/Alexis-ROYER/scenario>
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

import tempfile
import time
import typing

import scenario

from .attributes import ScenarioAttribute
from .features import Feature
from .paths import MAIN_PATH


class TestCase(scenario.Scenario):
    """
    Base class for :mod:`scenario.test` test cases.
    """

    def __init__(
            self,
            title,  # type: str
            objective,  # type: str
            features,  # type: typing.List[Feature]
    ):  # type: (...) -> None
        scenario.Scenario.__init__(self)

        # Scenario attributes.
        self.title = title  # type: str
        self.setattribute(ScenarioAttribute.TEST_TITLE, title)
        self.objective = objective  # type: str
        self.setattribute(ScenarioAttribute.TEST_OBJECTIVE, objective)
        self.features = features  # type: typing.List[Feature]
        self.setattribute(ScenarioAttribute.FEATURES, ", ".join([str(_feature) for _feature in features]))

        #: Temporary paths registry.
        self._tmp_paths = []  # type: typing.List[scenario.Path]

        # Main path configuration.
        scenario.Path.setmainpath(MAIN_PATH)

        scenario.handlers.install(scenario.Event.AFTER_TEST, self.rmtmpfiles, scenario=self, once=True)

    def mktmppath(
            self,
            prefix=None,  # type: str
            suffix=None,  # type: str
    ):  # type: (...) -> scenario.Path
        """
        Builds a temporary path.

        :param prefix: Path prefix. None if not set.
        :param suffix: Path suffix. None if not set.
        :return: The temporary path built.
        """
        # First ensure a global 'scenario' container directory exists.
        _root_tmp_dir = scenario.Path.tmp() / "scenario"  # type: scenario.Path
        # Then ensure tmp files will be set in directories named by day.
        # This lets the opportunity to remove old tmp files based on their date info.
        _date = scenario.datetime.toiso8601(time.time())[:len("XXXX-XX-XX")]  # type: str
        _day_tmp_dir = _root_tmp_dir / _date  # type: scenario.Path
        _day_tmp_dir.mkdir(parents=True, exist_ok=True)
        # Eventually build the tmp path in that directory.
        _prefix = type(self).__name__ + "-"  # type: str
        if prefix is not None:
            _prefix += prefix
        _suffix = ""  # type: str
        if suffix is not None:
            _suffix = suffix
        _tmp_path = tempfile.mktemp(dir=_day_tmp_dir, prefix=_prefix, suffix=_suffix)  # type: str

        self._tmp_paths.append(scenario.Path(_tmp_path))
        self.debug("New tmp path: '%s'", self._tmp_paths[-1])
        return self._tmp_paths[-1]

    def rmtmpfiles(
            self,
            event,  # type: str
            data,  # type: typing.Any
    ):  # type: (...) -> None
        """
        Removes temporary files whose names have been computed with :meth:`mktmppath()`.

        :param event: Unused.
        :param data: Unused.
        """
        while self._tmp_paths:
            _tmp_path = self._tmp_paths.pop(0)  # type: scenario.Path
            if _tmp_path.is_file():
                # Remove the file when it exists.
                self.debug("Removing '%s'", _tmp_path)
                _tmp_path.unlink()
            # Remove empty directories.
            while not _tmp_path.is_dir():
                _tmp_path = _tmp_path.parent
            while _tmp_path.is_dir() and (not _tmp_path.samefile(scenario.Path.tmp())):
                if not _tmp_path.iterdir():
                    self.debug("Removing '%s'", _tmp_path)
                    _tmp_path.rmdir()
                    _tmp_path = _tmp_path.parent
                else:
                    self.debug("Non-empty directory '%s'", _tmp_path)
                    break
