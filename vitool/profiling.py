# -*- coding: utf-8 -*-

import time, logging, contextlib
from functools import wraps



class ArgsResFunc:
	
	def __init__(self, callback=print,
				args_format='{function.__module__}.{function.__qualname__}[{args}, {kwargs}]',
				result_format='{function.__module__}.{function.__qualname__} -> {result}'):
		self.callback = callback
		self.args_format = args_format
		self.result_format = result_format
	
	def __call__(self, function):
		@wraps(function)
		def wrap(*args, **kwargs):
			if self.callback is None:
				return function(*args, **kwargs)
			self.callback( self.args_format.format(function=function, args=args, kwargs=kwargs) )
			result = function(*args, **kwargs)
			self.callback( self.result_format.format(function=function, result=result) )
			return result
		return wrap



class TimeitFunc:
	
	def __init__(self, callback=print, format='{function.__module__}.{function.__qualname__}'):
		self.callback = callback
		self.format = format
		self.function = lambda : None
	
	def __str__(self):
		return self.format.format(function=self.function)

	def __call__(self, function):
		self.function = function
		@wraps(function)
		def wrap(*args, **kwargs):
			with Timeit(self.callback, self) as tm:
				return function(*args, **kwargs)
		return wrap



class Timeit:
	
	def __init__(self, callback=None, target='Target'):
		self.elapsed = 0
		self.callback = callback
		self.target = target
		self.now = time.perf_counter()
	
	def __str__(self):
		return f'{self.target} ran for {self.elapsed*1000:.3f} ms.'
	
	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self.measure()
	
	def measure(self, callback=None):
		now = time.perf_counter()
		self.elapsed = now - self.now
		self.now = now
		if callback is not None:
			callback(self)
		elif self.callback is not None:
			self.callback(self)



class Verbose:
	
	def __init__(self, logger, logging_format=f"%(asctime)s [%(levelname)s:%(name)s] - %(message)s"):
		self.is_controlling = False
		self.logger = logger
		logger_handler = logging.StreamHandler()
		logger_handler.setFormatter( logging.Formatter(logging_format) )
		self.logger.addHandler(logger_handler)
	
	def is_quiet(self):
		return self.logger.getEffectiveLevel() >= logging.WARNING

	def quiet(self, enable):
		value = logging.WARNING if enable else logging.INFO
		return self.level(value)

	@contextlib.contextmanager
	def level(self, value):
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


