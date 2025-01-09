# -*- coding: utf-8 -*-

import time, logging, contextlib
from itertools import islice


def batched(iterable, length, stride=1, start=0, stop=None):
	iterator = islice(iterable, start, stop)
	tail = list(islice(iterator, length))
	while len(tail) == length:
		yield iter(tail)
		tail += islice(iterator, stride)
		del tail[:stride]



class Timeit:
	
	def __init__(self, callback=None):
		self.callback = callback
		self.elapsed = 0
		self.start = time.perf_counter()
	
	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self.elapsed = time.perf_counter() - self.start
		if self.callback is None:
			return
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


