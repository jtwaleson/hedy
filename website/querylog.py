import datetime
import functools
import os
import threading
import time

from . import log_queue
from typing import Callable, Dict, Union

IS_WINDOWS = os.name == "nt"
if not IS_WINDOWS:
    import resource


class LogRecord:
    """A log record."""

    def __init__(self, **kwargs) -> None:
        self.start_time = time.time()

        if not IS_WINDOWS:
            self.start_rusage = resource.getrusage(resource.RUSAGE_SELF)
        self.attributes = kwargs
        self.running_timers = set([])
        loadavg = os.getloadavg()[0] if not IS_WINDOWS else None
        self.set(start_time=dtfmt(self.start_time), pid=os.getpid(), loadavg=loadavg, fault=0)

        dyno = os.getenv("DYNO")
        if dyno:
            self.set(dyno=dyno)

    def finish(self) -> None:
        end_time = time.time()
        if not IS_WINDOWS:
            end_rusage = resource.getrusage(resource.RUSAGE_SELF)
            user_ms = ms_from_fsec(end_rusage.ru_utime - self.start_rusage.ru_utime)
            sys_ms = ms_from_fsec(end_rusage.ru_stime - self.start_rusage.ru_stime)
            max_rss = end_rusage.ru_maxrss
            inc_max_rss = max_rss - self.start_rusage.ru_maxrss
        else:
            user_ms = None
            sys_ms = None
            max_rss = None
            inc_max_rss = None

        self.set(
            end_time=dtfmt(end_time),
            user_ms=user_ms,
            sys_ms=sys_ms,
            max_rss=max_rss,
            inc_max_rss=inc_max_rss,
            duration_ms=ms_from_fsec(end_time - self.start_time),
        )

        # There should be 0, but who knows
        self._terminate_running_timers()

        LOG_QUEUE.add(self.as_data())

    def set(self, **kwargs) -> None:
        """Set keys based on keyword arguments."""
        self.attributes.update(kwargs)

    def update(self, dict):
        """Set keys based on a dictionary."""
        self.attributes.update(dict)

    def timer(self, name: str) -> "LogTimer":
        return LogTimer(self, name)

    def inc(self, name, amount=1):
        if name in self.attributes:
            self.attributes[name] = self.attributes[name] + amount
        else:
            self.attributes[name] = amount

    def inc_timer(self, name, time_ms):
        self.inc(name + "_ms", time_ms)
        self.inc(name + "_cnt")

    def record_exception(self, exc):
        self.set(fault=1, error_message=str(exc))

    def as_data(self) -> Dict[str, Union[str, int, float, bool]]:
        return self.attributes

    def _remember_timer(self, timer):
        self.running_timers.add(timer)

    def _forget_timer(self, timer):
        if timer in self.running_timers:
            self.running_timers.remove(timer)

    def _terminate_running_timers(self) -> None:
        for timer in list(self.running_timers):
            timer.finish()

    def __enter__(self) -> "LogRecord":
        return self

    def __exit__(self, type: None, value: None, tb: None) -> None:
        if value:
            self.record_exception(value)
        self.finish()


class NullRecord(LogRecord):
    """A dummy log record that doesn't do anything.

    Will be returned if we don't have a default record.
    """

    def __init__(self, **kwargs) -> None:
        pass

    def finish(self) -> None:
        pass

    def set(self, **kwargs):
        pass

    def _remember_timer(self, _: "LogTimer") -> None:
        pass

    def _forget_timer(self, _: "LogTimer") -> None:
        pass

    def _terminate_running_timers(self):
        pass

    def inc_timer(self, _: str, _2: int) -> None:
        pass

    def inc(self, name: str, amount: int = 1) -> None:
        pass

    def as_data(self):
        return {}

    def record_exception(self, exc):
        self.set(fault=1, error_message=str(exc))


THREAD_LOCAL = threading.local()
THREAD_LOCAL.current_log_record = NullRecord()


def begin_global_log_record(**kwargs) -> None:
    """Open a new global log record with the given attributes."""
    THREAD_LOCAL.current_log_record = LogRecord(**kwargs)


def read_global_log_record():
    """Read the current global log record."""
    return THREAD_LOCAL.current_log_record.as_data()


def finish_global_log_record(exc: None = None) -> Union[LogRecord, NullRecord]:
    """Finish the global log record, and return it."""
    try:
        # When developing, this can sometimes get called before 'current_log_record' has been set.
        if hasattr(THREAD_LOCAL, "current_log_record"):
            record = THREAD_LOCAL.current_log_record
            if exc:
                record.record_exception(exc)
            record.finish()
            return record
        return NullRecord()
    finally:
        THREAD_LOCAL.current_log_record = NullRecord()


def log_value(**kwargs) -> None:
    """Log values into the currently globally active Log Record."""
    if hasattr(THREAD_LOCAL, "current_log_record"):
        # For some malformed URLs, the records are not initialized,
        # so we check whether there's a current_log_record
        THREAD_LOCAL.current_log_record.set(**kwargs)


def log_time(name: str) -> "LogTimer":
    """Log a time into the currently globally active Log Record."""
    return THREAD_LOCAL.current_log_record.timer(name)


def log_counter(name: str, count: int = 1) -> None:
    """Increase the count of something in the currently globally active Log Record."""
    return THREAD_LOCAL.current_log_record.inc(name, count)


def timed(fn: Callable) -> Callable:
    """Function decorator to make the given function timed into the currently active log record."""

    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        with log_time(fn.__name__):
            return fn(*args, **kwargs)

    return wrapped


def timed_as(name: str) -> Callable:
    """Function decorator to make the given function timed into the currently active log record.

    Use a different name from the actual function name.
    """

    def decoractor(fn):
        @functools.wraps(fn)
        def wrapped(*args, **kwargs):
            with log_time(name):
                return fn(*args, **kwargs)

        return wrapped

    return decoractor


def emergency_shutdown() -> None:
    """The process is being killed. Do whatever needs to be done to save the logs."""
    THREAD_LOCAL.current_log_record.set(terminated=True)
    THREAD_LOCAL.current_log_record.finish()
    LOG_QUEUE.emergency_save_to_disk()


def dtfmt(timestamp: float) -> str:
    dt = datetime.datetime.utcfromtimestamp(timestamp)
    return dt.isoformat() + "Z"


class LogTimer:
    """A quick and dirty timer."""

    def __init__(self, record: NullRecord, name: str) -> None:
        self.record = record
        self.name = name
        self.running = False

    def finish(self) -> None:
        if self.running:
            delta = ms_from_fsec(time.time() - self.start)
            self.record.inc_timer(self.name, delta)
            self.record._forget_timer(self)
            self.running = False

    def __enter__(self) -> None:
        self.record._remember_timer(self)
        self.start = time.time()
        self.running = True

    def __exit__(self, type: None, value: None, tb: None) -> None:
        self.finish()


def ms_from_fsec(x: float) -> int:
    """Milliseconds from fractional seconds."""
    return int(x * 1000)


LOG_QUEUE = log_queue.LogQueue("querylog", batch_window_s=300)
LOG_QUEUE.try_load_emergency_saves()
