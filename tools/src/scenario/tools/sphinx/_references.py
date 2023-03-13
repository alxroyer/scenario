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
        debug_indentation="",  # type: str
        short_ref=None,  # type: str
):  # type: (...) -> None
    """
    Recursive function applied in the end on final doc trees.
    """
    from ._sphinxlogging import SphinxLogger

    _logger = SphinxLogger("simplifyreferences()", enable_debug=True)  # type: SphinxLogger

    _logger.debug("%ssimplifyreferences(docname=%r, element=%r, short_ref=%r): element.attributes=%r",
                  debug_indentation, docname, element, short_ref, element.attributes)

    # :class:`docutils.nodes.reference` node: determine the short reference when applicable.
    if isinstance(element, docutils.nodes.reference):
        _reference = element  # type: docutils.nodes.reference
        _reftitle = _reference.get("reftitle", "")  # type: str
        _match = re.match(r"^scenario\.([_a-z0-9]+)\.(.*)", _reftitle)
        if _match:
            short_ref = _match.group(2)
        else:
            _logger.debug("%ssimplifyreferences(docname=%r): 'reftitle' %r does not match pattern",
                          debug_indentation, docname, _reftitle)

    for _child_index in range(len(element.children)):  # type: int
        _child = element.children[_child_index]  # type: docutils.nodes.Node
        if isinstance(_child, docutils.nodes.Text):
            # Text children: simplify the text when `short_ref` is set.
            if short_ref is not None:
                _short_ref = short_ref  # type: str
                if _child.endswith("()"):
                    _short_ref += "()"
                if _short_ref.endswith(_child):
                    _logger.debug("%ssimplifyreferences(docname=%r): Text %r is even shorter than %r, don't change it",
                                  debug_indentation, docname, _child, short_ref)
                elif _child.endswith(_short_ref):
                    _logger.debug("%ssimplifyreferences(docname=%r): Simplifying %r >> %r",
                                  debug_indentation, docname, _child, _short_ref)
                    element.children[_child_index] = docutils.nodes.Text(_short_ref)
                else:
                    _logger.warning(f"{docname}: Mismatching text {_child!r} with expected short reference {short_ref!r}")
        elif isinstance(_child, docutils.nodes.Element):
            # Element children: make recursive calls.
            simplifyreferences(docname, _child, debug_indentation=f"{debug_indentation} ", short_ref=short_ref)
        else:
            _logger.warning(f"{docname}: Unexpected kind of node {_child!r}")
