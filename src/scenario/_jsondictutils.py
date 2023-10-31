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
JSON-like dictionary utils.

Applicable to YAML by the way.
"""

import abc
import json
import typing

if typing.TYPE_CHECKING:
    from ._path import AnyPathType as _AnyPathType


if typing.TYPE_CHECKING:
    #: JSON dictionary type.
    #:
    #: Applicable to YAML data as well.
    JsonDictType = typing.Dict[str, typing.Any]


class JsonDict(abc.ABC):

    JSON_SUFFIXES = (".json", )  # type: typing.Sequence[str]
    YAML_SUFFIXES = (".yml", ".yaml", )  # type: typing.Sequence[str]

    @staticmethod
    def assertjsondictinstance(
            obj,  # type: typing.Any
    ):  # type: (...) -> JsonDictType
        from ._debugutils import saferepr

        if isinstance(obj, dict) and all([isinstance(_key, str) for _key in obj]):
            return obj
        else:
            raise TypeError(f"{saferepr(obj)} not a JSON-like dictionary")

    @staticmethod
    def isjson(
            path,  # type: _AnyPathType
    ):  # type: (...) -> bool
        from ._path import Path

        return Path(path).suffix.lower() in JsonDict.JSON_SUFFIXES

    @staticmethod
    def isyaml(
            path,  # type: _AnyPathType
    ):  # type: (...) -> bool
        from ._path import Path

        return Path(path).suffix.lower() in JsonDict.YAML_SUFFIXES

    @staticmethod
    def isknwonsuffix(
            path,  # type: _AnyPathType
    ):  # type: (...) -> bool
        return any([
            JsonDict.isjson(path),
            JsonDict.isyaml(path),
        ])

    @staticmethod
    def readfile(
            input_path,  # type: _AnyPathType
            *,
            encoding=None,  # type: str
    ):  # type: (...) -> JsonDictType
        from ._debugutils import saferepr
        from ._path import Path
        from ._textfileutils import TextFile

        # Ensure `input_path` is a `Path` instance.
        if not isinstance(input_path, Path):
            input_path = Path(input_path)

        # Instantiate a `TextFile` object to read from the `input_path` file.
        _text_file = TextFile(input_path, "r", encoding=encoding)  # type: TextFile

        # Read the file with format depending on its extension.
        if input_path.suffix.lower() in JsonDict.JSON_SUFFIXES:
            # JSON format.

            _content = json.loads(_text_file.read())  # type: typing.Any

        elif input_path.suffix.lower() in JsonDict.YAML_SUFFIXES:
            # YAML format.

            # Import `yaml`: may raise an `EnvironmentError`.
            try:
                import yaml
            except ImportError as _err:
                raise EnvironmentError(_err)

            _content = yaml.safe_load(_text_file.read())  # Type already declared above.

        else:
            raise ValueError(f"Unknown extension {input_path.suffix!r}, can't read '{input_path}'")

        # Return the content read.
        try:
            return JsonDict.assertjsondictinstance(_content)
        except TypeError:
            raise ValueError(f"Bad content {saferepr(_content)}, '{input_path}' should contain a string dictionary")

    @staticmethod
    def writefile(
            content,  # type: JsonDictType
            output_path,  # type: _AnyPathType
            *,
            schema_subpath=None,  # type: str
            encoding=None,  # type: str
            indent=2,  # type: int
    ):  # type: (...) -> None
        from ._path import Path
        from ._pkginfo import PKG_INFO
        from ._textfileutils import TextFile

        # Ensure `output_path` is a `Path` instance.
        if not isinstance(output_path, Path):
            output_path = Path(output_path)
        # Ensure 'utf-8' by default.
        encoding = encoding or "utf-8"

        # Add meta information at the beginning of `content`.
        _content = {
            "$encoding": encoding,
        }  # type: JsonDictType
        if schema_subpath is not None:
            _content.update({
                "$schema": f"{PKG_INFO.repo_url}/blob/v{PKG_INFO.version}/{schema_subpath}",
                "$version": PKG_INFO.version,
            })
        _content.update(content)

        # Instantiate a `TextFile` object to write the `output_path` file.
        _text_file = TextFile(output_path, "w", encoding=encoding)  # type: TextFile

        # Write the file with format depending on its extension.
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if output_path.suffix.lower() in JsonDict.JSON_SUFFIXES:
            # JSON format.

            _text_file.write(json.dumps(_content, indent=indent))

        elif output_path.suffix.lower() in JsonDict.YAML_SUFFIXES:
            # YAML format.

            # Import `yaml`: may raise an `EnvironmentError`.
            try:
                import yaml
            except ImportError as _err:
                raise EnvironmentError(_err)

            # Let's specify encoding with a heading comment.
            _encoding_comment = f"# -*- coding: {_content['$encoding']} -*-"  # type: str
            del _content["$encoding"]

            _text_file.write(
                _encoding_comment + "\n"
                + "\n"
                + yaml.safe_dump(_content, indent=indent),
            )

        else:
            raise ValueError(f"Unknown extension {output_path.suffix!r}, can't write '{output_path}'")
