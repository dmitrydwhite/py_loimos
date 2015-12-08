#!/usr/bin/python

import json

import random
from random import randint
from random import shuffle

"The central operation of each game instance"
class GameSpace:
  MAX_OUTBREAKS = 7
  NUMBER_OF_DISEASES = 4
  DISEASE_COLORS = ["yellow", "red", "blue", "gray"]
  DISEASE_CUBES = 24
  STARTING_STATION = "ATLANTA"

  "initialize GameSpace values"
  def __init__(self):
    # self.values = {}

    config = self.init_user_interface()

    self.cities = self.cities()
    self.diseases = self.init_diseases(config)
    self.players = self.init_players(config['players'])
    self.outbreak_counter = self.init_outbreak_counter(config);
    self.player_dex = self.init_player_deck()
    self.infection_dex = self.init_infection_deck()
    self.infected_cities = []

    self.setup_game()
    self.start_game()

  ## Begin the Game ##
  
  def setup_game(self):
    pass
  
  def start_game(self):
    pass

  ## Primary GameSpace Initializing Methods ##
  
  def init_user_interface(self):
    # Needs to return an object with the following expectations:
    #   {
    #     players: 3        // Number indicating number of players, for random assignment
    #       "OR"
    #     players: {        // Object with 0-indexed numbers as keys, and valid *ID*'s as values
    #       "0": "SCIENCE",
    #       "1": "MEDICAL",
    #       "2": "DISPATCH"
    #     }
    #     outbreak_counter: {
    #       outbreaks: 0      // Number indicating the starting number of outbreaks
    #       max_outbreaks: 7  // Number indicating the last safe count of outbreaks
    #     }
    #   }
    config = {
      # "diseases": {},
      # "players": ["SCIENCE", "MEDICAL"],
      "players": 4,
      "outbreak_counter": {}
    }
    return config

  "Initialize Players"
  def init_players(self, config):
    player_set = config
    game_players = {}

    with open("classic_players.json") as plyers:
      player_json = json.load(plyers)
      players = player_json["players"]

    if type(config) is int:
      player_set = random.sample(players, config)

    for player in player_set:
      game_players[player] = Player(players[player], len(self.diseases))

    return game_players

  "Initialize the outbreak counter"
  def init_outbreak_counter(self, config):
    if "outbreak_counter" in config:
      counter = config["outbreak_counter"]
    else:
      counter = {
        "outbreaks": 0,
        "maximum": self.MAX_OUTBREAKS
      }

    return counter

  def init_player_deck(self):
    pass

  def init_infection_deck(self):
    infection_dex = random.sample(self.cities, len(self.cities))
    return infection_dex

  def init_diseases(self, config):
    if 'diseases' in config:
      num_diseases = config['diseases']
    else:
      num_diseases = self.NUMBER_OF_DISEASES

    diseases = {}
    disease_names = self.generate_disease_names(num_diseases)

    for idx, dizeez in enumerate(disease_names):
      diseases[idx] = {
        "name": dizeez,
        "cubes_left": self.DISEASE_CUBES,
        "color": self.DISEASE_COLORS[idx],
        "cured": False
      }

    return diseases

  "Initialize all the playable cities for this board"
  def cities(self):
    cits = {}

    with open("classic_board.json") as board:
      dat = json.load(board)

    for civitas in dat["cities"]:
      cits[civitas["name"]] = civitas

    return cits

  ## Gameplay Methods ##
  
  def move_p(self, player, location):
    pass

  def transfer_research(self, player1, player2, research):
    pass

  def treat(self, location, disease):
    pass

  def cure(self, disease):
    pass

  ## Helper Functions ##
  
  def generate_disease_names(self, diseases):
    i = 0
    name_array = []
    prefix_array = ['CALO', 'BALACO', 'ANIRI', 'AGIRO', 'XYLO', 'PHYLI', 'RHHEA']
    suffix_array = ['GEA', 'GINA', 'TOSIS', 'SPORADIA', 'TITIS', 'MYDIA', 'COLIDYS', 'PRASEA']

    if not type(diseases) is int:
      diseases = 0
    
    while i < diseases:
      prefix = randint(0, len(prefix_array)-1)
      suffix = randint(0, len(suffix_array)-1)
      new_name = prefix_array[prefix] + suffix_array[suffix]
      if new_name not in name_array:
        name_array.append(new_name)
        i += 1

    return name_array

"The model for a game's player"
class Player:

  DEFAULT_ATTRIBUTES = {
    "solve": 5,
    "treat": 1,
    "treat_all_on_enter": False,
    "build_here": False,
    "fly_from_station": False,
    "transfer_any": False,
    "send_others": False,
    "re_apply_grant": False,
    "protect_connected_cities": False
  }

  disease = {}

  def __init__(self, config, diseases, values=None):
    if values is None:
      self.values = {}
    else:
      self.values = values

    self.set_attributes(config)
    self.set_treatment_ability(diseases)

  def set_attributes(self, config):
    for attribute in self.DEFAULT_ATTRIBUTES.keys():
      if attribute in config:
        self[attribute] = config[attribute]
      else:
        self[attribute] = self.DEFAULT_ATTRIBUTES[attribute]

  def set_treatment_ability(self, diseases):
    for idx in range(diseases):
      self.disease[idx] = {
        "treat": self['treat'],
        "solve": self['solve']
      }

  def __setitem__(self, key, value):
    self.values[key] = value

  def __getitem__(self, key):
    return self.values[key]


L = GameSpace()

print(L)
print(L.players)
print(L.infection_dex)