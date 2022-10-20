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


def ordinal(
        index,  # type: int
):  # type: (...) -> str
    if index == 0:
        return "1st"
    if index == 1:
        return "2nd"
    if index == 2:
        return "3rd"
    return "%dth" % (index + 1)


def adverbial(
        count,  # type: int
):  # type: (...) -> str
    if count == 0:
        return "none"
    if count == 1:
        return "once"
    if count == 2:
        return "twice"
    return "%d times" % count
