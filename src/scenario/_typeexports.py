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
Types exported as :attr:`scenario.types`.
"""

import typing


# Explicit export declarations (see https://docs.python.org/3/tutorial/modules.html#importing-from-a-package).
__all__ = []  # type: typing.List[str]


if typing.TYPE_CHECKING:
    __doc__ += """
    .. py:attribute:: JsonDict

        .. seealso:: :obj:`._jsondictutils.JsonDictType` implementation.
    """
    from ._jsondictutils import JsonDictType as JsonDict
    __all__.append("JsonDict")

    __doc__ += """
    .. py:attribute:: SetWithReqLinks

        .. seealso:: :obj:`._reqtypes.SetWithReqLinksType` implementation.
    """
    from ._reqtypes import SetWithReqLinksType as SetWithReqLinks
    __all__.append("SetWithReqLinks")

    __doc__ += """
    .. py:attribute:: OrderedSet

        .. seealso:: :obj:`._setutils.OrderedSetType` implementation.
    """
    from ._setutils import OrderedSetType as OrderedSet
    __all__.append("OrderedSet")

    __doc__ += """
    .. py:attribute:: VarItem

        .. seealso:: :obj:`._typeutils.VarItemType` implementation.
    """
    from ._typeutils import VarItemType as VarItem
    __all__.append("VarItem")
