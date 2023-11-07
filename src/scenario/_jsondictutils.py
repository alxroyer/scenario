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
import re
import typing

if typing.TYPE_CHECKING:
    from ._path import AnyPathType as _AnyPathType


if typing.TYPE_CHECKING:
    #: JSON dictionary type.
    #:
    #: Applicable to YAML data as well.
    JsonDictType = typing.Dict[str, typing.Any]


class JsonDict(abc.ABC):
    """
    Abstract class that provides useful class methods to work with JSON-like dictionaries.
    """

    #: Recognized JSON file suffixes.
    #:
    #: Lower case only.
    JSON_SUFFIXES = (".json", )  # type: typing.Sequence[str]

    #: Recognized YAML file suffixes.
    #:
    #: Lower case only.
    YAML_SUFFIXES = (".yml", ".yaml", )  # type: typing.Sequence[str]

    @staticmethod
    def assertjsondictinstance(
            obj,  # type: typing.Any
    ):  # type: (...) -> JsonDictType
        """
        Checks whether ``obj`` is a JSON-like dictionary.

        :param obj: Object to check.
        :return: ``obj`` as a JSON-like dictionary.
        """
        from ._debugutils import saferepr

        if isinstance(obj, dict) and all([isinstance(_key, str) for _key in obj]):
            return obj
        else:
            raise TypeError(f"{saferepr(obj)} not a JSON-like dictionary")

    @staticmethod
    def isjson(
            path,  # type: _AnyPathType
    ):  # type: (...) -> bool
        """
        Determines whether the given file is a JSON file.

        :param path: Path of the file which format to check.
        :return: ``True`` if the file is a JSON file, ``False`` otherwise.

        Based of file suffix only, not on file content.
        """
        from ._path import Path

        return Path(path).suffix.lower() in JsonDict.JSON_SUFFIXES

    @staticmethod
    def isyaml(
            path,  # type: _AnyPathType
    ):  # type: (...) -> bool
        """
        Determines whether the given file is a YAML file.

        :param path: Path of the file which format to check.
        :return: ``True`` if the file is a YAML file, ``False`` otherwise.

        Based of file suffix only, not on file content.
        """
        from ._path import Path

        return Path(path).suffix.lower() in JsonDict.YAML_SUFFIXES

    @staticmethod
    def isknwonsuffix(
            path,  # type: _AnyPathType
    ):  # type: (...) -> bool
        """
        Tells whether the file is of one of the recognized formats containing JSON-like dictionaries.

        :param path: Path of the file which suffix to check.
        :return: ``True`` if the file type may contain a JSON-like dictionary.
        """
        return any([
            JsonDict.isjson(path),
            JsonDict.isyaml(path),
        ])

    @staticmethod
    def isschema(
            path,  # type: _AnyPathType
            schema_subpath,  # type: str
    ):  # type: (...) -> bool
        """
        Tells whether an existing file corresponds to an expected JSON schema.

        Schema will be search in the first lines of the file content.

        :param path: File which schema to check.
        :param schema_subpath: Schema subpath, from the root directory of this repository.
        :return: ``True`` when the file matches the given schema, ``False`` otherwise.
        """
        from ._pkginfo import PKG_INFO

        _file = open(path, "rb")  # type: typing.BinaryIO
        try:
            # Read the 5 first lines only.
            for _ in range(5):
                _line = _file.readline()  # type: bytes
                _regex = r'%s/(.*/)*%s' % (PKG_INFO.repo_url, schema_subpath)  # type: str
                if re.search(_regex.encode("utf-8"), _line):
                    return True
            return False
        finally:
            _file.close()

    @staticmethod
    def readfile(
            input_path,  # type: _AnyPathType
            *,
            encoding=None,  # type: str
    ):  # type: (...) -> JsonDictType
        """
        Reads a JSON-like dictionary from an input file.

        Automatically recognizes the file format from its suffix.

        :param input_path: Path of the file to read.
        :param encoding: Encoding to use for reading. Automatically determined from the file content by default.
        :return: JSON-like dictionary read from the input file.
        """
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
        """
        Writes JSON-like content into a file.

        Adds meta information at the beginning of the ``content`` dictionary when set:

        - ``"$encoding"``,
        - ``"$schema"`` and ``"$version"`` when ``schema_subpath`` is provided.

        :param content:
            JSON-like dictionary content.
        :param output_path:
            Output file to write.

            Intermediate directories will be created if needed.
        :param schema_subpath:
            Optional schema subpath, from the root directory of this repository.
        :param encoding:
            Optional encoding specification.

            'utf-8' by default.
        :param indent:
            Number of space characters for indentation.
        """
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
