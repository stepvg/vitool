# -*- coding: utf-8 -*-

import time
from itertools import islice



def batched(iterable, length, stride=1, start=0, stop=None):
	iterator = islice(iterable, start, stop)
	tail = list(islice(iterator, length))
	while len(tail) == length:
		yield iter(tail)
		tail += islice(iterator, stride)
		del tail[:stride]



class Timer:

	def __init__(self, seconds=0):
		self.event_time = 0
		self.every(seconds)

	def every(self, seconds):
		self.interval = seconds
		if not self.interval:
			self.event_time = 0
			return
		if not self.event_time:
			self.event_time = self.interval + time.perf_counter()

	def disable(self):
		self.every(0)
	
	def __bool__(self):
		return bool(self.interval)

	def on_time(self, callback, *args, **kwargs):
		if not self.interval:
			return
		now = time.perf_counter()
		if now > self.event_time:
			callback(*args, **kwargs)
			self.event_time += self.interval
			if now > self.event_time:
				self.event_time = self.interval + now

