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
Path management.
"""

import logging
import os
import pathlib
import sys
import tempfile
import typing


if typing.TYPE_CHECKING:
    #: Type for path-like data: either a simple string or a ``os.PathLike`` instance.
    AnyPathType = typing.Union[str, os.PathLike]


class Path:
    """
    Helper class for path management.

    This class really looks like ``pathlib.Path``,
    but differs from it in that:

    1. it ensures persistent paths, even though initialized from a relative path and the current directory changes afterwards,
    2. it provides a :attr:`prettypath` display from a main directory set for the current project (see :meth:`setmainpath()`),
    3. it does not describe the current working implicitely when initialized from nothing, but a *void* path.

    The :class:`Path` class supports the ``os.PathLike`` interface.
    """

    #: Main path, used to compute the relative :attr:`prettypath`.
    #: Unset by default.
    _main_path = None  # type: typing.Optional[Path]

    @staticmethod
    def setmainpath(
            path,  # type: typing.Optional[AnyPathType]
            log_level=logging.INFO,  # type: int
    ):  # type: (...) -> None
        """
        Sets the main path, used to compute the relative :attr:`prettypath`.

        :param path: New main path.
        :param log_level: Log level (as defined by the standard ``logging`` package) to use for the related log line.
        """
        from ._loggermain import MAIN_LOGGER

        if path is None:
            if Path._main_path is not None:
                MAIN_LOGGER.log(log_level, "Main path unset")
        else:
            if not isinstance(path, Path):
                path = Path(path)
            if (Path._main_path is None) or (not path.samefile(Path._main_path)):
                MAIN_LOGGER.log(log_level, f"Main path: '{path.abspath}'")
        Path._main_path = path

    @staticmethod
    def getmainpath():  # type: (...) -> typing.Optional[Path]
        """
        :return: Main path, i.e. base path for :attr:`prettypath` computations.
        """
        return Path._main_path

    @staticmethod
    def cwd():  # type: (...) -> Path
        """
        Computes a :class:`Path` instance representing the current working directory.

        :return: Current working directory.
        """
        return Path(os.getcwd())

    @staticmethod
    def home():  # type: (...) -> Path
        """
        Computes a :class:`Path` instance representing the current user's home directory.

        :return: Current user's home directory.
        """
        if sys.version_info >= (3, 5):
            return Path(pathlib.Path.home())
        else:
            raise EnvironmentError(f"Python {sys.version} not supported")

    @staticmethod
    def tmp():  # type: (...) -> Path
        """
        Computes a :class:`Path` instance representing the temporary directory.

        :return: Temporary directory.
        """
        return Path(tempfile.gettempdir())

    def __init__(
            self,
            path=None,  # type: AnyPathType
            relative_to=None,  # type: Path
    ):  # type: (...) -> None
        """
        Ensures the management of an absolute path.

        :param path:
            File or directory path as a path-like.

            Makes the :class:`Path` instance *void* when not set.
        :param relative_to:
            Base directory or file to consider as the root, when the path given is a relative path.

            Giving a file path as ``relative_to`` is equivalent to giving its owner directory.

        If the path given is relative, it is transformed in its absolute form from the current working directory.
        """
        #: ``pathlib.Path`` instance used to store the absolute path described by this :class:`Path` instance.
        self._abspath = pathlib.Path("//void/path")  # type: pathlib.Path
        if isinstance(path, Path):
            # No need to duplicate the immutable `pathlib.Path` object.
            # The latter can be shared between the two `scenario.Path` instances.
            self._abspath = path._abspath
        elif path:
            # Find out whether `path` is relative, and `relative_to` is set.
            path = pathlib.Path(path)
            if (not path.is_absolute()) and relative_to:
                # Note:
                # Use of an intermediate `pathlib.Path` object in order to help type checkings.
                # `is_file()` may not be known yet for `scenario.Path`.
                if pathlib.Path(relative_to).is_file():
                    relative_to = relative_to.parent
                self._abspath = pathlib.Path(relative_to) / path
            else:
                # Let's resolve `path` as is otherwise.
                self._abspath = path.resolve()

        # === `pathlib.PurePath` API support ===
        # `pathlib.PurePath.parts` implemented as a member property.
        # `pathlib.PurePath.drive` implemented as a member property.
        # `pathlib.PurePath.root` implemented as a member property.
        # `pathlib.PurePath.anchor` implemented as a member property.
        # `pathlib.PurePath.parents` implemented as a member property.
        # `pathlib.PurePath.parent` implemented as a member property.
        # `pathlib.PurePath.name` implemented as a member property.
        # `pathlib.PurePath.suffix` implemented as a member property.
        # `pathlib.PurePath.suffixes` implemented as a member property.
        # `pathlib.PurePath.stem` implemented as a member property.
        self.as_posix = self._abspath.as_posix  #: Shortcut to ``pathlib.PurePath.as_posix()``.
        self.as_uri = self._abspath.as_uri  #: Shortcut to ``pathlib.PurePath.as_uri()``.
        # `pathlib.PurePath.is_absolute()` implemented as a static method (not a member method, which differs from `pathlib`!).
        # `pathlib.PurePath.is_relative_to()` implemented as a member method.
        self.is_reserved = self._abspath.is_reserved  #: Shortcut to ``pathlib.PurePath.is_reserved()``.
        # `pathlib.PurePath.joinpath()` implemented as a member method.
        self.match = self._abspath.match  #: Shortcut to ``pathlib.PurePath.match()``.
        # `pathlib.PurePath.relative_to()` implemented as a member method.
        # `pathlib.PurePath.with_name()` implemented as a member method.
        # `pathlib.PurePath.with_stem()` implemented as a member method.
        # `pathlib.PurePath.with_suffix()` implemented as a member method.

        # === `pathlib.Path` API support ===
        # `pathlib.Path.cwd()` implemented as a static method.
        # `pathlib.Path.home()` implemented as a static method.
        self.stat = self._abspath.stat  #: Shortcut to ``pathlib.Path.stat()``.
        self.chmod = self._abspath.chmod  #: Shortcut to ``pathlib.Path.chmod()``.
        self.exists = self._abspath.exists  #: Shortcut to ``pathlib.Path.exists()``.
        if sys.version_info >= (3, 5):
            self.expanduser = self._abspath.expanduser  #: Shortcut to ``pathlib.Path.expanduser()``.
        # `pathlib.Path.glob()` implemented as a member method.
        if sys.platform != "win32":
            # Memo: `Path.group()` raises "NotImplementedError: Path.group() is unsupported on this system" under Windows.
            self.group = self._abspath.group  #: Shortcut to ``pathlib.Path.group()``.
        self.is_dir = self._abspath.is_dir  #: Shortcut to ``pathlib.Path.is_dir()``.
        self.is_file = self._abspath.is_file  #: Shortcut to ``pathlib.Path.is_file()``.
        if sys.version_info >= (3, 7):
            self.is_mount = self._abspath.is_mount  #: Shortcut to ``pathlib.Path.is_mount()``.
        self.is_symlink = self._abspath.is_symlink  #: Shortcut to ``pathlib.Path.is_symlink()``.
        self.is_socket = self._abspath.is_socket  #: Shortcut to ``pathlib.Path.is_socket()``.
        self.is_fifo = self._abspath.is_fifo  #: Shortcut to ``pathlib.Path.is_fifo()``.
        self.is_block_device = self._abspath.is_block_device  #: Shortcut to ``pathlib.Path.is_block_device()``.
        self.is_char_device = self._abspath.is_char_device  #: Shortcut to ``pathlib.Path.is_char_device()``.
        # `pathlib.Path.iterdir()` implemented as a member method.
        self.lchmod = self._abspath.lchmod  #: Shortcut to ``pathlib.Path.lchmod()``.
        self.lstat = self._abspath.lstat  #: Shortcut to ``pathlib.Path.lstat()``.
        self.mkdir = self._abspath.mkdir  #: Shortcut for ``pathlib.Path.mkdir()``.
        self.open = self._abspath.open  #: Shortcut to ``pathlib.Path.open()``.
        if sys.platform != "win32":
            # Memo: `Path.owner()` raises "NotImplementedError: Path.owner() is unsupported on this system" under Windows.
            self.owner = self._abspath.owner  #: Shortcut to ``pathlib.Path.owner()``.
        if sys.version_info >= (3, 5):
            self.read_bytes = self._abspath.read_bytes  #: Shortcut to ``pathlib.Path.read_bytes()``.
            self.read_text = self._abspath.read_text  #: Shortcut to ``pathlib.Path.read_text()``.
        if sys.version_info >= (3, 9):
            self.readlink = self._abspath.readlink  #: Shortcut to ``pathlib.Path.readlink()``.
        # `pathlib.Path.rename()` implemented as a member method.
        # `pathlib.Path.replace()` implemented as a member method.
        # `pathlib.Path.resolve()` implemented as a member method.
        # `pathlib.Path.rglob()` implemented as a member method.
        self.rmdir = self._abspath.rmdir  #: Shortcut to ``pathlib.Path.rmdir()``.
        # `pathlib.Path.samefile()` implemented as a member method.
        self.symlink_to = self._abspath.symlink_to  #: Shortcut to ``pathlib.Path.symlink_to()``.
        if sys.version_info >= (3, 10):
            self.hardlink_to = self._abspath.hardlink_to  #: Shortcut to ``pathlib.Path.hardlink_to()``.
        if sys.version_info >= (3, 8):
            self.link_to = self._abspath.link_to  #: Shortcut to ``pathlib.Path.link_to()``.
        self.touch = self._abspath.touch  #: Shortcut to ``pathlib.Path.touch()``.
        self.unlink = self._abspath.unlink  #: Shortcut to ``pathlib.Path.unlink()``.
        if sys.version_info >= (3, 5):
            self.write_bytes = self._abspath.write_bytes  #: Shortcut to ``pathlib.Path.write_bytes()``.
            self.write_text = self._abspath.write_text  #: Shortcut to ``pathlib.Path.write_text()``.

    def __fspath__(self):  # type: () -> str
        """
        ``os.PathLike`` interface implementation.
        """
        return os.fspath(self._abspath)

    def __repr__(self):  # type: () -> str
        """
        Canonical string representation.
        """
        from ._reflection import qualname

        return f"<{qualname(type(self))} object for '{self.prettypath}'>"

    def __str__(self):  # type: () -> str
        """
        Human readable string representation (same as :attr:`prettypath`).
        """
        return self.prettypath

    def __hash__(self):  # type: () -> int
        """
        Hash computation.

        Makes it possible to use :class:`Path` objects as dictionary keys.
        """
        return hash(self._abspath)

    @property
    def parts(self):  # type: () -> typing.Tuple[str, ...]
        """
        See `pathlib.PurePath.parts <https://docs.python.org/3/library/pathlib.html#pathlib.PurePath.parts>`_.
        """
        return self._abspath.parts

    @property
    def drive(self):  # type: () -> str
        """
        See `pathlib.PurePath.drive <https://docs.python.org/3/library/pathlib.html#pathlib.PurePath.drive>`_.
        """
        return self._abspath.drive

    @property
    def root(self):  # type: () -> str
        """
        See `pathlib.PurePath.root <https://docs.python.org/3/library/pathlib.html#pathlib.PurePath.root>`_.
        """
        return self._abspath.root

    @property
    def anchor(self):  # type: () -> str
        """
        See `pathlib.PurePath.anchor <https://docs.python.org/3/library/pathlib.html#pathlib.PurePath.anchor>`_.
        """
        return self._abspath.anchor

    @property
    def parents(self):  # type: () -> typing.Sequence[Path]
        """
        Gives the list of parent directories as :class:`Path` objects.

        See `pathlib.PurePath.parents <https://docs.python.org/3/library/pathlib.html#pathlib.PurePath.parents>`_.
        """
        return tuple([Path(_path) for _path in self._abspath.parents])

    @property
    def parent(self):  # type: () -> Path
        """
        Gives the parent directory as a :class:`Path` object.

        See `pathlib.PurePath.parent <https://docs.python.org/3/library/pathlib.html#pathlib.PurePath.parent>`_.
        """
        return Path(self._abspath.parent)

    @property
    def name(self):  # type: () -> str
        """
        Base name of the path.

        See `pathlib.PurePath.name <https://docs.python.org/3/library/pathlib.html#pathlib.PurePath.name>`_.
        """
        return self._abspath.name

    @property
    def suffix(self):  # type: () -> str
        """
        Gives the extension of the file (or directory name), with its leading dot, if any,
        or an empty string if no extension.

        See `pathlib.PurePath.suffix <https://docs.python.org/3/library/pathlib.html#pathlib.PurePath.suffix>`_.
        """
        return self._abspath.suffix

    @property
    def suffixes(self):  # type: () -> typing.List[str]
        """
        Gives the list of consecutive extensions, with their leading dot character.

        See `pathlib.PurePath.suffixes <https://docs.python.org/3/library/pathlib.html#pathlib.PurePath.suffixes>`_.
        """
        return self._abspath.suffixes

    @property
    def stem(self):  # type: () -> str
        """
        Gives the basename of the path, without the final extension if any.

        See `pathlib.PurePath.stem <https://docs.python.org/3/library/pathlib.html#pathlib.PurePath.stem>`_.
        """
        return self._abspath.stem

    @property
    def abspath(self):  # type: () -> str
        """
        Absolute form of the path in the POSIX style.
        """
        return self._abspath.as_posix()

    @property
    def prettypath(self):  # type: () -> str
        """
        Gives the pretty path.

        The pretty path is actually a relative path from the main path if set (see :meth:`setmainpath()`),
        or the current working directory otherwise,
        and presented in the POSIX style.
        """
        _ref_path = Path.cwd()  # type: Path
        if Path._main_path is not None:
            _ref_path = Path._main_path
        _prettypath = self._abspath.as_posix()  # type: str
        if self.is_relative_to(_ref_path) and (self != _ref_path):
            _prettypath = self.relative_to(_ref_path)
        return _prettypath

    def resolve(self):  # type: (...) -> Path
        """
        Retrieves another :class:`Path` instance similar to this one.

        :return: New :class:`Path` instance.
        """
        return Path(self)

    def __eq__(
            self,
            other,  # type: object
    ):  # type: (...) -> bool
        """
        Checks whether ``other`` equals to this path.

        :param other: Path to checks against.
        :return: ``True`` when the paths equal, ``False`` otherwise.
        """
        if isinstance(other, (str, os.PathLike)):
            try:
                return self.samefile(other)
            except FileNotFoundError:
                # May occur when `self` does not exist.
                return self.abspath == Path(other).abspath
        return False

    def samefile(
            self,
            other,  # type: AnyPathType
    ):  # type: (...) -> bool
        """
        Returns ``True`` when ``other`` describes the same path as this one.

        :param other: Other path (or anything that is not a path at all).
        :return: ``True`` when ``other`` is the same path.
        """
        if not isinstance(other, Path):
            try:
                other = Path(other)
            except OSError:
                # ``other`` cannot be interpreted as a path.
                return False

        if self.exists() and other.exists():
            return self._abspath.samefile(other._abspath)
        else:
            return os.fspath(self) == os.fspath(other)

    def __truediv__(
            self,
            other,  # type: str
    ):  # type: (...) -> Path
        """
        Joins this directory path with a sub-path.

        :param other: Sub-path to apply from this directory path.
        :return: New :class:`Path` instance.
        """
        return Path(self._abspath / other)

    def joinpath(
            self,
            *other  # type: str
    ):  # type: (...) -> Path
        """
        Joins this directory path with a list of sub-paths.

        :param other: Sub-paths to apply from this directory path.
        :return: New :class:`Path` instance.
        """
        return Path(self._abspath.joinpath(*other))

    def with_name(
            self,
            name,  # type: str
    ):  # type: (...) -> Path
        """
        See `pathlib.PurePath.with_name() <https://docs.python.org/3/library/pathlib.html#pathlib.PurePath.with_name>`_.
        """
        return Path(self._abspath.with_name(name))

    def with_stem(
            self,
            stem,  # type: str
    ):  # type: (...) -> Path
        """
        See `pathlib.PurePath.with_stem() <https://docs.python.org/3/library/pathlib.html#pathlib.PurePath.with_stem>`_.
        """
        if sys.version_info >= (3, 9):
            return Path(self._abspath.with_stem(stem))
        else:
            # Note: `PurePath.with_stem()` exists only from Python 3.9.
            return self.parent / (stem + self.suffix)

    def with_suffix(
            self,
            suffix,  # type: str
    ):  # type: (...) -> Path
        """
        See `pathlib.PurePath.with_suffix() <https://docs.python.org/3/library/pathlib.html#pathlib.PurePath.with_suffix>`_.
        """
        return Path(self._abspath.with_suffix(suffix))

    def is_void(self):  # type: (...) -> bool
        """
        Tells whether this path is void.

        :return: ``True`` when the path is void, ``False`` otherwise.
        """
        return self == Path()

    @staticmethod
    def is_absolute(
            path,  # type: AnyPathType
    ):  # type: (...) -> bool
        """
        Tells whether a given path is an absolute path.

        :param path: Path to check.
        :return: ``True`` when ``path`` is an absolute path, ``False`` otherwise.
        """
        try:
            return pathlib.Path(path).is_absolute()
        except:  # noqa  ## Too broad exception clause.
            return False

    def is_relative_to(
            self,
            other,  # type: AnyPathType
    ):  # type: (...) -> bool
        """
        Tells whether this path is a sub-path of the candidate parent directory.

        :param other: Candidate parent directory.
        :return: ``True`` when this path is a sub-path of ``other``.

        See `pathlib.PurePath.is_relative_to() <https://docs.python.org/3/library/pathlib.html#pathlib.PurePath.is_relative_to>`_.
        """
        if sys.version_info >= (3, 9):
            return self._abspath.is_relative_to(other)
        else:
            # Note: `PurePath.is_relative_to()` exists only from Python 3.9.
            if not isinstance(other, Path):
                other = Path(other)
            return os.fspath(self).startswith(os.fspath(other))

    def relative_to(
            self,
            other,  # type: AnyPathType
    ):  # type: (...) -> str
        """
        Computes a relative path.

        :param other: Reference path to compute the relative path from.
        :return: Relative path from ``other`` in the POSIX style.

        .. note::
            The behaviour of this method differs from the one of ``pathlib.PurePath.relative_to()``.

            ``pathlib.PurePath.relative_to()`` raises a ``ValueError`` as soon as this path is not a sub-path of ``other``.
            In order te be able compute relative paths beginning with "../", we use ``os.path.relpath()`` instead.

        See `pathlib.PurePath.relative_to() <https://docs.python.org/3/library/pathlib.html#pathlib.PurePath.relative_to>`_.
        """
        if not isinstance(other, Path):
            other = Path(other)
        # Use `os.path.relpath()` instead of `pathlib.PurePath.relative_to()`.
        return pathlib.Path(os.path.relpath(self._abspath, other)).as_posix()

    def iterdir(self):  # type: (...) -> typing.Iterator[Path]
        """
        Lists this directory path.

        :return: Paths iterator.

        See `pathlib.Path.iterdir() <https://docs.python.org/3/library/pathlib.html#pathlib.Path.iterdir>`_.
        """
        return [Path(_subpath) for _subpath in self._abspath.iterdir()].__iter__()

    def glob(
            self,
            pattern,  # type: str
    ):  # type: (...) -> typing.Iterator[Path]
        """
        Returns the list of files that match the given pattern.

        :param pattern:
            Path pattern (see ``glob.glob()``).
            May be either a relative or an absolute path specification.
        :return:
            List of paths that match the pattern.

        See `pathlib.Path.glob() <https://docs.python.org/3/library/pathlib.html#pathlib.Path.glob>`_.
        """
        return [Path(_match) for _match in self._abspath.glob(pattern)].__iter__()

    def rglob(
            self,
            pattern,  # type: str
    ):  # type: (...) -> typing.Iterator[Path]
        """
        See `pathlib.Path.rglob() <https://docs.python.org/3/library/pathlib.html#pathlib.Path.rglob>`_.
        """
        return [Path(_match) for _match in self._abspath.rglob(pattern)].__iter__()

    def rename(
            self,
            target,  # type: AnyPathType
    ):  # type: (...) -> Path
        """
        Moves this file or directory as ``target``.

        :param target: Target path.
        :return: New target :class:`Path` instance.

        See `pathlib.Path.rename() <https://docs.python.org/3/library/pathlib.html#pathlib.Path.rename>`_.
        """
        self._abspath.rename(pathlib.Path(target))
        # Note: `pathlib.Path.rename()` returns the new path only from Python 3.8.
        return Path(target)

    def replace(
            self,
            target,  # type: AnyPathType
    ):  # type: (...) -> Path
        """
        See `pathlib.Path.replace() <https://docs.python.org/3/library/pathlib.html#pathlib.Path.replace>`_.
        """
        self._abspath.replace(pathlib.Path(target))
        # Note: `pathlib.Path.replace()` returns the new path only from Python 3.8.
        return Path(target)
