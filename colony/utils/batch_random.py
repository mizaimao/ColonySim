"""Some classes to manage random number generations"""

import numpy as np
from dataclasses import dataclass
from typing import List, Optional, Union


BATCH_SIZE: int = 1000

@dataclass
class BatchRandom:
    """Build random numbers in batch and return single ones.
    Not sure if I should use iterator here."""
    seed: int
    low: Union[float, int]
    high: Union[float, int]

    batch_size: Optional[int] = BATCH_SIZE

    def __post_init__(self):
        """Setup functions."""
        self.int_mode: bool = isinstance(self.low, int)
        assert type(self.low) == type(self.high), "Please don't mix float and integer \
            when puting high and low, otherwise it won't know which type to use."
        self.rng: np.random.RandomState = np.random.RandomState(self.seed)

        # values will be added in _build_new_batch
        self.index: int
        self.queue: np.ndarray
        self._build_new_batch()

    def __len__(self):
        """Batch size."""
        return self.batch_size

    def _build_new_batch(self):
        """Bulid a new batch of random numbers"""
        self.index = 0
        self.queue = self.rng.uniform(
            self.low,
            self.high,
            self.batch_size
        ).astype(np.int if self.int_mode else float)  # float -> float64

    def get(self):
        value: Union[int, float] = self.queue[self.index]
        self.index += 1
        # exhausted, build a new batch
        if self.index == self.batch_size:
            self._build_new_batch()
        return value
