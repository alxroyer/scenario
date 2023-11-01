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

    _logger = Logger.getinstance(Logger.Id.TRACK_DOCUMENTED_ITEMS)  # type: Logger
    _logger.debug("trackmoduleitems(module=%r)", module)

    # Use `sphinx.pycode.Parser.annotations` to find out typed items in the module.
    # Don't use `vars()`, otherwise all neighbour modules that import an original item will be tracked as well.
    # Such imported items are not the ones we are interested in here.
    # Note: It means that untyped items won't be tracked by the way. So much the worse!
    _parser = sphinx.pycode.Parser(inspect.getsource(module))  # type: sphinx.pycode.Parser
    _parser.parse()
    for _class_name, _obj_name in _parser.annotations:  # type: str, str
        # Do not track private attributes.
        if _obj_name.startswith("__"):
            continue

        # Compute fqname and item type.
        if _class_name:
            _fq_name = f"{module.__name__}.{_class_name}.{_obj_name}"  # type: str
            _obj_type = "attribute"  # type: str
        else:
            _fq_name = f"{module.__name__}.{_obj_name}"  # Type already declared above
            _obj_type = "data"  # Type already declared above
            if inspect.isfunction(getattr(module, _obj_name)):
                _obj_type = "function"

        # Memorize the tracked item.
        if _fq_name not in TRACKED_ITEMS:
            _logger.debug("Tracking %s `%s`", _obj_type, _fq_name)
            TRACKED_ITEMS[_fq_name] = _obj_type
        else:
            _logger.debug("Already tracked %s `%s`", _obj_type, _fq_name)
            if TRACKED_ITEMS[_fq_name] != _obj_type:
                _logger.warning(f"Unexpected type {_obj_type} for {TRACKED_ITEMS[_fq_name]} `{_fq_name}`")

        # Check consistency with `DOCUMENTED_ITEMS`.
        if _fq_name in DOCUMENTED_ITEMS:
            _logger.debug("Documented %s `%s` found", _obj_type, _fq_name)
            if DOCUMENTED_ITEMS[_fq_name].type != _obj_type:
                _logger.warning(f"Unexpected type {_obj_type} for {DOCUMENTED_ITEMS[_fq_name].type} `{_fq_name}`")


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


def savedocumenteditem(
        fq_name,  # type: str
        obj_type,  # type: str
        obj,  # type: object
        lines,  # type: typing.List[str]
):  # type: (...) -> None
    from ._logging import Logger

    _logger = Logger.getinstance(Logger.Id.TRACK_DOCUMENTED_ITEMS)  # type: Logger

    # Memorize the documented item.
    if fq_name not in DOCUMENTED_ITEMS:
        _logger.debug("Documented %s `%s`", obj_type, fq_name)
        DOCUMENTED_ITEMS[fq_name] = DocumentedItem(obj_type, obj, lines)
    else:
        _logger.debug("Already documented %s `%s`", obj_type, fq_name)
        if DOCUMENTED_ITEMS[fq_name].type != obj_type:
            _logger.warning(f"Unexpected type {obj_type} for {DOCUMENTED_ITEMS[fq_name].type} `{fq_name}`")

    # Check consistency with `TRACKED_ITEMS`.
    if fq_name in TRACKED_ITEMS:
        _logger.debug("Tracked %s `%s` found", obj_type, fq_name)
        if TRACKED_ITEMS[fq_name] != obj_type:
            _logger.warning(f"Unexpected type {obj_type} for {TRACKED_ITEMS[fq_name]} `{fq_name}`")


def warnundocitems():  # type: (...) -> None
    from ._logging import Logger

    _logger = Logger.getinstance(Logger.Id.TRACK_DOCUMENTED_ITEMS)  # type: Logger

    # Print out console warnings for non documented tracked items.
    for _fq_name in TRACKED_ITEMS:  # type: str
        if _fq_name not in DOCUMENTED_ITEMS:
            _logger.warning(f"Undocumented {TRACKED_ITEMS[_fq_name]} `{_fq_name}`")
