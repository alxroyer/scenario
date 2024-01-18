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
    )
    _stats.print_stats()
"""

import builtins
import importlib
import time
import traceback
import types
import typing

if True:
    from ._fastpath import FAST_PATH as _FAST_PATH  # `FAST_PATH` imported once for performance concerns.
if typing.TYPE_CHECKING:
    from ._logger import Logger as _LoggerType


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
        from ._datetimeutils import f2strduration
        from ._debugutils import CallbackStr

        _current_time = time.time()  # type: float
        self.logger.log(
            self.log_level,
            "%s: %s: %s (+%s)",
            self.context, message,
            CallbackStr(f2strduration, _current_time - self.t0),
            CallbackStr(f2strduration, _current_time - self._last_tick),
        )
        self.ticks.append((message, _current_time - self._last_tick))
        self._last_tick = _current_time

    def finish(self):  # type: (...) -> None
        """
        Terminates logging for the given timer.
        """
        from ._datetimeutils import f2strduration
        from ._debugutils import CallbackStr

        _current_time = time.time()  # type: float
        self.logger.log(
            self.log_level,
            "%s: Total time: %s (+%s)",
            self.context,
            CallbackStr(f2strduration, _current_time - self.t0),
            CallbackStr(f2strduration, _current_time - self._last_tick),
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


class PerfImportWrapper:
    """
    Importer function wrapper for performance analysis.

    Usage:

    .. code-block:: python

        PerfImportWrapper.Stats.clear()
        PerfImportWrapper.install()

        # Code to profile imports here.

        PerfImportWrapper.uninstall()
        PerfImportWrapper.Stats.show(self, logging.WARNING)
    """

    #: Import name to debug callers for.
    refine_import = None  # type: typing.Optional[str]

    class Stats:
        """
        Import statistics for a given module name.
        """

        def __init__(
                self,
                name,  # type: str
        ):  # type: (...) -> None
            """
            :param name: Imported module name.
            """
            #: Imported module name.
            self.name = name  # type: str
            #: Import count for the given module name.
            self.count = 0  # type: int
            #: Total time taken for related imports.
            self.total_time = 0.0  # type: float
            #: Caller statistics.
            self.callers = {}  # type: typing.Dict[str, int]

        @staticmethod
        def clear():  # type: (...) -> None
            """
            Clears :class:`PerfImportWrapper` statistics.
            """
            PerfImportWrapper._stats.clear()

        @staticmethod
        def show(
                logger,  # type: _LoggerType
                level,  # type: int
        ):  # type: (...) -> None
            """
            Shows :class:`PerfImportWrapper` statistics.

            :param logger: Logger object to use for logging.
            :param level: Log level to use for logging.
            """
            for _import_stats in sorted(PerfImportWrapper._stats.values(), key=lambda import_stats: - import_stats.count):  # type: PerfImportWrapper.Stats
                logger.log(level, f"import {_import_stats.name}: " + ", ".join([
                    f"count={_import_stats.count}",
                    f"total_time={_import_stats.total_time:.3f}",
                    f"average={_import_stats.total_time / float(_import_stats.count):.3f}",
                ]))
                for _location_count in sorted(_import_stats.callers.items(), key=lambda t: t[1], reverse=True):  # type: typing.Tuple[str, int]
                    logger.log(level, f"  {_location_count[0]}: {_location_count[1]}")

    #: Import statistics.
    _stats = {}  # type: typing.Dict[str, PerfImportWrapper.Stats]

    #: Initial importer handler.
    _initial_importer = importlib.__import__  # Let type inference do the job.

    @staticmethod
    def install():  # type: (...) -> None
        """
        Installs the importer wrapper.

        .. warning:: Don't install twice in a row! Please :meth:`uninstall()` before.
        """
        PerfImportWrapper._initial_importer = builtins.__import__
        builtins.__import__ = PerfImportWrapper._wrapper

    @staticmethod
    def uninstall():  # type: (...) -> None
        """
        Uninstalls the importer wrapper.

        .. warning:: Don't uninstall if not installed! :meth:`install()` should have been called before.
        """
        builtins.__import__ = PerfImportWrapper._initial_importer

    @staticmethod
    def _wrapper(
            name,  # type: str
            globals=None,  # type: typing.Optional[typing.Mapping[str, typing.Any]]  # noqa  ## Shadows the built-in name 'globals'
            locals=None,  # type: typing.Optional[typing.Mapping[str, typing.Any]]  # noqa  ## Shadows the built-in name 'locals'
            fromlist=(),  # type: typing.Sequence[str]
            level=0,  # type: int
    ):  # type: (...) -> types.ModuleType
        """
        Importer wrapper function.

        Feeds the statistics.
        """
        # Save starting time.
        _t0 = time.time()  # type: float

        # Do import the module.
        _module = PerfImportWrapper._initial_importer(name, globals, locals, fromlist, level)  # type: types.ModuleType

        # Update statistics.
        if name not in PerfImportWrapper._stats:
            PerfImportWrapper._stats[name] = PerfImportWrapper.Stats(name)
        _stats = PerfImportWrapper._stats[name]  # type: PerfImportWrapper.Stats
        _stats.count += 1
        _stats.total_time += (time.time() - _t0)

        # Refined statistics.
        if name == PerfImportWrapper.refine_import:
            # Memo: Skip
            #   (-1) => `PerfImportWrapper._wrapper()` (this method)
            _location = _FAST_PATH.code_location.fromtbitem(traceback.extract_stack()[-2]).tolongstring()  # type: str
            if _location not in _stats.callers:
                _stats.callers[_location] = 0
            _stats.callers[_location] += 1

        # Return the imported module.
        return _module
