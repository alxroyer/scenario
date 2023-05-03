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
Configuration key management.
"""


class ConfigKey:
    """
    Configuration key utils.
    """

    @staticmethod
    def join(
            a,  # type: str
            b,  # type: str
    ):  # type: (...) -> str
        """
        Joins key parts.

        :param a: First key part to join.
        :param b: Second key part to join.
        :return: Concatenation of the two key parts.
        """
        if not a:
            return b
        if not b:
            return a
        if b.startswith("["):
            return f"{a}{b}"
        return f"{a}.{b}"
