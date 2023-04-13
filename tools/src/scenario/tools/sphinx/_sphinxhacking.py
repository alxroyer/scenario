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
import docutils.parsers.rst.states
import sphinx.application
import sphinx.domains.python
import sphinx.ext.autodoc
import sphinx.util.typing
import typing


class SphinxHacking:

    _make_xrefs_origin = sphinx.domains.python.PyXrefMixin.make_xrefs
    _parse_reftarget_origin = sphinx.domains.python.parse_reftarget
    _object_description_origin = sphinx.ext.autodoc.object_description

    def setup(
            self,
            app,  # type: sphinx.application.Sphinx
    ):  # type: (...) -> None
        # Hack `sphinx.domains.python.PyXrefMixin.make_xrefs()` to fix redundant optional types.
        # Use `setattr()` to avoid a "Cannot assign to a method [assignment]" typing error.
        setattr(sphinx.domains.python.PyXrefMixin, "make_xrefs", SphinxHacking._makexrefs)
        # Hack `sphinx.domains.python.parse_reftarget()` to fix `scenario` type cross-references.
        sphinx.domains.python.parse_reftarget = SphinxHacking._parsereftarget
        # Hack `sphinx.ext.autodoc.object_description()` (see [sphinx#904](https://github.com/sphinx-doc/sphinx/issues/904)).
        sphinx.ext.autodoc.object_description = SphinxHacking._objectdescription

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

        :param object: Caution! may be ``None``.
        :raise ValueError:
            When ``object`` is ``None``,
            so that *autodoc* does not print out erroneous attribute values,
            especially for instance attribute.

        .. note::
            The signature follows strictly the one of ``sphinx.util.inspect.object_description()``
            in order to avoid typing errors when setting this method as a replacement for ``sphinx.ext.autodoc.object_description()``.
            The name of the  parameter ``object`` must remain as is (not ``obj``)!

        .. warning::
            Unfortunately, it seems we have no way to differenciate class and instance attributes when the value is ``None``
            (see `sphinx#904 <https://github.com/sphinx-doc/sphinx/issues/904>`_).
        """
        from ._logging import Logger

        _logger = Logger.getinstance(Logger.Id.OBJECT_DESCRIPTION_HACK)  # type: Logger
        _logger.debug("SphinxHacking._objectdescription(object=%r)", object)

        if object is None:
            raise ValueError("No value for data/attributes")
        return SphinxHacking._object_description_origin(object)
