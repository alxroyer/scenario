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
:mod:`scenario` package information.
"""

import typing


class PackageInfo:
    """
    Package information.
    """

    @property
    def version(self):  # type: () -> str
        """
        Current version of the :mod:`scenario` package as a `semver <https://semver.org/>`_ string.

        :return: ``"x.y.z"`` version string.
        """
        return ".".join([str(_i) for _i in self.version_tuple])

    @property
    def version_tuple(self):  # type: () -> typing.Tuple[int, int, int]
        """
        Current version of the :mod:`scenario` package as a `semver <https://semver.org/>`_ tuple.

        :return: ``(x, y, z)`` version tuple.
        """
        return 0, 2, 2


__doc__ += """
.. py:attribute:: PKG_INFO

    Main :class:`PackageInfo` instance.
"""
PKG_INFO = PackageInfo()
