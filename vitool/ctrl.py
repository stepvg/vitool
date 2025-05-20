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
		self.enabled = False
		self.every(seconds)


	def __bool__(self):
		return self.enabled


	def disable(self):
		self.enabled = False

	
	def alarm(self, event_timestamp):
		self.event_time = event_timestamp
		self.interval = event_timestamp - time.perf_counter()
		self.enabled = True


	def wake_up(self, in_seconds):
		self.event_time = in_seconds + time.perf_counter()
		self.interval = in_seconds
		self.enabled = True


	def every(self, seconds):
		self.interval = seconds
		if not seconds:
			self.enabled = False
			return
		if not self.enabled:
			self.enabled = True
			self.event_time = self.interval + time.perf_counter()


	def on_time(self, callback=None, *args, **kwargs):
		if self.enabled:
			now = time.perf_counter()
			if now > self.event_time:
				if callback is not None:
					callback(*args, **kwargs)
				self.event_time += self.interval
				if now > self.event_time:
					self.event_time = self.interval + now
				return True
				
		return False

