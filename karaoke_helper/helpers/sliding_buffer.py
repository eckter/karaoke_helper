import numpy as np


class SlidingBuffer:
    """
    Circular buffer that can always return a continuous numpy array without copy.
    The getter returns the last `window_size` elements (with zeros if no value has been set).
    Writes are made twice, but we never copy or move chunks of data.
    """

    def __init__(self, window_size: int, frame_size: int):
        self.window_size = window_size
        self.frame_size = frame_size
        self.buffer_size = self.window_size * 2
        self.buffer = np.zeros((self.buffer_size, frame_size))
        self.last_write = 0

    def add(self, values: np.ndarray):
        added_size = len(values)

        def write(start):
            end = start + added_size
            values_start = 0 if start >= 0 else -start
            start = max(0, start)
            end = min(self.buffer_size, end)
            if start >= end:
                return
            values_end = min(added_size, end - start + values_start)
            self.buffer[start:end] = values[values_start:values_end]

        write(self.last_write)
        write(self.last_write - self.window_size)
        write(self.last_write + self.window_size)
        self.last_write = (self.last_write + added_size) % self.buffer_size

    def get(self) -> np.ndarray:
        end = self.last_write
        start = end - self.window_size
        if start < 0:
            start += self.window_size
            end += self.window_size
        return self.buffer[start:end]
