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

import sphinx.application
import sphinx.domains.python
import sphinx.ext.autodoc
import typing


class SphinxHacking:

    _parse_reftarget_origin = sphinx.domains.python.parse_reftarget
    _object_description_origin = sphinx.ext.autodoc.object_description

    def setup(
            self,
            app,  # type: sphinx.application.Sphinx
    ):  # type: (...) -> None
        # Hack `sphinx.domains.python.parse_reftarget()` to fix `scenario` type cross-references.
        sphinx.domains.python.parse_reftarget = self._parsereftarget
        # Hack `sphinx.ext.autodoc.object_description()` (see [sphinx#904](https://github.com/sphinx-doc/sphinx/issues/904)).
        sphinx.ext.autodoc.object_description = self._objectdescription

    def _parsereftarget(
            self,
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

    def _objectdescription(
            self,
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
