import json
from dataclasses import dataclass

@dataclass
class Config:
    def __init__(self, config: dict):
        """
        Configuration class
        
        Attributes:
            one_night_chance {float, inclusively between 0 and 1} -- chance of 
                mating when two opposite sex meet
            fertility_rate {float, non-negative)} -- currently not implemented 
            duel_fatality {floate, inclusively between 0 and 1} --
                chance of death when two spores are meet with the same gender
            natural_fatality {floate, inclusively between 0 and 1} -- 
                currently not implemented
            crowd_threshold {int} -- max number of individuals on the same
                tile, above which famine is induced killing all spores on tile
        """
        self.one_night_chance = config["one_night_chance"]
        self.fertility_rate = config["fertility_rate"]
        self.duel_fatality = config["duel_fatality"]
        self.natural_fatality = config["duel_fatality"]
        self.crowd_threshold = config["crowd_threshold"] 

# objected shared in multiple places
cfg = Config(json.load(open('config.json', 'r')))
