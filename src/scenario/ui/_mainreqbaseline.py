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
Main requirement baseline storage for :mod:`scenario.ui`.
"""

import scenario


class UIMainReqBaseline(scenario.ReqBaselineObject):
    """
    Main requirement baseline storage.

    Instantiated once with the :data:`UI_MAIN_REQ_BASELINE` singleton.
    """

    def __init__(self):  # type: (...) -> None
        """
        Simple initialization of a :class:`scenario._reqblobj.ReqBaselineObject`,
        without requirement baseline at first.
        """
        scenario.ReqBaselineObject.__init__(self)

    def set(
            self,
            req_baseline,  # type: scenario.ReqBaseline
    ):  # type: (...) -> None
        """
        Sets the main requirement baseline.

        :param req_baseline: Main requirement baseline.
        """
        super()._setreqbaseline(req_baseline, force=True)


#: Main instance of :class:`UIMainReqBaseline`.
UI_MAIN_REQ_BASELINE = UIMainReqBaseline()  # type: UIMainReqBaseline
