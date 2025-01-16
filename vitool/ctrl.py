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



class Timer:

	def __init__(self, interval=0):
		self.start(interval)

	def start(self, interval):
		self.interval = interval
		self.start = time.perf_counter()

	def stop(self):
		self.interval = 0

	# check
	def on_time(self, callback, *args, **kwargs):
		if not self.interval:
			return
		now = time.perf_counter()
		d = now - self.start
		if d > self.interval:
			self.start = now if d - self.interval > self.interval else (self.start + self.interval)
			callback(*args, **kwargs)

