# -*- coding: utf-8 -*-

import time
from itertools import islice
import typing as tp


def batched(
		iterable: tp.Iterable[tp.Any],
		length: int,
		stride: int = 1,
		start: int = 0,
		stop: None | int = None
	) -> tp.Generator[tp.Iterator[tp.Any], None, None]:
	"""
	Generate overlapping batches of fixed length from an iterable.

	Args:
		iterable: The input sequence or iterable.
		length: The number of elements in each batch.
		stride: The step size between consecutive batches (default is 1).
		start: The index to start slicing the iterable (default is 0).
		stop: The index to stop slicing the iterable (default is None, meaning no limit).

	Yields:
		An iterator over a batch of elements of size ``length``.
		Batches overlap depending on the ``stride`` value.

	Example:
		>>> print(list(map(tuple, batched(range(10), length=4, stride=2, start=1, stop=10))))
		[(1, 2, 3, 4), (3, 4, 5, 6), (5, 6, 7, 8)]
	"""
	iterator = islice(iterable, start, stop)
	tail = list(islice(iterator, length))
	while len(tail) == length:
		yield iter(tail)
		tail += islice(iterator, stride)
		del tail[:stride]



class Timer:
	"""
	A simple timer class for scheduling periodic or delayed events.

	The timer can be configured to trigger after a given interval,
	or repeatedly at fixed intervals. It provides methods to enable,
	disable, and check if an event is due.
	"""
	
	def __init__(self, seconds: float = 0) -> None:
		"""
		Initialize a new Timer instance.

		Args:
			seconds: The interval in seconds. If 0, the timer is disabled.
		"""
		self.enabled = False
		self.every(seconds)


	def __bool__(self) -> bool:
		"""
		Return whether the timer is currently enabled.

		Returns:
			True if the timer is enabled, False otherwise.
		"""
		return self.enabled


	def disable(self) -> None:
		"""
		Disable the timer.
		"""
		self.enabled = False

	
	def alarm(self, event_timestamp: float) -> None:
		"""
		Set the timer to trigger at a specific timestamp.

		Args:
			event_timestamp: The absolute time (from ``time.perf_counter``) when the event should occur.
		"""
		self.event_time = event_timestamp
		self.interval = event_timestamp - time.perf_counter()
		self.enabled = True


	def wake_up(self, in_seconds: float) -> None:
		"""
		Set the timer to trigger after a given delay.

		Args:
			in_seconds: Delay in seconds before the timer event triggers.
		"""
		self.event_time = in_seconds + time.perf_counter()
		self.interval = in_seconds
		self.enabled = True


	def every(self, seconds: float) -> None:
		"""
		Configure the timer to trigger periodically at a given interval.

		Args:
			seconds: Interval in seconds between events. If 0, disables the timer.
		"""
		self.interval = seconds
		if not seconds:
			self.enabled = False
			return
		if not self.enabled:
			self.enabled = True
			self.event_time = self.interval + time.perf_counter()


	def on_time(
			self,
			callback: None | tp.Callable[..., tp.Any] = None,
			*args: tp.Any,
			**kwargs: tp.Any
		) -> bool:
		"""
		Check if the timer event is due, and execute a callback if provided.

		Args:
			callback: A callable to be executed when the timer event occurs.
			*args: Positional arguments passed to the callback.
			**kwargs: Keyword arguments passed to the callback.

		Returns:
			True if the event was triggered, False otherwise.
		"""
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

