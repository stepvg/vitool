# -*- coding: utf-8 -*-

import time, logging, contextlib
from functools import wraps
import types, typing as tp



class ArgsResFunc:
	"""A decorator that logs function arguments and results.

	This decorator formats function arguments and return values
	using the provided templates and outputs them through a callback.
	"""

	def __init__(
		self,
		callback: None | tp.Callable[[str], None] = print,
		args_format: str = '{function.__module__}.{function.__qualname__}[{args}, {kwargs}]',
		result_format: str = '{function.__module__}.{function.__qualname__} -> {result}'
		) -> None:
		"""
		Initialize ArgsResFunc.
		
		Args:
			callback: Function to output formatted logs. Defaults to ``print``.
			args_format: Format string for function arguments.
			result_format: Format string for function result.
		"""
		self.callback = callback
		self.args_format = args_format
		self.result_format = result_format

	
	def __call__(self, function: tp.Callable[..., tp.Any]) -> tp.Callable[..., tp.Any]:
		"""
		Wrap the target function with logging.

		Args:
			function: Function to wrap.

		Returns:
			Wrapped function with logging of arguments and results.
		"""
		@wraps(function)
		def wrap(*args: tp.Any, **kwargs: tp.Any) -> tp.Any:
			if self.callback is None:
				return function(*args, **kwargs)
			self.callback( self.args_format.format(function=function, args=args, kwargs=kwargs) )
			result = function(*args, **kwargs)
			self.callback( self.result_format.format(function=function, result=result) )
			return result
		return wrap



class TimeitFunc:
	"""Decorator class to measure execution time of functions."""
	
	def __init__(
			self,
			callback: None | tp.Callable[['Timeit'], None] = print,
			format: str = '{function.__module__}.{function.__qualname__}',
			timeit_format: str = '{self.target} ran for {self.elapsed_ms:.3f} ms.'
		) -> None:
		"""
		Initialize TimeitFunc.

		Args:
			callback: Function to process log messages.
			format: Format string for the decorated function name.
			timeit_format: Format string for timing results.
		"""
		self.format = format
		self.function = lambda : None
		self.timeit = Timeit(callback, self, timeit_format)

	def __str__(self) -> str:
		"""Return formatted representation of the wrapped function."""
		return self.format.format(function=self.function)

	def __call__(self, function: tp.Callable[..., tp.Any]) -> tp.Callable[..., tp.Any]:
		"""
		Wrap the target function to measure execution time.

		Args:
			function: Function to wrap.

		Returns:
			Wrapped function with timing.
		"""
		self.function = function
		@wraps(function)
		def wrap(*args: tp.Any, **kwargs: tp.Any) -> tp.Any:
			with self.timeit:
				return function(*args, **kwargs)
		return wrap



class Timeit:
	"""Context manager to measure elapsed execution time."""
	
	def __init__(
			self,
			callback: None | tp.Callable[['Timeit'], None] = None,
			target: tp.Any = 'Target',
			format: str = '{self.target} ran for {self.elapsed_ms:.3f} ms.'
		) -> None:
		"""
		Initialize Timeit.

		Args:
			callback: Function to process timing results.
			target: Identifier for the measured target.
			format: Format string for timing results.
		"""
		self.elapsed = 0
		self.callback = callback
		self.target = target
		self.format = format
		self.now = time.perf_counter()
	
	
	@property
	def elapsed_ms(self) -> float:
		"""Return elapsed time in milliseconds."""
		return self.elapsed * 1000


	def __str__(self) -> str:
		"""Return formatted timing string."""
		return self.format.format(self=self)

	
	def __enter__(self) -> 'Timeit':
		"""Start timing."""
		self.now = time.perf_counter()
		return self


	def __exit__(
			self,
			exc_type: None | type[BaseException],
			exc_value: None | BaseException,
			traceback: None | types.TracebackType
		) -> None:
		"""Stop timing when leaving the context."""
		self.measure()
	
	
	def measure(self, callback: None | tp.Callable[['Timeit'], None] = None) -> None:
		"""
		Measure elapsed time and optionally invoke a callback.

		Args:
			callback: Optional function to process the timing result.
		"""
		now = time.perf_counter()
		self.elapsed = now - self.now
		self.now = now
		if callback is not None:
			callback(self)
		elif self.callback is not None:
			self.callback(self)



class Verbose:
	"""Helper class to control logging verbosity."""
	
	def __init__(
			self,
			logger: logging.Logger,
			logging_format: str = "%(asctime)s [%(levelname)s:%(name)s] - %(message)s"
		) -> None:
		"""
		Initialize Verbose.

		Args:
			logger: Logger instance to control.
			logging_format: Format string for log messages.
		"""
		self.is_controlling = False
		self.logger = logger
		logger_handler = logging.StreamHandler()
		logger_handler.setFormatter( logging.Formatter(logging_format) )
		self.logger.addHandler(logger_handler)
	
	
	def is_quiet(self) -> bool:
		"""
		Check if the logger is in quiet mode.

		Returns:
			True if log level is >= WARNING, False otherwise.
		"""
		return self.logger.getEffectiveLevel() >= logging.WARNING


	def quiet(self, enable: bool) -> tp.ContextManager[None]:
		"""
		Temporarily set logger to quiet (WARNING) or verbose (INFO).

		Args:
			enable: If True, sets logger to WARNING; otherwise sets to INFO.

		Returns:
			Context manager controlling log level.
		"""
		value = logging.WARNING if enable else logging.INFO
		return self.level(value)


	@contextlib.contextmanager
	def level(self, value: int) -> tp.Generator[None, None, None]:
		"""
		Temporarily set the logging level.

		Args:
			value: New logging level.

		Yields:
			Control back to the caller.
		"""
		if self.is_controlling:				# Someone is controlling the logger
			yield						# Don't control the logger now
			return
		try:
			self.is_controlling = True
			old_level = self.logger.getEffectiveLevel()
			self.logger.setLevel(value)
			yield
		finally:
			self.logger.setLevel(old_level)
			self.is_controlling = False


