import numpy as np

def add_single_waterbody(water_type: str,
                         water_size: int,
                         map: np.ndarray,
                         rng: np.random.RandomState):
    """Add a single type of waterbody to the map, by calling corresponding water functions.

    Args
        water_type: type of water body to add.
        water_size: size of water body, in mega pixel.
        map: a pointer to map array.
        rng: RandomState instance that is used as RNG.
    """
    if water_type == "no water":
        return
    if water_type == "river":
        add_river(water_size, map, rng)
    elif water_type == "sea side":
        add_seaside(water_size, map, rng)
    elif water_type == "lake":
        add_lake(water_size, map, rng)
    else:
        raise NotImplementedError(f"Unknown water type: {water_type}")


def add_river(water_size: int, map: np.ndarray, rng: np.random.RandomState):
    """Add a river to the map. A river starts at one of four sides of the map, travese to another side
    """
    width, height = map.shape
    start_side, end_side = rng.choice(["left", "top", "right", "bottom"], size=2, replace=False)
    
    
    # TODO
    return

def add_seaside(water_size: int, map: np.ndarray, rng: np.random.RandomState):
    """Add a seaside to map. Takes up one of the four sides on map.
    """
    width, height = map.shape
    # TODO
    return

def add_lake(water_size: int, map: np.ndarray, rng: np.random.RandomState):
    """Add a lake to the map, a single water body occupying given water_size of mega pixels.
    """
    width, height = map.shape
    # TODO
    return