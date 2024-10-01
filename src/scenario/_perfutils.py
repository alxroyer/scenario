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
Performance analysis utils.

Memo for python profiling with ``cProfile`` and ``pstats``:

.. code-block:: python

    import cProfile
    import pstats

    _profile = cProfile.Profile()
    _profile.enable()

    # Code to profile here.

    _profile.disable()

    _stats = (
        pstats.Stats(_profile)
        .strip_dirs()
        .sort_stats(pstats.SortKey.CUMULATIVE)
        .reverse_order()
    )
    _stats.print_stats()
"""

import builtins
import os
import time
import traceback
import typing

if True:
    from . import _datetimeutils as _datetimeutils  # @perf
    from . import _debugutils as _debugutils  # @perf
    from ._fastpath import FAST_PATH as _FAST_PATH  # @perf
if typing.TYPE_CHECKING:
    from ._logger import Logger as _LoggerType


class CallLocation:
    """
    Call location management for tool classes in this module.
    """

    #: Base list of paths to skip.
    _base_skipped_paths = [
        # Skip any location from this source file.
        os.path.relpath(__file__, os.getcwd()),
    ]  # type: typing.Sequence[str]

    def __init__(
            self,
            *,
            file,  # type: str
            func="",  # type: str
            line=0,  # type: int
    ):  # type: (...) -> None
        """
        Instantiates a call location object.

        :param file: See :attr:`file`.
        :param line: See :attr:`line`.
        :param func: See :attr:`func`.
        """
        #: Path of source file.
        #: Usually a relative path from the current working directory.
        #: Unix separators.
        self.file = file.replace("\\", "/")  # type: str
        #: Line number in :attr:`file`.
        #: 0 stands for not set.
        self.line = line  # type: int
        #: Function name :attr:`file`
        #: (without class name in case of a method, and without parentheses).
        #: Empty strings stand for not set.
        self.func = func  # type: str

    def __str__(self):  # type: () -> str
        """
        Printable string representation.

        Skips :attr:`line` and :attr:`func` if not relevant.
        """
        _location = self.file  # type: str
        if self.line > 0:
            _location += f":{self.line}"
        if self.func:
            _location += f":{self.func}"
        return _location

    def __eq__(self, other):  # type: (object) -> bool
        """
        Necessary to use :class:`CallLocation` objects as dictionary keys.

        :param other: Object to compare with.
        """
        # Don't use `isinstance()` to avoid infinite cyclic calls when `IsInstanceCallTracker` is in use.
        # if isinstance(other, CallLocation):
        if type(other) is CallLocation:
            return all([
                other.file == self.file,  # noqa  ## Unresolved attribute reference 'file' for class 'object'
                other.line == self.line,  # noqa  ## Unresolved attribute reference 'line' for class 'object'
                other.func == self.func,  # noqa  ## Unresolved attribute reference 'func' for class 'object'
            ])
        return False

    def __hash__(self):  # type: () -> int
        """
        Necessary to use :class:`CallLocation` objects as dictionary keys.
        """
        return hash((self.file, self.line, self.func))

    @staticmethod
    def locate(
            *,
            skipped=None,  # type: typing.Sequence[CallLocation]
    ):  # type: (...) -> CallLocation
        """
        Locates the call location from the current stack.

        :param skipped: Optional list of skipped locations.
        :return: Call location instance.
        """
        skipped = skipped or []
        skipped = [
            *[CallLocation(file=_path) for _path in CallLocation._base_skipped_paths],
            *skipped,
        ]

        for _frame_summary in reversed(traceback.extract_stack()):  # type: traceback.FrameSummary
            _location = CallLocation(
                file=_frame_summary.filename,
                line=_frame_summary.lineno or 0,
                func=_frame_summary.name,
            )  # type: CallLocation

            # Check whether this location is skipped.
            for _skipped_location in skipped:  # type: CallLocation
                if all([
                    _location.file == _skipped_location.file,
                    (not _skipped_location.func) or (_location.func == _skipped_location.func),
                    (not _skipped_location.line) or (_location.line == _skipped_location.line),
                ]):
                    # Location skipped.
                    # Break this inner loop, skip the `else` block below, and proceed with next frame summary.
                    break
            else:
                # Location not skipped.
                return _location

        raise Exception("Can't determine call location")


class Timer:
    """
    Timer with ability to measure intermediate times.
    """

    def __init__(
            self,
            context,  # type: str
            logger,  # type: _LoggerType
            level,  # type: int
    ):  # type: (...) -> None
        """
        Creates and starts a timer object to log execution times.

        :param context: Context description. Usually a function/method name.
        :param logger: Logger object to use for logging.
        :param level: Log level to use for logging.
        """
        #: Context description. Usually a function/method name.
        self.context = context  # type: str
        #: Logger object to use for logging.
        self.logger = logger  # type: _LoggerType
        #: Log level to use for logging.
        self.log_level = level  # type: int

        #: Starting time for this timer.
        self.t0 = time.time()  # type: float
        #: Ticks: tuples of message and elapsed time since the previous tick.
        self.ticks = []  # type: typing.List[typing.Tuple[str, float]]
        #: Last tick time.
        self._last_tick = self.t0  # type: float

    def tick(
            self,
            message,  # type: str
    ):  # type: (...) -> None
        """
        Logs intermediate time information.

        :param message: Object of this tick.
        """
        _current_time = time.time()  # type: float
        self.logger.log(
            self.log_level,
            "%s: %s: %s (+%s)",
            self.context, message,
            _debugutils.callback(_datetimeutils.f2strduration, _current_time - self.t0),
            _debugutils.callback(_datetimeutils.f2strduration, _current_time - self._last_tick),
        )
        self.ticks.append((message, _current_time - self._last_tick))
        self._last_tick = _current_time

    def finish(self):  # type: (...) -> None
        """
        Terminates logging for the given timer.
        """
        _current_time = time.time()  # type: float
        self.logger.log(
            self.log_level,
            "%s: Total time: %s (+%s)",
            self.context,
            _debugutils.callback(_datetimeutils.f2strduration, _current_time - self.t0),
            _debugutils.callback(_datetimeutils.f2strduration, _current_time - self._last_tick),
        )
        self._last_tick = _current_time

    @property
    def total_time(self):  # type: () -> float
        """
        :return: Total time elapsed measured by this timer.
        """
        return self._last_tick - self.t0

    @staticmethod
    def showaverageticktimes(
            timers,  # type: typing.Sequence[Timer]
            logger,  # type: _LoggerType
            level,  # type: int
    ):  # type: (...) -> None
        """
        Prints average tick times for a collection of timers.

        :param timers: Collection of timers to compute average tick times for.
        :param logger: Logger object to use for logging.
        :param level: Log level to use for logging.
        """
        class _TickInfo:
            def __init__(
                    self,
                    message,  # type: str
            ):  # type: (...) -> None
                self.message = message  # type: str
                self.count = 0  # type: int
                self.total_time = 0.0  # type: float

        # Find out the complete list of tick messages over all timers.
        _unique_tick_messages = []  # type: typing.List[str]
        for _timer in timers:  # type: Timer
            _unique_tick_messages.extend(map(lambda tick_tuple: tick_tuple[0], _timer.ticks))
        _unique_tick_messages = list(set(_unique_tick_messages))
        _ticks = [_TickInfo(_tick_message) for _tick_message in _unique_tick_messages]  # type: typing.List[_TickInfo]

        # Sum up tick times.
        for _tick in _ticks:  # type: _TickInfo
            for _timer in timers:  # Type already declared above.
                _matching_tick_tuples = list(filter(
                    lambda tick_tuple: tick_tuple[0] == _tick.message,
                    _timer.ticks,
                ))  # type: typing.Sequence[typing.Tuple[str, float]]
                _tick.count += len(_matching_tick_tuples)
                _tick.total_time += sum([_tick_tuple[1] for _tick_tuple in _matching_tick_tuples])
        _total_time = sum([_tick.total_time for _tick in _ticks])  # type: float

        # Sort by total time descending.
        _ticks.sort(key=lambda tick: tick.total_time, reverse=True)

        # Print out tick times.
        _max_msg_len = max([*map(len, _unique_tick_messages), len("TOTAL")])  # type: int
        logger.log(level, f"{'TOTAL':>{_max_msg_len}}: " + ", ".join([
            f"{len(_ticks)} times ({100.0:.3f}%)",
            f"{_total_time:.3f} seconds ({100.0:.3f}%)",
            f"average: {_total_time / len(_ticks):.3f} seconds",
        ]))
        for _tick in _ticks:  # Type already declared above.
            logger.log(level, f"{_tick.message:>{_max_msg_len}}: " + ", ".join([
                f"{_tick.count} times ({100.0 * float(_tick.count) / float(len(_ticks)) if _ticks else 0.0:.3f}%)",
                f"{_tick.total_time:.3f} seconds ({100.0 * _tick.total_time / _total_time if _total_time else 0.0}%)",
                f"average: {_tick.total_time / _tick.count:.3f} seconds",
            ]))


class CallTracker:
    """
    Tool class for counting and analyzing locations for a given call.

    Locations may be refined by keywords.

    Usage:

    .. code-block:: python

        # Once:
        MY_CALL_TRACKER = CallTracker()
        MY_CALL_TRACKER.skip(CallLocation(...))
        MY_CALL_TRACKER.skip(CallLocation(...))

        # Then, each time the function/method tracked is called:
        MY_CALL_TRACKER.call()
        # Or, for separate keyword entries:
        MY_CALL_TRACKER.call(f"...")
    """

    def __init__(
            self,
            name,  # type: str
    ):  # type: (...) -> None
        """
        Instantiates a new call tracker object.

        :param name: Name of the call tracker.
        """
        #: Call tracker name.
        self.name = name  # type: str

        #: Skipped call locations.
        #: Fed by :meth:`skip()`.
        #: Cleared by :meth:`clear()`.
        self._skipped_locations = []  # type: typing.List[CallLocation]

        #: Keyword entries.
        #: Fed by :meth:`call()`.
        self._keyword_entries = {}  # type: typing.Dict[str, CallTracker._KeywordEntry]

    def skip(
            self,
            location,  # type: CallLocation
    ):  # type: (...) -> None
        """
        Skip call locations matching the given specifications.

        :param location: Call location to skip.
        """
        self._skipped_locations.append(location)

    def call(
            self,
            keyword="",  # type: str
            elapsed=0.0,  # type: float
    ):  # type: (...) -> None
        """
        Registers a call.

        :param keyword: Optional keyword.
        :param elapsed: Elapsed time for the call being registered.
        """
        # Search for an already registered keyword entry, otherwise register a new one.
        try:
            _keyword_entry = self._keyword_entries[keyword]  # type: CallTracker._KeywordEntry
        except KeyError:
            _keyword_entry = self._keyword_entries[keyword] = CallTracker._KeywordEntry(keyword)

        # Determine the call location (without using `ExecutionLocations` implementation).
        _location = CallLocation.locate(skipped=self._skipped_locations)  # type: CallLocation

        # Search for an already registered location entry, otherwise register a new one.
        try:
            _location_entry = _keyword_entry.locations[_location]  # type: CallTracker._LocationEntry
        except KeyError:
            _location_entry = _keyword_entry.locations[_location] = CallTracker._LocationEntry()

        # Increment call count and cumulative time.
        _location_entry.count += 1
        _location_entry.cumulative_time += elapsed

    def clear(self):  # type: (...) -> None
        """
        Clears keyword entries, with call locations already registered if any.
        """
        self._keyword_entries.clear()

    def show(
            self,
            logger,  # type: _LoggerType
            level,  # type: int
            *,
            reverse=False,  # type: bool
    ):  # type: (...) -> None
        """
        Displays results.

        :param logger:
            Logger object to use for logging.
        :param level:
            Log level to use for logging.
        :param reverse:
            ``False`` to start with highest counts (same default presentation as ``cProfile`` / ``pstats``,
            ``True`` to end with highest counts.
        """
        logger.log(level, f"{self.name}:")

        with logger.pushindentation("  "):
            def _logtotal():  # type: (...) -> None
                _total_count = sum([_.count for _ in self._keyword_entries.values()])  # type: int
                _total_cumulative_time = sum([_.cumulative_time for _ in self._keyword_entries.values()])  # type: float
                logger.log(level, f"    {_total_count} / {_total_cumulative_time:.3f}: TOTAL")

            if not self._keyword_entries:
                logger.log(level, "No entry")

            else:
                if (not reverse) and (len(self._keyword_entries) > 1):
                    _logtotal()
                    logger.log(level, "---")

                for _keyword_entry in sorted(
                    self._keyword_entries.values(),
                    key=lambda keyword_entry: keyword_entry.count,
                    reverse=not reverse,
                ):  # type: CallTracker._KeywordEntry
                    logger.log(level, f"{_keyword_entry.count} / {_keyword_entry.cumulative_time:.3f}: {_keyword_entry.keyword or '(all)'}:")

                    with logger.pushindentation("  "):
                        for _location, _location_entry in sorted(
                            _keyword_entry.locations.items(),
                            key=lambda t: t[1].count,  # Sort on location counts.
                            reverse=not reverse,
                        ):  # type: CallLocation, CallTracker._LocationEntry
                            logger.log(level, f"{_location_entry.count} / {_location_entry.cumulative_time:.3f}: {_location}")

                if reverse and (len(self._keyword_entries) > 1):
                    logger.log(level, "---")
                    _logtotal()

    class _KeywordEntry:
        """
        Keyword entry.
        """

        def __init__(
                self,
                keyword,  # type: str
        ):  # type: (...) -> None
            """
            :param keyword: Keyword associated with this entry.
            """
            #: Keyword of the entry.
            self.keyword = keyword  # type: str
            #: Call locations.
            self.locations = {}  # type: typing.Dict[CallLocation, CallTracker._LocationEntry]

        @property
        def count(self):  # type: () -> int
            """
            Sum of call location counts associated with this entry.
            """
            return sum([_location_entry.count for _location_entry in self.locations.values()])

        @property
        def cumulative_time(self):  # type: () -> float
            """
            Sum of call location times associated with this entry.
            """
            return sum([_location_entry.cumulative_time for _location_entry in self.locations.values()])

    class _LocationEntry:
        """
        Call location entry.
        """

        def __init__(self):  # type: (...) -> None
            """
            Initializes a call location entry with 0 for :attr:`count` and :attr:`cumulative_time`.
            """
            #: Number of times this call location has occurred.
            self.count = 0  # type: int
            #: Cumulative time elapsed for the :attr:`count` calls.
            #: May be unused.
            self.cumulative_time = 0.0  # type: float


class WrapperCallTracker(CallTracker):
    """
    Function wrapper for performance analysis.

    Works also with ``builtins`` functions!

    Example:

    .. code-block:: python

        _path_init_call_tracker = WrapperCallTracker(
            Path, "__init__",
            keyword=lambda args, kwargs, ret: f"Path(path={args[0]!r}, relative_to={args[1]!r})",
        )
        _path_init_call_tracker.skip(CallLocation(file="src/scenario/_path.py", func="__init__"))
        _path_init_call_tracker.install()

        # Code to profile `Path.__init__()` calls here.

        _path_init_call_tracker.uninstall()
        _path_init_call_tracker.show(scenario.logging, logging.WARNING)
    """

    if typing.TYPE_CHECKING:
        #: Keyword computation handler type.
        #:
        #: Arguments:
        #:
        #: 1. Positional arguments.
        #: 2. Named arguments.
        #: 3. Return value.
        #:
        #: Return value:
        #:
        #: - Keyword computed from the arguments above.
        KeywordHandlerType = typing.Callable[
            [
                typing.Sequence[typing.Any],
                typing.Mapping[str, typing.Any],
                typing.Any,
            ],
            str,
        ]

    def __init__(
            self,
            obj,  # type: object
            name,  # type: str
            *,
            keyword=None,  # type: WrapperCallTracker.KeywordHandlerType
    ):  # type: (...) -> None
        """
        Saves the owner object and name of the function to wrap.

        :param obj: See :attr:`wrapped_obj`.
        :param name: See :attr:`wrapped_name`.
        :param keyword: Optional keyword computation handler.
        """
        CallTracker.__init__(self, f"{_FAST_PATH.reflection.qualname(obj)}.{name}()")

        #: Object owning the function to wrap.
        self.wrapped_obj = obj  # type: object
        #: Name of the function to wrap in :attr:`wrapped_obj`.
        self.wrapped_name = name  # type: str

        #: Keyword computation handler.
        self.keyword = keyword or (lambda arg, kwargs, ret: "")  # type: WrapperCallTracker.KeywordHandlerType

        #: Initial function handler.
        #: Saved by :meth:`install()` and restored by :meth:`uninstall()`.
        self._initial_function = None  # type: typing.Any

    def install(self):  # type: (...) -> None
        """
        Installs the function wrapper.

        .. warning:: Don't install twice in a row! Please :meth:`uninstall()` before.
        """
        assert self._initial_function is None, f"{self.name}: Don't install the function wrapper twice in a row"
        self._initial_function = getattr(self.wrapped_obj, self.wrapped_name)
        setattr(self.wrapped_obj, self.wrapped_name, lambda *args, **kwargs: WrapperCallTracker._wrapper(self, args, kwargs))

    def uninstall(self):  # type: (...) -> None
        """
        Uninstalls the function wrapper.

        .. warning:: Don't uninstall if not installed! :meth:`install()` should have been called before.
        """
        assert self._initial_function is not None, f"{self.name}: Function wrapper not installed"
        setattr(self.wrapped_obj, self.wrapped_name, self._initial_function)
        self._initial_function = None

    @staticmethod
    def _wrapper(
            self,  # type: WrapperCallTracker
            args,  # type: typing.Sequence[typing.Any]
            kwargs,  # type: typing.Mapping[str, typing.Any]
    ):  # type: (...) -> typing.Any
        """
        Function wrapper.

        Tracks the call statistics.

        Defined as a static method to avoid positional argument errors due to ``self`` management of Python.
        """
        # Save starting time.
        _t0 = time.time()  # type: float

        # Call the real function.
        _res = self._initial_function(*args, **kwargs)  # type: typing.Any

        # Register the call.
        self.call(self.keyword(args, kwargs, _res), elapsed=time.time() - _t0)

        # Return value.
        return _res


class ImportCallTracker(WrapperCallTracker):
    """
    :class:`WrapperCallTracker` specialization for ``import`` statements.

    Example:

    .. code-block:: python

        _import_call_tracker = ImportCallTracker()
        _import_call_tracker.install()

        # Code to profile imports here.

        _import_call_tracker.uninstall()
        _import_call_tracker.show(scenario.logging, logging.WARNING)
    """

    def __init__(self):  # type: (...) -> None
        """
        Configures the base :class:`WrapperCallTracker` class for ``import`` wrapping.
        """
        WrapperCallTracker.__init__(
            self,
            builtins, "__import__",
            keyword=ImportCallTracker._keyword,
        )

    @staticmethod
    def _keyword(
            args,  # type: typing.Sequence[typing.Any]
            kwargs,  # type: typing.Mapping[str, typing.Any]  # noqa  ## Unused parameter.
            ret,  # type: typing.Any  # noqa  ## Unused parameter.
    ):  # type: (...) -> str
        """
        Computes :class:`CallTracker` keywords from ``import`` arguments.
        """
        _name = args[0]  # type: str
        _globals = args[1]  # type: typing.Optional[typing.Mapping[str, typing.Any]]
        _fromlist = args[3]  # type: typing.Sequence[str]

        # `from . import xxx` imports: fix empty `name` value with the expected single value in `fromlist`.
        if not _name:
            if len(_fromlist) != 1:
                raise ImportError("Unexpected `from . import xxx, xxx` with several modules imported at once")
            _name = _fromlist[0]

        # Full qualified name, if applicable.
        if _globals and ("__package__" in _globals) and _globals["__package__"]:
            _name = f"{_globals['__package__']}.{_name}"

        return _name


class IsInstanceCallTracker(WrapperCallTracker):
    """
    :class:`WrapperCallTracker` specialization for ``isinstance()`` calls.

    Example:

    .. code-block:: python

        _is_instance_call_tracker = IsInstanceCallTracker()
        _is_instance_call_tracker.install()

        # Code to profile `isinstance()` calls here.

        _is_instance_call_tracker.uninstall()
        _is_instance_call_tracker.show(scenario.logging, logging.WARNING)
    """

    def __init__(self):  # type: (...) -> None
        """
        Configures the base :class:`WrapperCallTracker` class for ``isinstance()`` wrapping.
        """
        WrapperCallTracker.__init__(
            self,
            builtins, "isinstance",
            keyword=lambda args, kwargs, ret: str(args[1]),
        )
