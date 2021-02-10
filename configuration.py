import json
from dataclasses import dataclass

@dataclass
class Config:
    def __init__(self, config: dict):
        self.one_night_chance = config["one_night_chance"]
        self.fertility_rate = config["fertility_rate"]
        self.duel_fatality = config["duel_fatality"]
        self.natural_fatality = config["duel_fatality"]
        self.crowd_threshold = config["crowd_threshold"] 
cfg = Config(json.load(open('config.json', 'r')))