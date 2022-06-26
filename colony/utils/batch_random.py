"""Some classes to manage random number generations"""

import numpy as np
from dataclasses import dataclass
from typing import List, Optional, Union


BATCH_SIZE: int = 5000


@dataclass
class BatchRandom:
    """Template class for batch random numbers.
    Not sure if I should use iterator here."""
    seed: int
    batch_size: Optional[int] = BATCH_SIZE

    def __post_init__(self):
        # values will be added in _build_new_batch
        self.index: int
        self.queue: np.ndarray
        self.rng: np.random.RandomState = np.random.RandomState(self.seed)

    def __len__(self):
        """Batch size."""
        return self.batch_size

    def _build_new_batch(self):
        pass

    def get(self, size: int = 1) -> Union[int, float, np.ndarray]:
        """Retrive a single value from generated stack, and generate a new batch if it runs out."""
        if size > 1:
            return self.get_batch(size)

        value: Union[int, float] = self.queue[self.index]
        self.index += 1
        # exhausted, build a new batch
        if self.index == self.batch_size:
            self._build_new_batch()
        return value

    def get_batch(self, size: int) -> np.ndarray:
        """Get a batch of random numbers."""
        assert size <= self.batch_size * 100, "Requested batch is 100x of batch size, \
            please consider a more efficient way to get random numbers."
        end: int = self.index + size
        # values = front_list + [middle_lists] + leftover_list
        values: List[np.ndarray] = [self.queue[self.index: end]]
        new_size: int = size - len(values[0])
        self.index += len(values[0])
        
        # append middle lists
        for _ in range(int(new_size // self.batch_size)):
            self._build_new_batch()
            values.append(self.queue.copy())
        
        # adjust leftover index and add values
        if self.index == self.batch_size:
            self._build_new_batch()
        leftover: int = new_size % self.batch_size
        assert self.index + leftover < self.batch_size, "Sanity check failed, index bug."
        values.append(self.queue[self.index: self.index + leftover])
        return np.concatenate(values)


@dataclass
class BatchUniform(BatchRandom):
    """Build random numbers in batch and return single ones."""
    low: Union[float, int] = 0
    high: Union[float, int] = 100

    def __post_init__(self):
        """Setup functions."""
        super().__post_init__()
        self.int_mode: bool = isinstance(self.low, int)
        assert type(self.low) == type(self.high), "Please don't mix float and integer \
            when puting high and low, otherwise it won't know which type to use."
        self._build_new_batch()

    def _build_new_batch(self):
        """Bulid a new batch of random numbers"""
        self.index = 0
        self.queue = self.rng.uniform(
            self.low,
            self.high,
            self.batch_size
        ).astype(np.int if self.int_mode else float)  # float -> float64


@dataclass
class BatchNormal(BatchRandom):
    """Batch random numbers from normal distribution."""
    mean: float = 0.
    std: float = 1.

    def __post_init__(self):
        """Setup normal distribution."""
        super().__post_init__()
        self._build_new_batch()

    def _build_new_batch(self):
        self.index = 0
        self.queue = self.rng.normal(self.mean, self.std, self.batch_size)
