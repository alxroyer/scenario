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
import typing

# Sphinx imports.
import docutils.nodes
import docutils.parsers.rst.states
import sphinx.application
import sphinx.domains.python
import sphinx.ext.autodoc
import sphinx.ext.autodoc.importer
import sphinx.pycode
import sphinx.util.inspect
import sphinx.util.typing


class SphinxHacking:

    _get_class_members_origin = sphinx.ext.autodoc.importer.get_class_members
    _make_xrefs_origin = sphinx.domains.python.PyXrefMixin.make_xrefs
    _parse_reftarget_origin = sphinx.domains.python.parse_reftarget
    _object_description_origin = sphinx.ext.autodoc.object_description

    def setup(
            self,
            app,  # type: sphinx.application.Sphinx
    ):  # type: (...) -> None
        # Hack `sphinx.ext.autodoc.ClassDocumenter.format_args()`.
        # Use `setattr()` to avoid a "Cannot assign to a method [assignment]" typing error.
        setattr(sphinx.ext.autodoc.ClassDocumenter, "_get_signature", SphinxHacking._classdocumentergetsignature)
        # Hack `sphinx.ext.autodoc.importer.get_class_members()`
        # both in `sphinx.ext.autodoc.importer` and `sphinx.ext.autodoc` (function imported at the module level).
        sphinx.ext.autodoc.importer.get_class_members = SphinxHacking._getclassmembers
        sphinx.ext.autodoc.get_class_members = SphinxHacking._getclassmembers
        # Hack `sphinx.domains.python.PyXrefMixin.make_xrefs()`.
        # Use `setattr()` to avoid a "Cannot assign to a method [assignment]" typing error.
        setattr(sphinx.domains.python.PyXrefMixin, "make_xrefs", SphinxHacking._makexrefs)
        # Hack `sphinx.domains.python.parse_reftarget()`.
        sphinx.domains.python.parse_reftarget = SphinxHacking._parsereftarget
        # Hack `sphinx.ext.autodoc.object_description()`.
        sphinx.ext.autodoc.object_description = SphinxHacking._objectdescription

    @staticmethod
    def _classdocumentergetsignature(
            self,  # type: sphinx.ext.autodoc.ClassDocumenter
            **kwargs  # type: typing.Any
    ):  # type: (...) -> typing.Tuple[typing.Optional[typing.Any], typing.Optional[str], typing.Optional[inspect.Signature]]
        """
        Replacement hack for ``sphinx.ext.autodoc.ClassDocumenter._get_signature()``.

        Avoids documenting ``__init__()`` signatures in class documentations when ``autodoc_typehints`` is ``'description'``.
        """
        from ._logging import Logger

        _logger = Logger(Logger.Id.CLASS_DOCUMENTER_FORMAT_ARGS)  # type: Logger
        _logger.debug("SphinxHacking._classdocumentergetsignature(): self.object=%r => returning (None, None, None)", self.object)

        return None, None, None

    @staticmethod
    def _getclassmembers(
            subject,  # type: typing.Any
            objpath,  # type: typing.List[str]
            attrgetter,  # type: typing.Callable[..., typing.Any]
            inherit_docstrings=True,  # type: bool
    ):  # type: (...) -> typing.Dict[str, sphinx.ext.autodoc.ObjectMember]
        """
        Replacement hack for ``sphinx.ext.autodoc.importer.get_class_members()``.

        Workarounds for ``sphinx.ext.autodoc.importer.get_class_members()`` bugs:

        - `sphinx#11353 <https://github.com/sphinx-doc/sphinx/issues/11353>`_
        - `sphinx#11387 <https://github.com/sphinx-doc/sphinx/issues/11387>`_
        """
        from scenario._debugutils import SafeRepr  # noqa  ## Access to a protected member.
        from scenario._reflection import fqname  # noqa  ## Access to a protected member.
        from ._logging import Logger

        _logger = Logger(Logger.Id.GET_CLASS_MEMBERS)  # type: Logger
        _logger.debug("SphinxHacking._getclassmembers(subject=%r, objpath=%r, attrgetter=%r, inherit_docstrings=%r)",
                      subject, objpath, attrgetter, inherit_docstrings)

        # Call the base `sphinx.ext.autodoc.importer.get_class_members()` at first.
        _kwargs = {}  # type: typing.Dict[str, typing.Any]
        if sphinx.version_info >= (5, 0):
            _kwargs["inherit_docstrings"] = inherit_docstrings
        _members = SphinxHacking._get_class_members_origin(
            subject, objpath, attrgetter,
            **_kwargs,
        )  # type: typing.Dict[str, sphinx.ext.autodoc.ObjectMember]
        _logger.debug("_members = %s", SafeRepr(_members))

        # [sphinx#11353](https://github.com/sphinx-doc/sphinx/issues/11353)
        #
        # When analyzing an enum class that does not just inherit from `enum.Enum` or a derivate,
        # `superclass = subject.__mro__[1]` does not necessarily retrieve the `enum.Enum` super-class.
        # In the case of `StrEnum`, it retrieves `str` for instance.
        def _fixenumclassmembers():  # type: (...) -> None
            # Checking identification of the `enum.Enum` super-class:
            # - as computed in in `sphinx.ext.autodoc.importer.get_class_members()`:
            _possibly_wrong_enum_superclass = subject.__mro__[1]  # type: type
            _logger.debug("_possibly_wrong_enum_superclass = %r", _possibly_wrong_enum_superclass)
            # - as it had better be computed:
            _enum_superclass = list(filter(sphinx.util.inspect.isenumclass, subject.__mro__))[-1]  # type: type
            _logger.debug("_enum_superclass = %r", _enum_superclass)

            if _possibly_wrong_enum_superclass is _enum_superclass:
                _logger.debug("No need to fix members for %r", subject)
            else:
                _logger.debug("[sphinx#11353] Fixing %s enum members", fqname(subject))
                _logger.debug("_members (before) = %r", _members)

                # Call `attrgetter()` as done in `sphinx.ext.autodoc.importer.get_class_members()`.
                _obj_dict = attrgetter(subject, '__dict__', {})  # type: typing.Mapping[str, typing.Any]
                _logger.debug("_obj_dict = %r", _obj_dict)

                # Scan the `_obj_dict` `attrgetter()` result as done in `sphinx.ext.autodoc.importer.get_class_members()`.
                for _obj_name in _obj_dict:  # type: str
                    _obj = _obj_dict[_obj_name]  # type: typing.Any
                    _obj_desc = sphinx.ext.autodoc.ObjectMember(_obj_name, _obj, class_=subject)  # type: sphinx.ext.autodoc.ObjectMember

                    # Determine whether the object should be kept in the member list.
                    _save_member = True  # type: bool
                    if _obj_name == "_member_type_":
                        _logger.debug("'_member_type_' explicitly filtered-out")
                        _save_member = False
                    elif hasattr(_enum_superclass, _obj_name) and (_obj.__doc__ == getattr(_enum_superclass, _obj_name).__doc__):
                        _logger.debug("%r inherited from %r", _obj_name, _enum_superclass)
                        _save_member = False

                    # Depending on the decision above, restore, remove, or keep as is the member.
                    if _save_member:
                        if _obj_name in _members:
                            _logger.debug("Keeping %r in members", _obj_desc)
                        else:
                            _logger.debug("Restoring %r into members", _obj_desc)
                            _members[_obj_name] = _obj_desc
                    else:
                        if _obj_name in _members:
                            _logger.debug("Removing %r from members", _obj_desc)
                            del _members[_obj_name]
                        else:
                            _logger.debug("Keep avoiding %r from members", _obj_desc)

                _logger.debug("_members (modified) = %r", _members)
        if sphinx.util.inspect.isenumclass(subject):
            _fixenumclassmembers()

        # [sphinx#11387](https://github.com/sphinx-doc/sphinx/issues/11387)
        #
        # Things are messed up for inherited members when using annotations.
        def _fixobjectmembersdefclass():  # type: (...) -> None
            for _mro_class in sphinx.util.inspect.getmro(subject):  # type: type
                # Don't proceed with builtin superclasses.
                if _mro_class.__module__ == "builtins":
                    continue

                # Inspired from `sphinx.ext.autodoc.importer.get_class_members()`.
                _analyzer = sphinx.pycode.ModuleAnalyzer.for_module(_mro_class.__module__)  # type: sphinx.pycode.ModuleAnalyzer
                _analyzer.analyze()
                for (_ns, _name), _docstring in _analyzer.attr_docs.items():  # type: typing.Tuple[str, str], typing.List[str]
                    if (
                        # Is the attribute name of those described in `_members`?
                        (_name in _members)
                        # Is the given attribute actually part of `_mro_class`?
                        and (_ns == _mro_class.__name__)
                        # Is it the same docstring? If not, the attribute may have been redefined, with a different documentation normally.
                        and (_members[_name].docstring == "\n".join(_docstring))
                        # Is it really new information? If not, no need to log anything.
                        and (_members[_name].class_ is not _mro_class)
                    ):
                        _logger.debug("[sphinx#11387] Fixing definition class for %s.%s from %s to %s",
                                      fqname(subject), _name, fqname(_members[_name].class_), fqname(_mro_class))
                        _members[_name].class_ = _mro_class
        _fixobjectmembersdefclass()

        return _members

    @staticmethod
    def _makexrefs(
            self,  # type: sphinx.domains.python.PyXrefMixin
            rolename,  # type: str
            domain,  # type: str
            target,  # type: str
            innernode=docutils.nodes.emphasis,  # type: typing.Type[sphinx.util.typing.TextlikeNode]
            contnode=None,  # type: docutils.nodes.Node
            env=None,  # type: sphinx.application.BuildEnvironment
            inliner=None,  # type: docutils.parsers.rst.states.Inliner
            location=None,  # type: docutils.nodes.Node
    ):  # type: (...) -> typing.List[docutils.nodes.Node]
        """
        Replacement hack for ``sphinx.domains.python.PyXrefMixin.make_xrefs()``.

        Fixes redundant optional types in parameter typehints,
        when ``autodoc_typehints`` is set to ``description`` or ``both``.

        Calls :func:`._typehints.checkredundantoptionaltypes()`
        prior to calling the actual ``sphinx.domains.python.PyXrefMixin.make_xrefs()`` implementation.

        .. note::
            In order to serve this goal, we could have tried to hacking the call stack earlier in ``sphinx.util.docfields``.
            But it seemed a bit more tricky in the end.
            Hacking the single ``make_xrefs()`` implementation in ``sphinx.domains.python`` ensures the job will be done for the python domain.
        """
        from ._logging import Logger
        from ._typehints import checkredundantoptionaltypes

        _logger = Logger(Logger.Id.MAKE_XREFS_HACK)  # type: Logger
        _logger.debug("SphinxHacking._makexrefs(self=%r, rolename=%r, domain=%r, target=%r, innernode=%r, contnode=%r, env=%r, inliner=%r, location=%r)",
                      self, rolename, domain, target, innernode, contnode, env, inliner, location)

        _short_target = checkredundantoptionaltypes(target)  # type: str
        if _short_target != target:
            _logger.debug("%r fixed into %r", target, _short_target)
            target = _short_target

        return SphinxHacking._make_xrefs_origin(
            self,
            rolename=rolename,
            domain=domain,
            target=target,
            innernode=innernode,
            contnode=contnode,
            env=env,
            inliner=inliner,
            location=location,
        )

    @staticmethod
    def _parsereftarget(
            reftarget,  # type: str
            suppress_prefix=False,  # type: bool
    ):  # type: (...) -> typing.Tuple[str, str, str, bool]
        """
        Replacement hack for ``sphinx.domains.python.parse_reftarget()``.

        Fixes non-working cross-references for types.

        We could have hacked ``sphinx.domains.python.type_to_xref()`` for the purpose:
        ensure a ``pending_xref`` instance has ``'data'`` for its ``reftype`` attribute,
        instead of ``'class'`` badly set by `sphinx.domains.python.parse_reftarget()`.

        It's eventually easier to hack ``sphinx.domains.python.parse_reftarget()`` directly:
        make it return a ``'data'`` `reftype` instead of ``'class'`` for our `scenario` types.
        """
        from ._logging import Logger
        from ._typehints import SCENARIO_TYPES

        _logger = Logger(Logger.Id.PARSE_REFTARGET_HACK)  # type: Logger
        _logger.debug("SphinxHacking._parsereftarget(reftarget=%r, suppress_prefix=%r)", reftarget, suppress_prefix)

        _reftype, _reftarget, _title, _refspecific = SphinxHacking._parse_reftarget_origin(
            reftarget,
            suppress_prefix=suppress_prefix,
        )  # type: str, str, str, bool
        if _reftarget in SCENARIO_TYPES:
            _logger.debug("Fixing type for %r from %r to %r", _reftarget, _reftype, "data")
            _reftype = "data"

        return _reftype, _reftarget, _title, _refspecific

    @staticmethod
    def _objectdescription(
            object,  # type: typing.Any  # noqa  ## Shadows built-in name 'object'
    ):  # type: (...) -> str
        """
        Replacement hack for ``sphinx.ext.autodoc.object_description()``.

        Called for data/attribute value description.

        :param object: Caution! may be ``None``.
        :raise ValueError: When ``object`` should not be described, i.e. not a basic type in this implementation.

        .. note::
            The signature follows strictly the one of ``sphinx.util.inspect.object_description()``
            in order to avoid typing errors when setting this method as a replacement for ``sphinx.ext.autodoc.object_description()``.
            The name of the  parameter ``object`` must remain as is (not ``obj``)!

        .. note::
            For the memo: it seems we have no way to differenciate class and instance attributes when the value is ``None``
            (see `sphinx#904 <https://github.com/sphinx-doc/sphinx/issues/904>`_).
        """
        from ._logging import Logger

        _logger = Logger.getinstance(Logger.Id.OBJECT_DESCRIPTION_HACK)  # type: Logger
        _logger.debug("SphinxHacking._objectdescription(object=%r)", object)

        # Retrieve the result from the original function at first.
        _object_description = SphinxHacking._object_description_origin(object)  # type: str

        # Display data/attribute description for non-empty basic types only.
        if (
            isinstance(object, (int, float))
            or (isinstance(object, (str, bytes)) and object)
        ):
            _logger.debug("Returning %r", _object_description)
            return _object_description

        # Discard the description for `None` or any other kind of object.
        _err = ValueError(f"Object description {_object_description!r} for data/attribute discarded")
        _logger.debug("[sphinx#904] Discarding %r (%r raised)", _object_description, _err)
        raise _err
