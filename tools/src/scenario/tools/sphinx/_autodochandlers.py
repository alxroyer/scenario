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

import enum
import inspect
import re
import sphinx.application
import sphinx.ext.autodoc
import typing


class AutodocHandlers:
    """
    See [SPHINX_AUTODOC_EVENTS]:

    - https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#docstring-preprocessing
    - https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#skipping-members
    """

    def setup(
            self,
            app,  # type: sphinx.application.Sphinx
    ):  # type: (...) -> None
        app.connect("autodoc-skip-member", self.skipmember)
        app.connect("autodoc-process-signature", self.processsignature)
        app.connect("autodoc-process-docstring", self.processdocstring)

    def skipmember(
            self,
            app,  # type: sphinx.application.Sphinx
            owner_type,  # type: str
            nfq_name,  # type: str
            obj,  # type: typing.Optional[object]
            would_skip,  # type: bool
            options,  # type: typing.Any
    ):  # type: (...) -> typing.Optional[bool]
        """
        See https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#event-autodoc-skip-member

        [SPHINX_AUTODOC_EVENTS]:
            autodoc-skip-member(app, what, name, obj, skip, options)

            Emitted when autodoc has to decide whether a member should be included in the documentation.
            The member is excluded if a handler returns True. It is included if the handler returns False.

            If more than one enabled extension handles the autodoc-skip-member event, autodoc will use the first non-None value returned by a handler.
            Handlers should return None to fall back to the skipping behavior of autodoc and other enabled extensions.

        :param app:
            [SPHINX_AUTODOC_EVENTS]:
                The Sphinx application object
        :param owner_type:
            ``what`` in [SPHINX_AUTODOC_EVENTS]

            [SPHINX_AUTODOC_EVENTS]:
                The type of the object which the docstring belongs to
                (one of "module", "class", "exception", "function", "method", "attribute")"

            .. warning:: Actually the type of the owner object! (see `sphinx#6808 <https://github.com/sphinx-doc/sphinx/issues/6808>`_)
        :param nfq_name:
            ``name`` in [SPHINX_AUTODOC_EVENTS].

            [SPHINX_AUTODOC_EVENTS]:
                The fully qualified name of the object

            .. warning:: Actually not a fully qualified name. (see `sphinx#6808 <https://github.com/sphinx-doc/sphinx/issues/6808>`_)
        :param obj:
            [SPHINX_AUTODOC_EVENTS]:
                The object itself

            .. warning:: May be None, especially for class attributes.
            .. note:: Equal to :attr:`sphinx.ext.autodoc.INSTANCEATTR` for instance attributes.
        :param would_skip:
            ``skip`` in [SPHINX_AUTODOC_EVENTS].

            [SPHINX_AUTODOC_EVENTS]:
                A boolean indicating if autodoc will skip this member if the user handler does not override the decision
        :param options:
            [SPHINX_AUTODOC_EVENTS]:
                The options given to the directive:
                an object with attributes inherited_members, undoc_members, show_inheritance and noindex
                that are true if the flag option of same name was given to the auto directive
        :return:
            [SPHINX_AUTODOC_EVENTS]:
                The member is excluded if a handler returns True. It is included if the handler returns False.
                If more than one enabled extension handles the autodoc-skip-member event,
                autodoc will use the first non-None value returned by a handler.
                Handlers should return None to fall back to the skipping behavior of autodoc and other enabled extensions.
        """
        from scenario._enumutils import StrEnum  # noqa  ## Access to a protected member.
        from ._logging import Logger
        from ._reflection import isspecialfunction, fqname

        _logger = Logger.getinstance(Logger.Id.AUTODOC_SKIP_MEMBER)  # type: Logger
        _logger.debug("AutodocHandlers.skipmember(owner_type=%r, nfq_name=%r, obj=%r, would_skip=%r, options=%r)",
                      owner_type, nfq_name, obj, would_skip, options)
        _logger.debug(f"app.env.ref_context = {app.env.ref_context!r}")
        _logger.debug(f"app.env.ref_context.get('py:module') = {app.env.ref_context.get('py:module')!r}")
        _logger.debug(f"app.env.ref_context.get('py:class') = {app.env.ref_context.get('py:class')!r}")

        # When overriding `enum.Enum`, non-relevant inherited attributes come to be documented.
        # Skip `StrEnum` members which names can be found in the base `enum.Enum` class.
        if (not nfq_name.startswith("__")) and hasattr(enum.Enum, nfq_name):
            if obj is getattr(StrEnum, nfq_name):
                # Memo: `fqname()` may fail on `enum.Enum` members.
                _logger.debug("`%s.%s` skipped!", fqname(StrEnum), nfq_name)
                return True

        if would_skip:
            if inspect.isclass(obj) and (nfq_name != "__metaclass__"):
                _logger.debug("class `%s` not skipped!", fqname(obj))
                return False
            if inspect.isfunction(obj):
                _logger.debug("function `%s` not skipped!", fqname(obj))
                return False
            if inspect.ismethod(obj):
                _logger.debug("method `%s` not skipped!", fqname(obj))
                return False
            if owner_type in ("class", "exception"):
                if obj is not None:
                    if isspecialfunction(obj):
                        _logger.debug("method `%s` not skipped!", fqname(obj))
                        return False
                    if obj is sphinx.ext.autodoc.INSTANCEATTR:
                        _logger.debug("instance attribute `%s` not skipped!", nfq_name)
                        return False
                    if not nfq_name.startswith("__"):
                        _logger.debug("instance attribute `%s` not skipped!", nfq_name)
                        return False
                else:
                    if not nfq_name.startswith("__"):
                        _logger.debug("class attribute `%s` not skipped!", nfq_name)
                        return False

        _logger.debug("skipmember(nfq_name=%r) => default would_skip=%r", nfq_name, would_skip)
        return None

    def processsignature(
            self,
            app,  # type: sphinx.application.Sphinx
            what,  # type: str
            fq_name,  # type: str
            obj,  # type: typing.Optional[object]
            options,  # type: typing.Any
            signature,  # type: typing.Optional[str]
            return_annotation,  # type: typing.Optional[str]
    ):  # type: (...) -> typing.Optional[typing.Tuple[typing.Optional[str], typing.Optional[str]]]
        """
        See https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#event-autodoc-process-signature

        [SPHINX_AUTODOC_EVENTS]:
            autodoc-process-signature(app, what, name, obj, options, signature, return_annotation)

            Emitted when autodoc has formatted a signature for an object.

        :param app:
            [SPHINX_AUTODOC_EVENTS]:
                The Sphinx application object
        :param what:
            [SPHINX_AUTODOC_EVENTS]:
                The type of the object which the docstring belongs to
                (one of "module", "class", "exception", "function", "method", "attribute")

            .. note:: Actually is the type of the current object, [sphinx#6808](https://github.com/sphinx-doc/sphinx/issues/6808) not applicable here.
        :param fq_name:
            ``name`` in [SPHINX_AUTODOC_EVENTS].

            [SPHINX_AUTODOC_EVENTS]:
                The fully qualified name of the object

            .. note:: Actually is the fully qualified name, [sphinx#6808](https://github.com/sphinx-doc/sphinx/issues/6808) not applicable here.
        :param obj:
            [SPHINX_AUTODOC_EVENTS]:
                The object itself

            .. warning:: May be None, especially for attributes.
        :param options:
            [SPHINX_AUTODOC_EVENTS]:
                The options given to the directive:
                an object with attributes inherited_members, undoc_members, show_inheritance and noindex
                that are true if the flag option of same name was given to the auto directive
        :param signature:
            [SPHINX_AUTODOC_EVENTS]:
                Function signature, as a string of the form "(parameter_1, parameter_2)",
                or None if introspection didn't succeed and signature wasn't specified in the directive.
        :param return_annotation:
            [SPHINX_AUTODOC_EVENTS]:
                Function return annotation as a string of the form " -> annotation",
                or None if there is no return annotation.
        :return:
            [SPHINX_AUTODOC_EVENTS]:
                The event handler can return a new tuple (signature, return_annotation)
                to change what Sphinx puts into the output.
        """
        from ._logging import Logger
        from ._typehints import checkredundantoptionaltypes

        _logger = Logger.getinstance(Logger.Id.AUTODOC_PROCESS_SIGNATURE)  # type: Logger
        _logger.debug("AutodocHandlers.processsignature(what=%r, fq_name=%r, obj=%r, signature=%r, return_annotation=%r, options=%r)",
                      what, fq_name, obj, signature, return_annotation, options)

        # Useful local functions.
        def _errmsg(message):  # type: (str) -> str
            return f"autodoc-process-signature(fq_name={fq_name!r}): {message}"

        if what == "class":
            # Do not show `__init__()` arguments in the class signature.
            # `__init__()` documentation is generated separately.
            _logger.debug("Class %s signature set from %r to None", fq_name, signature)
            return None, None

        if signature and ("#" in signature):
            # As of sphinx@4.4.0, additional trailing comments after `# type: ...` comments are not automatically removed.
            # Let's remove them below.
            _logger.debug("Removing comments from signature %r", signature)

            # Split the comma-separated argument list.
            assert signature.startswith("(") and signature.endswith(")")
            _args = signature[1:-1].split(", ")  # type: typing.List[str]

            # Restore commas which were not to separate arguments.
            _index = 0  # type: int
            while _index < len(_args):
                # Check whether the argument line actually starts with a typed argument name.
                if re.search(r"^\w+: ", _args[_index]):
                    _logger.debug("  => arg#%d %r", _index + 1, _args[_index])
                    _index += 1
                else:
                    assert _index > 0, _errmsg(f"Unexpected {_args[_index]!r} at the beginning of signature {signature!r}")
                    _logger.debug("     Merging %r + %r", _args[_index - 1], _args[_index])
                    _args[_index - 1] += f", {_args[_index]}"  # Don't forget to restore the comma.
                    del _args[_index]

            # Remove comments.
            for _index in range(len(_args)):  # Type already declared above.
                if "#" in _args[_index]:
                    _logger.debug("  => Removing comment from arg#%d %r", _index + 1, _args[_index])
                    _match = (
                        # First try to match with a default value pattern at the end of the line.
                        re.match(r"^([^#]+)( *#.*)( = \w+)$", _args[_index])
                        # Otherwise match with no default value.
                        # The empty group in the end is left intentionally for grouping compatibility between the two regex.
                        or re.match(r"^([^#]+)( *#.*)()$", _args[_index])  # Empty group assumed.
                    )  # type: typing.Optional[typing.Match[str]]
                    assert _match, _errmsg(f"Could not parse comment from {_args[_index]!r}")
                    _args[_index] = _match.group(1).rstrip() + _match.group(3)
                    _logger.debug("     %r", _args[_index])

            # Rebuild the signature.
            signature = f"({', '.join(_args)})"

        # Fix redundant optional types.
        if signature:
            signature = checkredundantoptionaltypes(signature)
        if return_annotation:
            return_annotation = checkredundantoptionaltypes(return_annotation)

        _logger.debug("Final signature: %r -> %r", signature, return_annotation)
        return signature, return_annotation

    def processdocstring(
            self,
            app,  # type: sphinx.application.Sphinx
            what,  # type: str
            fq_name,  # type: str
            obj,  # type: typing.Optional[typing.Any]
            options,  # type: typing.Any
            lines,  # type: typing.List[str]
    ):  # type: (...) -> None
        """
        See https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#event-autodoc-process-docstring

        [SPHINX_AUTODOC_EVENTS]:
            autodoc-process-docstring(app, what, name, obj, options, lines)

            Emitted when autodoc has read and processed a docstring. lines is a list of strings – the lines of the processed docstring –
            that the event handler can modify in place to change what Sphinx puts into the output.

        :param app:
            [SPHINX_AUTODOC_EVENTS]:
                The Sphinx application object
        :param what:
            [SPHINX_AUTODOC_EVENTS]:
                The type of the object which the docstring belongs to
                (one of "module", "class", "exception", "function", "method", "attribute")

            .. note:: Actually is the type of the current object, [sphinx#6808](https://github.com/sphinx-doc/sphinx/issues/6808) not applicable here.
        :param fq_name:
            ``name`` in [SPHINX_AUTODOC_EVENTS].

            [SPHINX_AUTODOC_EVENTS]:
                The fully qualified name of the object

            .. note:: Actually is the fully qualified name, [sphinx#6808](https://github.com/sphinx-doc/sphinx/issues/6808) not applicable here.
        :param obj:
            [SPHINX_AUTODOC_EVENTS]:
                The object itself

            .. warning:: May be None, especially for attributes.
        :param options:
            [SPHINX_AUTODOC_EVENTS]:
                The options given to the directive:
                an object with attributes inherited_members, undoc_members, show_inheritance and noindex
                that are true if the flag option of same name was given to the auto directive"
        :param lines:
            [SPHINX_AUTODOC_EVENTS]:
                The lines of the docstring, see above

        Ensures Python items are documented.
        If not, prints a warning in the console and generates a warning in the output documentation.
        """
        from ._documenteditems import savedocumenteditem, trackmoduleitems
        from ._logging import Logger
        from ._reflection import isspecialfunction

        _logger = Logger.getinstance(Logger.Id.AUTODOC_PROCESS_DOCSTRING)  # type: Logger
        _logger.debug("AutodocHandlers.processdocstring(what=%r, fq_name=%r, obj=%r, lines=%r, options=%r)",
                      what, fq_name, obj, lines, options)

        # Check whether the item is documented.
        # Inspired from: https://stackoverflow.com/questions/14141170/how-can-i-just-list-undocumented-members-with-sphinx-autodoc
        # By default, check the docstring in `lines` (which may come from the upper classes) is not empty.
        _is_documented = (len(lines) > 0)  # type: bool
        if (obj is not None) and isspecialfunction(obj):
            # Do not check the `lines` parameters for special functions,
            # in as much as sphinx-build automatically fills this parameter with what is inherited from the base builtin types (usually `object`).
            _is_documented = (obj.__doc__ is not None)
        elif (obj is not None) and isinstance(obj, enum.EnumMeta):
            # Do not check the `lines` parameters for enums,
            # in as much as `sphinx-build` automatically fills this parameter with the defaut :class:`enum.Enum`'s docstring.
            _is_documented = (lines != ["An enumeration.", ""])
        if _is_documented:
            savedocumenteditem(fq_name, what, obj, lines)
        else:
            # If not:
            # - Display a warning in the console during the build.
            _logger.warning(f"Undocumented {what} `{fq_name}`")
            # # - Display a warning in the output documentation.
            # lines.append(f".. warning:: Undocumented {what} ``{fq_name}``.")

        # Identify the items to track when applicable.
        if inspect.ismodule(obj):
            trackmoduleitems(obj)
