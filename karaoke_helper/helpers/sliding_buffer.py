import numpy as np


class SlidingBuffer:
    """
    Circular buffer that can always return a continuous numpy array without copy.
    The getter returns the last `window_size` elements (with zeros if no value has been set).
    """

    def __init__(self, window_size: int, frame_size: int, buffer_size: int):
        self.window_size = window_size
        self.frame_size = frame_size
        self.buffer_size = buffer_size
        self.buffer = np.zeros((self.buffer_size, frame_size))
        self.last_write = self.window_size
        assert (self.buffer_size >= self.window_size * 2)

    def add(self, values: np.ndarray):
        values = values[-self.window_size:]
        added_size = len(values)

        if self.last_write + added_size > self.buffer_size:
            old_buffer = self.get()
            self.buffer[0:self.window_size] = old_buffer
            self.last_write = self.window_size

        self.buffer[self.last_write:self.last_write + added_size] = values
        self.last_write += added_size

    def get(self) -> np.ndarray:
        end = self.last_write
        start = end - self.window_size
        return self.buffer[start:end]
