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

import tempfile
import time
import typing

import scenario


class TestCase(scenario.Scenario):
    """
    Base class for :mod:`scenario.test` test cases.
    """

    def __init__(
            self,
            title,  # type: str
            description,  # type: scenario.types.AnyLongText
    ):  # type: (...) -> None
        from ._paths import ROOT_SCENARIO_PATH

        scenario.Scenario.__init__(self, title=title, description=description)

        #: Temporary paths registry.
        self._tmp_paths = []  # type: typing.List[scenario.Path]

        # Main path configuration.
        scenario.Path.setmainpath(ROOT_SCENARIO_PATH)

        scenario.handlers.install(
            scenario.Event.AFTER_TEST,
            lambda event, data: self.rmtmpfiles(),
            scenario=self,
            once=True,
        )

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
        self.debug("New tmp path %s ('%s')", self.getpathdesc(self._tmp_paths[-1]), self._tmp_paths[-1])
        return self._tmp_paths[-1]

    def rmtmpfiles(self):  # type: (...) -> None
        """
        Removes temporary files whose names have been computed with :meth:`mktmppath()`.
        """
        # Local constants.
        _NON_RELEVANT_SUFFIXES = (
            ".pyc",
        )  # type: typing.Tuple[str, ...]

        # Inner functions.
        def _rmdir(tmp_dir_path):  # type: (scenario.Path) -> bool
            """
            Recursively tries to remove non relevant sub-files and directories,
            then the directory itself.

            :param tmp_dir_path: Directory path to process.
            :return: ``True`` if the directory has been removed, ``False`` if not.
            """
            # List `tmp_path` and remove non relevant sub-files and sub-directories.
            for _subpath in tmp_dir_path.iterdir():  # type: scenario.Path
                if _subpath.is_file() and (_subpath.suffix in _NON_RELEVANT_SUFFIXES):
                    self.debug("Removing '%s'", _subpath)
                    _subpath.unlink()
                elif _subpath.is_dir():
                    # Recursive call.
                    if not _rmdir(_subpath):
                        return False

            # List `tmp_path` again.
            if not list(tmp_dir_path.iterdir()):
                self.debug("Removing '%s'", tmp_dir_path)
                tmp_dir_path.rmdir()
                return True
            else:
                self.debug("Non-empty directory '%s'", tmp_dir_path)
                return False

        # Note:
        # Do not pop the temporary paths from the cache yet, in order not to change their 'tmp#%d' representation
        # until all temporary paths have been removed.
        for _tmp_path in self._tmp_paths:  # type: scenario.Path
            # Remove the file when it exists.
            if _tmp_path.is_file():
                self.debug("Removing %s ('%s')", self.getpathdesc(_tmp_path), _tmp_path)
                _tmp_path.unlink()

            # Ensure `_tmp_path` is a directory.
            while not _tmp_path.is_dir():
                _tmp_path = _tmp_path.parent

            # Remove empty directories upward, up to the main *tmp* directory.
            while _tmp_path.is_dir() and (not _tmp_path.samefile(scenario.Path.tmp())):
                if not _rmdir(_tmp_path):
                    break
                _tmp_path = _tmp_path.parent

        # Eventually reset the temporary path cache.
        self._tmp_paths.clear()

    def getpathdesc(
            self,
            path,  # type: scenario.Path
    ):  # type: (...) -> str
        """
        Retrieves a description for a path.

        :param path: Either a temporary or regular file path.
        :return: File path description.
        """
        if path.is_relative_to(scenario.Path.tmp()):
            for _index in range(len(self._tmp_paths)):  # type: int
                if self._tmp_paths[_index] == path:
                    return f"tmp#{_index + 1}"
        return f"'{path}'"
