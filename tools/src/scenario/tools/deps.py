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

import os
import typing

import scenario


def shouldupdate(
        output,  # type: scenario.Path
        inputs,  # type: typing.List[scenario.Path]
):  # type: (...) -> bool
    """
    Checks that a file should be updated on the basis of its input file modification dates.

    :param output: File to update.
    :param inputs: Input files.
    :return: :const:`True` when an input file is newer than the output file, :const:`False` otherwise.
    """
    def filetime(
            path,  # type: scenario.Path
    ):  # type: (...) -> float
        assert path.is_file()
        _stat = path.stat()  # type: os.stat_result
        for _field in ["st_atime", "st_mtime", "st_ctime"]:  # type: str
            scenario.logging.debug("%s: %s=%s" % (path, _field, scenario.datetime.toiso8601(getattr(_stat, _field))))
        return float(_stat.st_atime) + (float(_stat.st_atime_ns) / 1000000.0)
    assert inputs
    for _input in inputs:  # type: scenario.Path
        if filetime(_input) >= filetime(output):
            return True
    return False
