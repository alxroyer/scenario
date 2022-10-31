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

import typing


class StatExpectations:
    def __init__(
            self,
            item_type,  # type: str
            executed_count,  # type: typing.Optional[int]
            total_count,  # type: typing.Optional[int]
    ):  # type: (...) -> None
        self.item_type = item_type  # type: str
        self.executed = executed_count  # type: typing.Optional[int]
        self.total = total_count  # type: typing.Optional[int]

    @staticmethod
    def sum(
            stat_type,  # type: str
            subs,  # type: typing.Optional[typing.List[typing.Any]]
    ):  # type: (...) -> StatExpectations
        assert stat_type in ("steps", "actions", "results")
        if subs is None:
            return StatExpectations(stat_type, None, None)

        _sum = StatExpectations(stat_type, 0, 0)  # type: StatExpectations
        _attr_name = stat_type[:-1] + "_stats"  # type: str
        for _sub in subs:  # type: typing.Any
            _sub_stats = getattr(_sub, _attr_name)  # type: StatExpectations
            if _sub_stats.total is None:
                return StatExpectations(stat_type, None, None)
            else:
                assert _sum.total is not None
                _sum.total += _sub_stats.total

            if _sub_stats.executed is None:
                _sum.executed = None
            elif _sum.executed is not None:
                _sum.executed += _sub_stats.executed
        return _sum
