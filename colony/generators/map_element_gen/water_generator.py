import numpy as np

def add_single_waterbody(water_type: str,
                         water_size: int,
                         map: np.ndarray,
                         rng: np.random.RandomState):
    if water_type == "no water":
        return
    if water_type == "river":
        return
    elif water_type == "sea side":
        return
    elif water_type == "lake":
        return
    else:
        raise NotImplementedError(f"Unknown water type: {water_type}")