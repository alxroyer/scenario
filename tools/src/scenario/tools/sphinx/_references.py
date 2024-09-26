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

import docutils.nodes
import re


def simplifyreferences(
        docname,  # type: str
        element,  # type: docutils.nodes.Element
        short_ref_package=None,  # type: str
        short_ref_name=None,  # type: str
):  # type: (...) -> None
    """
    Recursive function applied in the end on final doc trees.
    """
    from ._logging import Logger

    _logger = Logger.getinstance(Logger.Id.SIMPLIFY_REFERENCES)  # type: Logger

    _logger.debug("simplifyreferences(docname=%r, element=%r, short_ref_package=%r, short_ref_name): element.attributes=%r",
                  docname, element, short_ref_package, short_ref_name, element.attributes)

    # :class:`docutils.nodes.reference` node: determine the short reference when applicable.
    if isinstance(element, docutils.nodes.reference):
        _reference = element  # type: docutils.nodes.reference
        _reftitle = _reference.get("reftitle", "")  # type: str
        _match = re.match(r"^(scenario\.)(ui\.|)([_a-z0-9]+)\.(.*)", _reftitle)
        if _match:
            if _match.group(2):
                short_ref_package = _match.group(1) + _match.group(2)
            short_ref_name = _match.group(4)
        else:
            _logger.debug("'reftitle' %r does not match pattern", _reftitle)

    for _child_index in range(len(element.children)):  # type: int
        _child = element.children[_child_index]  # type: docutils.nodes.Node
        if isinstance(_child, docutils.nodes.Text):
            # Text children: simplify the text when `short_ref` is set.
            if short_ref_name is not None:
                _short_ref_name = short_ref_name  # type: str
                if _child.endswith("()"):
                    _short_ref_name += "()"

                if _short_ref_name.endswith(_child):
                    _logger.debug("Text %r is even shorter than %r, don't change it", _child, _short_ref_name)
                elif _child.endswith(_short_ref_name):
                    _short_ref = (short_ref_package or "") + _short_ref_name  # type: str
                    _logger.debug("Simplifying %r >> %r", _child, _short_ref)
                    element.children[_child_index] = docutils.nodes.Text(_short_ref)
                else:
                    _logger.warning(f"{docname}: Mismatching text {_child!r} with expected short reference {short_ref_name!r}")
        elif isinstance(_child, docutils.nodes.Element):
            # Element children: make recursive calls.
            with _logger.scenario_logger.pushindentation("  "):
                simplifyreferences(
                    docname, _child,
                    short_ref_package=short_ref_package,
                    short_ref_name=short_ref_name,
                )
        else:
            _logger.warning(f"{docname}: Unexpected kind of node {_child!r}")
