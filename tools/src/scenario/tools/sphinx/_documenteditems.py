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

import inspect
import re
import sphinx.pycode
import types
import typing


#: Dictionary of {fully qualified name: type of object}.
TRACKED_ITEMS = {}  # type: typing.Dict[str, str]


def trackmoduleitems(
        module,  # type: types.ModuleType
):  # type: (...) -> None
    """
    Identify items to track from a Python module, especially attributes.

    :param module: Module to track items from.

    .. warning:: Does not track untyped attributes.
    """
    from ._logging import Logger

    _logger = Logger.getinstance(Logger.Id.TRACK_MODULE_ITEMS)  # type: Logger
    _logger.debug("trackmoduleitems(module=%r)", module)

    assert inspect.ismodule(module), f"Not a module {module!r}"
    _parser = sphinx.pycode.Parser(inspect.getsource(module))  # type: sphinx.pycode.Parser
    _parser.parse()
    for _class_name, _attr_name in _parser.annotations:  # type: str, str
        _track_item = True  # type: bool

        # Do not track private attributes.
        if _attr_name.startswith("__"):
            continue
        if _class_name:
            _fq_name = f"{module.__name__}.{_class_name}.{_attr_name}"  # type: str
            _item_type = "attribute"  # type: str
        else:
            _fq_name = f"{module.__name__}.{_attr_name}"
            _item_type = "data"
            if module.__doc__:
                for _line in module.__doc__.splitlines():  # type: str
                    if re.match(r"\.\. py:attribute:: %s" % _attr_name, _line):
                        _logger.debug("Attribute '%s' already described in the '%s' module docstring. No need to track it.", _attr_name, module.__name__)
                        _track_item = False
                        break
            if _track_item:
                _logger.warning(f"Missing `.. py:attribute::` directive for attribute '{_attr_name}' in module '{module.__name__}'")

        if _track_item:
            _logger.debug("Tracking %s `%s`", _item_type, _fq_name)
            TRACKED_ITEMS[_fq_name] = _item_type


class DocumentedItem:

    def __init__(
            self,
            obj_type,  # type: str
            obj,  # type: object
            lines,  # type: typing.List[str]
    ):  # type: (...) -> None
        self.type = obj_type  # type: str
        self.obj = obj  # type: object
        self.lines = lines  # type: typing.List[str]


DOCUMENTED_ITEMS = {}  # type: typing.Dict[str, DocumentedItem]


def warnundocitems():  # type: (...) -> None
    from ._logging import Logger

    _logger = Logger.getinstance(Logger.Id.WARN_UNDOC_ITEMS)  # type: Logger

    # Print out console warnings for non documented tracked items.
    for _undoc_fq_name in TRACKED_ITEMS:  # type: str
        _logger.warning(f"Undocumented {TRACKED_ITEMS[_undoc_fq_name]} `{_undoc_fq_name}`")

    # Reset the documented and tracked item lists.
    DOCUMENTED_ITEMS.clear()
    TRACKED_ITEMS.clear()
