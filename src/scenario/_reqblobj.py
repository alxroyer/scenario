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
Requirement baseline related objects.
"""

import typing

if typing.TYPE_CHECKING:
    from._reqbl import ReqBaseline as _ReqBaselineType
    from ._reqdb import ReqDatabase as _ReqDatabaseType


class ReqBaselineObject:
    """
    Object working with a requirement baseline.
    """

    def __init__(
            self,
            req_baseline=None,  # type: _ReqBaselineType
    ):  # type: (...) -> None
        """
        Saves the given :class:`._reqbl.ReqBaseline`, or waits for one with :meth:`_setreqbaseline()`.

        :param req_baseline: Related :class:`._reqbl.ReqBaseline`, if known at instantiation.
        """
        self.__req_baseline = req_baseline  # type: typing.Optional[_ReqBaselineType]

    def _setreqbaseline(
            self,
            req_baseline,  # type: _ReqBaselineType
            *,
            force=False,  # type: bool
    ):  # type: (...) -> None
        """
        Sets the related requirement baseline.

        :param req_baseline: Related requirement baseline.
        :param force: ``True`` to force rewriting of a new requirement baseline in case a previous one was already set.
        :raise Exception: If the requirement baseline has already been set before (and ``force`` is ``False``).
        """
        if self.__req_baseline and (not force):
            raise Exception(f"Baseline {self.__req_baseline!r} already installed")
        self.__req_baseline = req_baseline

    @property
    def req_baseline(self):  # type: (...) -> _ReqBaselineType
        """
        Related requirement baseline.

        :raise ValueError: If the requirement baseline has not been set yet.
        """
        if self.__req_baseline:
            return self.__req_baseline
        raise ValueError("No requirement baseline installed yet")

    @property
    def req_db(self):  # type: (...) -> _ReqDatabaseType
        """
        Requirement database owned by the related baseline.

        :raise ValueError: If the requirement baseline has not been set yet.
        """
        return self.req_baseline.req_db
