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
import inspect
import sphinx.addnodes
import sphinx.application
import sphinx.domains.python
import sphinx.events
import sphinx.ext.autodoc
import sphinx.ext.autodoc.type_comment
import sphinx.ext.autodoc.typehints
# import sphinx.pycode.ast
import sphinx.util.docfields
import sphinx.util.inspect
import sphinx.util.typing
import typing


class SphinxHacking:

    _update_annotations_using_type_comments_origin = sphinx.ext.autodoc.type_comment.update_annotations_using_type_comments
    _get_type_comment_origin = sphinx.ext.autodoc.type_comment.get_type_comment
    _inspect_signature_origin = sphinx.util.inspect.signature
    _filter_meta_fields_origin = sphinx.domains.python.filter_meta_fields
    _merge_typehints_origin = sphinx.ext.autodoc.typehints.merge_typehints
    _docfieldtransformer_transform_origin = sphinx.util.docfields.DocFieldTransformer.transform
    _make_xrefs_origin = sphinx.domains.python.PyXrefMixin.make_xrefs
    _parse_reftarget_origin = sphinx.domains.python.parse_reftarget
    _object_description_origin = sphinx.ext.autodoc.object_description

    def setup(
            self,
            app,  # type: sphinx.application.Sphinx
    ):  # type: (...) -> None
        sphinx.ext.autodoc.type_comment.update_annotations_using_type_comments = SphinxHacking._updateannotationsusingtypecomments
        sphinx.ext.autodoc.type_comment.get_type_comment = SphinxHacking._gettypecomment
        sphinx.util.inspect.signature = SphinxHacking._inspectsignature
        sphinx.domains.python.filter_meta_fields = SphinxHacking._filtermetafields
        sphinx.ext.autodoc.typehints.merge_typehints = SphinxHacking._mergetypehints
        # Use `setattr()` to avoid a "Cannot assign to a method [assignment]" typing error.
        setattr(sphinx.util.docfields.DocFieldTransformer, "transform", SphinxHacking._docfieldtransformertransform)
        # Hack `sphinx.domains.python.PyXrefMixin.make_xrefs()` to fix redundant optional types.
        # Use `setattr()` to avoid a "Cannot assign to a method [assignment]" typing error.
        setattr(sphinx.domains.python.PyXrefMixin, "make_xrefs", SphinxHacking._makexrefs)
        # Hack `sphinx.domains.python.parse_reftarget()` to fix `scenario` type cross-references.
        sphinx.domains.python.parse_reftarget = SphinxHacking._parsereftarget
        # Hack `sphinx.ext.autodoc.object_description()` (see [sphinx#904](https://github.com/sphinx-doc/sphinx/issues/904)).
        sphinx.ext.autodoc.object_description = SphinxHacking._objectdescription

        # Fix event handlers already configured.
        for _event_name in ("autodoc-before-process-signature", "object-description-transform"):  # type: str
            for _event_listener_index, _event_listener in enumerate(app.events.listeners[_event_name]):  # type: int, sphinx.events.EventListener
                for _handler_origin, _handler_hack in [
                    (SphinxHacking._update_annotations_using_type_comments_origin, SphinxHacking._updateannotationsusingtypecomments),
                    (SphinxHacking._filter_meta_fields_origin, SphinxHacking._filtermetafields),
                    (SphinxHacking._merge_typehints_origin, SphinxHacking._mergetypehints),
                ]:
                    if _event_listener.handler is _handler_origin:
                        app.events.listeners[_event_name][_event_listener_index] = sphinx.events.EventListener(
                            _event_listener.id,
                            _handler_hack,
                            _event_listener.priority,
                        )

    @staticmethod
    def _updateannotationsusingtypecomments(
            app: sphinx.application.Sphinx,
            obj: typing.Any,
            bound_method: bool,
    ):  # type: (...) -> None
        def _print(message):  # type: (str) -> None
            if "assertequal" in repr(obj):
                print(message)
        _print(f"SphinxHacking._updateannotationsusingtypecomments(obj={obj!r}, bound_method={bound_method!r})")

        _print(f"SphinxHacking._updateannotationsusingtypecomments(): (before) "
               f"obj.__annotations__={obj.__annotations__ if hasattr(obj, '__annotations__') else '(none)'!r}")

        # SphinxHacking._update_annotations_using_type_comments_origin(app, obj, bound_method)

        try:
            type_sig = sphinx.ext.autodoc.type_comment.get_type_comment(obj, bound_method)
            _print(f"SphinxHacking._updateannotationsusingtypecomments(): type_sig={type_sig!r}")
            if type_sig:  # type: ignore[truthy-bool]
                sig = sphinx.util.inspect.signature(obj, bound_method)
                _print(f"SphinxHacking._updateannotationsusingtypecomments(): sig={sig!r}")
                for param in sig.parameters.values():
                    _print(f"SphinxHacking._updateannotationsusingtypecomments(): param={param!r}")
                    if param.name not in obj.__annotations__:
                        annotation = type_sig.parameters[param.name].annotation
                        if annotation is not inspect.Parameter.empty:
                            obj.__annotations__[param.name] = sphinx.pycode.ast.unparse(annotation)

                if 'return' not in obj.__annotations__:
                    obj.__annotations__['return'] = type_sig.return_annotation
        except KeyError as exc:
            sphinx.ext.autodoc.type_comment.logger.warning(
                sphinx.ext.autodoc.type_comment.__("Failed to update signature for %r: parameter not found: %s"),
                obj, exc,
            )
        except NotImplementedError as exc:  # failed to ast.unparse()
            sphinx.ext.autodoc.type_comment.logger.warning(
                sphinx.ext.autodoc.type_comment.__("Failed to parse type_comment for %r: %s"),
                obj, exc,
            )

        _print(f"SphinxHacking._updateannotationsusingtypecomments(): (after) "
               f"obj.__annotations__={obj.__annotations__ if hasattr(obj, '__annotations__') else '(none)'!r}")

    @staticmethod
    def _gettypecomment(
            obj,  # type: typing.Any
            bound_method=False,  # type: bool
    ):  # type: (...) -> inspect.Signature
        def _print(message):  # type: (str) -> None
            if "assertequal" in repr(obj):
                print(message)
        _print(f"SphinxHacking._gettypecomment(obj={obj!r}, bound_method={bound_method!r})")

        _res = SphinxHacking._get_type_comment_origin(obj, bound_method=bound_method)

        _print(f"SphinxHacking._gettypecomment() -> {_res!r}")
        return _res

    @staticmethod
    def _inspectsignature(
            subject,  # type: typing.Callable[..., typing.Any]
            bound_method = False,  # type: bool
            type_aliases={},  # type: typing.Dict[str, typing.Any]
    ):  # type: (...) -> inspect.Signature
        def _print(message):  # type: (str) -> None
            if "assertequal" in repr(subject):
                print(message)
        _print(f"_inspectsignature(subject={subject!r}, bound_method={bound_method!r}, type_aliases={type_aliases!r})")

        # _res = SphinxHacking._inspect_signature_origin(subject, bound_method=bound_method, type_aliases=type_aliases)

        try:
            try:
                _print(f"_inspectsignature(): sphinx.util.inspect._should_unwrap(subject)={sphinx.util.inspect._should_unwrap(subject)!r}")
                if sphinx.util.inspect._should_unwrap(subject):
                    signature = inspect.signature(subject)
                else:
                    signature = inspect.signature(subject, follow_wrapped=True)
            except ValueError as _err:
                _print(f"_inspectsignature(): {_err!r}")
                _print(f"_inspectsignature(): Using standard `inspect.signature()`")
                # follow built-in wrappers up (ex. functools.lru_cache)
                signature = inspect.signature(subject)
            parameters = list(signature.parameters.values())
            return_annotation = signature.return_annotation
        except IndexError as _err:
            _print(f"_inspectsignature(): {_err!r}")
            # Until python 3.6.4, cpython has been crashed on inspection for
            # partialmethods not having any arguments.
            # https://bugs.python.org/issue33009
            if hasattr(subject, '_partialmethod'):
                _print(f"_inspectsignature(): But subject={subject!r} has '_partialmethod' attribute")
                parameters = []
                return_annotation = inspect.Parameter.empty
            else:
                raise
        _print(f"_inspectsignature(): parameters={parameters!r}")
        _print(f"_inspectsignature(): return_annotation={return_annotation!r}")

        try:
            # Resolve annotations using ``get_type_hints()`` and type_aliases.
            localns = sphinx.util.inspect.TypeAliasNamespace(type_aliases)
            _print(f"_inspectsignature(): localns={localns!r}")
            annotations = typing.get_type_hints(subject, None, localns)
            _print(f"_inspectsignature(): annotations={annotations!r}")
            for i, param in enumerate(parameters):
                if param.name in annotations:
                    annotation = annotations[param.name]
                    _print(f"_inspectsignature(): annotation={annotation!r}")
                    if isinstance(annotation, sphinx.util.inspect.TypeAliasForwardRef):
                        annotation = annotation.name
                    parameters[i] = param.replace(annotation=annotation)
            if 'return' in annotations:
                _print(f"_inspectsignature(): annotations['return']={annotations['return']!r}")
                if isinstance(annotations['return'], sphinx.util.inspect.TypeAliasForwardRef):
                    return_annotation = annotations['return'].name
                else:
                    return_annotation = annotations['return']
        except Exception as _err:
            _print(f"_inspectsignature(): {_err!r}")
            _print(f"_inspectsignature(): passed...")
            # ``get_type_hints()`` does not support some kind of objects like partial,
            # ForwardRef and so on.
            pass

        if bound_method:
            if inspect.ismethod(subject):
                # ``inspect.signature()`` considers the subject is a bound method and removes
                # first argument from signature.  Therefore no skips are needed here.
                pass
            else:
                if len(parameters) > 0:
                    parameters.pop(0)

        # To allow to create signature object correctly for pure python functions,
        # pass an internal parameter __validate_parameters__=False to Signature
        #
        # For example, this helps a function having a default value `inspect._empty`.
        # refs: https://github.com/sphinx-doc/sphinx/issues/7935
        _print(f"_inspectsignature(): Creating inspect.Signature(parameters={parameters!r}, return_annotation={return_annotation!r})")
        _res = inspect.Signature(parameters, return_annotation=return_annotation,
                                 __validate_parameters__=False)

        if "assertequal" in repr(subject):
            print(f"_inspectsignature() -> {_res!r}")
        return _res

    @staticmethod
    def _filtermetafields(
            app,  # type: sphinx.application.Sphinx
            domain,  # type: str
            objtype,  # type: str
            content,  # type: docutils.nodes.Element
    ):  # type: (...) -> None
        print(f"_filtermetafields(domain={domain!r}, objtype={objtype!r}, content={content.astext()!r})")
        SphinxHacking._filter_meta_fields_origin(app, domain, objtype, content)
        print(f"_filtermetafields() -> content={content.astext()!r}")

    @staticmethod
    def _mergetypehints(
            app,  # type: sphinx.application.Sphinx
            domain,  # type: str
            objtype,  # type: str
            contentnode,  # type: docutils.nodes.Element
    ):  # type: (...) -> None
        print(f"_mergetypehints(domain={domain!r}, objtype={objtype!r}, content={contentnode.astext()!r})")

        # SphinxHacking._merge_typehints_origin(app, domain, objtype, contentnode)

        if domain != 'py':
            return
        if app.config.autodoc_typehints not in ('both', 'description'):
            print(f"_mergetypehints(): app.config.autodoc_typehints={app.config.autodoc_typehints!r}")
            return

        try:
            signature = typing.cast(sphinx.addnodes.desc_signature, contentnode.parent[0])
            if signature['module']:
                fullname = '.'.join([signature['module'], signature['fullname']])
            else:
                fullname = signature['fullname']
        except KeyError as _err:
            # signature node does not have valid context info for the target object
            print(f"_mergetypehints(): {_err!r}")
            return

        annotations = app.env.temp_data.get('annotations', {})
        print(f"_mergetypehints(): annotations={annotations!r}")
        if annotations.get(fullname, {}):
            field_lists = [n for n in contentnode if isinstance(n, docutils.nodes.field_list)]
            print(f"_mergetypehints(): field_lists={field_lists!r}")
            if field_lists == []:
                field_list = sphinx.ext.autodoc.typehints.insert_field_list(contentnode)
                field_lists.append(field_list)
                print(f"_mergetypehints(): field_lists={field_lists!r}")

            for field_list in field_lists:
                print(f"_mergetypehints(): field_list={field_list!r}")
                if app.config.autodoc_typehints_description_target == "all":
                    if objtype == 'class':
                        sphinx.ext.autodoc.typehints.modify_field_list(field_list, annotations[fullname], suppress_rtype=True)
                    else:
                        sphinx.ext.autodoc.typehints.modify_field_list(field_list, annotations[fullname])
                elif app.config.autodoc_typehints_description_target == "documented_params":
                    sphinx.ext.autodoc.typehints.augment_descriptions_with_types(
                        field_list, annotations[fullname], force_rtype=True
                    )
                else:
                    sphinx.ext.autodoc.typehints.augment_descriptions_with_types(
                        field_list, annotations[fullname], force_rtype=False
                    )
        else:
            print(f"_mergetypehints(): No fullname={fullname!r}")

        print(f"_mergetypehints() -> content={contentnode.astext()!r}")

    @staticmethod
    def _docfieldtransformertransform(
            self,  # type: sphinx.util.docfields.DocFieldTransformer
            node,  # type: docutils.nodes.field_list
    ):  # type: (...) -> None
        print(f"DocFieldTransformer.transform(node={node.astext()!r})")

        for field in typing.cast(typing.List[docutils.nodes.field], node):
            field_name = typing.cast(docutils.nodes.field_name, field[0])
            print(f"  DocFieldTransformer.transform(): field_name = {field_name.astext()!r}")

        SphinxHacking._docfieldtransformer_transform_origin(self, node)

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

        # Discard the description for any other kind of object (`None` among others).
        _err = ValueError(f"Object description {_object_description!r} for data/attribute discarded")
        _logger.debug("Discarding %r (%r raised)", _object_description, _err)
        raise _err
