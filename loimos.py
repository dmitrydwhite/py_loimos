#!/usr/bin/python

import json

import random
from random import randint
from random import shuffle

"The central operation of each game instance"
class GameSpace:
  MAX_OUTBREAKS = 7
  NUMBER_OF_DISEASES = 4
  NUMBER_OF_EPIDEMICS = 4
  DISEASE_COLORS = ["yellow", "red", "blue", "gray"]
  DISEASE_CUBES = 24
  STARTING_STATION = "ATLANTA"
  INFECTION_RATE_INCREMENT = 1
  game_status = 0

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
    self.play_game()

  ## Begin the Game ##
  
  def setup_game(self):
    self.build_station(self.STARTING_STATION)
    self.create_the_emergency()
    for player in self.players:
      self.move_p(self.players[player], self.players[player]["location"])
    self.deal_cards()
    self.insert_epidemics()

  def play_game(self):
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
    stack = len(self.cities)
    player_deck = random.sample(self.cities, stack)

    with open("classic_events.json") as events:
      grants_json = json.load(events)
      grants = grants_json["events"]

    player_deck += grants

    random.shuffle(player_deck)

    return player_deck

  def deal_cards(self):
    num_map = [0, 4, 4, 3, 2, 1, 1, 1]
    starting_cards = num_map[len(self.players)]

    for player in self.players:
      self.players[player]["research"] = self.player_dex[0:starting_cards]
      del self.player_dex[0:starting_cards]

  def insert_epidemics(self):
    stack = len(self.player_dex)
    divisions = stack / self.NUMBER_OF_EPIDEMICS
    stack_start = 0
    stack_end = divisions

    for count in range(1, self.NUMBER_OF_EPIDEMICS):
      epidemic_loc = randint(stack_start, stack_end)
      self.player_dex.insert(epidemic_loc, "EPIDEMIC")
      stack_start += divisions
      stack_end += divisions

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

  """
  This method creates the initial infection state for the starting cities
  """
  def create_the_emergency(self):
    for rate in range(1,4):
      this_round = self.infection_dex[0:3]
      del self.infection_dex[0:3]
      for city in this_round:
        disease = self.cities[city]['group']
        infections = {}
        infections[disease] = rate
        self.cities[city]['infections'] = infections
      self.infected_cities += this_round
      
  ## Gameplay Player Methods ##
  
  def move_p(self, player, location):
    if player["protect_connected_cities"] == True:
      self.quarantine_surrounding(player["location"], False)

    player["location"] = location

    if player["protect_connected_cities"] == True:
      self.quarantine_surrounding(player["location"], True)

    if player["treat_all_on_enter"] == True:
      if "infections" in self.cities[player["location"]]:
        for disease in self.cities[player["location"]]["infections"]:
          if self.diseases[disease]["cured"] == True:
            self.cities[player["location"]]["infections"][disease] = 0


  def transfer_research(self, player1, player2, research):
    pass

  def treat(self, location, disease):
    pass

  def cure(self, disease):
    pass

  def build_station(self, location):
    self.cities[location]["has_station"] = True

  def quarantine_surrounding(self, location, protect):
    for city in self.cities[location]["connections"]:
        self.cities[city]["is_quarantined"] = protect
    self.cities[location]["is_quarantined"] = protect

  ## Gameplay Game Methods ##
  
  def epidemic(self):
    self.increase_rate()
    self.intensify()
    self.infect_cities()

  def increase_rate(self):
    self.infection_rate += self.INFECTION_RATE_INCREMENT

  def intensify(self):
    new_location = self.infection_dex.pop()
    self.infect(new_location, 3)

  def infect(self, city_name, cubes, origin_city):
    if cubes is None:
      cubes = 1

    if self.cities[city_name]["is_quarantined"]:
      return

    if not "infectinons" in self.cities[city_name]:
      self.cities[city_name]["infections"] = {}

    if origin_city is not None:
      infecting_disease = self.cities[origin_city]["group"]
    else:
      infecting_disease = self.cities[city_name]["group"]

    if not infecting_disease in self.cities[city_name]["infections"]:
      self.cities[city_name]["infections"][infecting_disease] = 0

    self.cities[city_name]["infections"][infecting_disease] += cubes

    if self.cities[city_name]["infections"][infecting_disease] > 3:
      self.outbreak_from(city_name, infecting_disease)

  def outbreak_from(self, origin_city, disease):
    self.outbreak_counter["outbreaks"] += 1

    if self.outbreak_counter["outbreaks"] > self.outbreak_counter["maximum"]:
      self.game_status(1)

    for city_name in self.cities[origin_city]["connections"]:
      self.infect(city_name, 1, disease)

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
    "protect_connected_cities": False,
    "location": "ATLANTA"
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
print(L.infected_cities)
print(L.player_dex)

for player in L.players:
  print(player, L.players[player]["research"])