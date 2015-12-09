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

  infection_rate = 2
  game_status = 0
  one_quiet_night = False

  "initialize GameSpace values"
  def __init__(self):
    # self.values = {}

    self.inter = Loimos_Interface(self)
    
    config = self.inter.get_config()

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
    turn_order = random.sample(self.players, len(self.players))
    print(turn_order)
    while self.game_status == 0:
      for player in turn_order:
        for city in self.infected_cities:
          print(self.cities[city])

        self.inter.take_player_turn(self.players[player])
        self.draw_player_cards(self.players[player])
        self.inter.offer_grant()
        self.advance_game(self.one_quiet_night)

  ## Primary GameSpace Initializing Methods ##

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
      game_players[player] = Player(players[player], len(self.diseases), player)

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
        self.diseases[disease]["cubes_left"] -= rate
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

  def treat(self, location, disease, cubes):
    starting_cubes = self.cities[location]["infections"][disease]

    if starting_cubes < cubes:
      cubes = starting_cubes

    self.cities[location]["infections"][disease] -= cubes
    self.diseases[disease]["cubes_left"] += cubes

  def cure(self, disease):
    pass

  def build_station(self, location):
    self.cities[location]["has_station"] = True

  def quarantine_surrounding(self, location, protect):
    for city in self.cities[location]["connections"]:
        self.cities[city]["is_quarantined"] = protect
    self.cities[location]["is_quarantined"] = protect

  def draw_player_cards(self, player):
    pass

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
    self.infected_cities.append(new_location)
    random.shuffle(self.infected_cities)
    re_stacked_deck = self.infected_cities + self.infection_dex
    self.infection_dex = re_stacked_deck

  def infect(self, city_name, cubes, disease):
    if cubes is None:
      cubes = 1

    if "is_quarantined" in self.cities[city_name] and self.cities[city_name]["is_quarantined"] == True:
      return

    if not "infectinons" in self.cities[city_name]:
      self.cities[city_name]["infections"] = {}

    if disease is None:
      print("disease is None")
      infecting_disease = self.cities[city_name]["group"]
    else:
      infecting_disease = disease

    if not infecting_disease in self.cities[city_name]["infections"]:
      self.cities[city_name]["infections"][infecting_disease] = 0

    self.cities[city_name]["infections"][infecting_disease] += cubes
    self.diseases[infecting_disease]["cubes_left"] -= cubes

    if self.diseases[infecting_disease]["cubes_left"] <= 0:
      self.set_game_status(1)

    if self.cities[city_name]["infections"][infecting_disease] > 3:
      self.outbreak_from(city_name, infecting_disease)

  def outbreak_from(self, origin_city, disease):
    self.outbreak_counter["outbreaks"] += 1

    if self.outbreak_counter["outbreaks"] > self.outbreak_counter["maximum"]:
      self.set_game_status(1)

    for city_name in self.cities[origin_city]["connections"]:
      self.infect(city_name, 1, disease)

  def advance_game(self, one_quiet_night):
    if one_quiet_night == True:
      return
    else:
      self.infect_cities()

  def infect_cities(self):
    for count in range(1, self.infection_rate):
      next_city = self.infection_dex[0]
      self.infect(next_city, None, None)
      self.infected_cities.append(next_city)
      del self.infection_dex[0]

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

  ## State Setters ##
  
  def set_game_status(self, status_code):
    self.game_status = status_code

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
    # "disease": {}
  }


  def __init__(self, config, diseases, group_name, values=None):
    if values is None:
      self.values = {}
    else:
      self.values = values

    print("config", config)
    self.set_attributes(config, diseases, group_name)
    # self.set_treatment_ability(diseases)

    # print(self["disease"])

  def set_attributes(self, config, diseases, group_name):
    self["group"] = group_name

    for attribute in self.DEFAULT_ATTRIBUTES.keys():
      if attribute in config:
        self[attribute] = config[attribute]
      else:
        self[attribute] = self.DEFAULT_ATTRIBUTES[attribute]

    # for idx in range(diseases):
    #   self["disease"][idx] = {
    #     "treat": self["treat"],
    #     "solve": self["solve"]
    #   }

  # def set_treatment_ability(self, diseases):
  #   for idx in range(diseases):
  #     self.disease[idx] = {
  #       "treat": self['treat'],
  #       "solve": self['solve']
  #     }

  def __setitem__(self, key, value):
    self.values[key] = value

  def __getitem__(self, key):
    return self.values[key]


class Loimos_Interface:

  def __init__(self, gameObj, values=None):
    if values is None:
      self.values = {}
    else:
      self.values = values

    self.players = self.init_players()

    self.options = self.init_options()
    self.L = gameObj

  def get_config(self):
    config = {
      "players": self.players
    }

    return config

  def init_players(self):
    player_num = 0
    player_list = []

    select_at_random = raw_input("Choose players at random? (Y/N) ")
    if select_at_random.upper() == "Y":
      player_num = int(raw_input("How many players? "))
    elif select_at_random.upper() == "N":
      add_player = True
      while add_player == True:
        next_player = raw_input("Select Role: ").upper()
        if next_player not in ["SCIENCE", "MEDICAL", "OPERATIONS", "RESEARCH", "PLANNING", "DISPATCH", "QUARANTINE"]:
          print("Not a valid player Role.")
          continue
        else:
          player_num += 1
          player_list.append(next_player)
          if player_num >= 2:
            add_more = raw_input("Add another player?(Y/N) ").upper()
            if add_more == "N":
              add_player = False

    print(player_list)
    if len(player_list) > 0:
      return player_list
    else:
      return player_num

  def init_options(self):
    pass

  def offer_grant(self):
    print("Does any team wish to submit a grant?")

  def take_player_turn(self, player):
    turn_active = 0
    actions_rem = 4

    while turn_active == 0:
      self.prompt_action(player)
      actions_rem -= 1
      if actions_rem == 0:
        turn_active = 1

  def prompt_action(self, player):
    input_status = 0
    commands = {
      "collab": self.collaborate,
      "treat": self.treat,
      "cure": self.cure,
      "ride": self.ride_or_ferry,
      "book": self.book_a_flight,
      "shuttle": self.shuttle,
      "station": self.construct_station,
      "review": self.review,
      "status": self.status,
      "apply": self.apply_grant,
      "xm": self.transmit,
      "dispatch": self.dispatch_other_player,
      "reapply": self.re_apply_grant
    }
    print(player["group"])
    while input_status == 0:
      raw_text = raw_input(player["group"] + "@" + player["location"] + "}>")

      cmd = raw_text.split(' ', 1)
      if len(cmd) > 1:
        args = cmd[1]
      else:
        args = None

      if cmd[0] in commands:
        called_method = commands[cmd[0]]
        called_method(args, player)
        input_status = 1
      else:
        print("Command not recognized by L.O.I.M.O.System")

  def collaborate(self, args, player):
    print("Collaborating")

  def treat(self, args, player):
    print(player["group"])
    if args != None:
      args = args.lower()
    
    treatment_loc = player["location"]
    
    if "infections" in self.L.cities[treatment_loc]:
      treatment_infections = self.L.cities[treatment_loc]["infections"]
    else:
      treatment_infections = {}
    
    game_diseases = self.L.diseases
    
    disease_to_treat = None

    if len(treatment_infections) == 0:
      disease_to_treat = None
    else:
      for disease in treatment_infections:
        if treatment_infections[disease] != 0:
          disease_to_treat = disease
          break

    if disease_to_treat == None:
      print("no diseases suitable for treatment at this location")
      return

    if len(treatment_infections) > 1:
      multi_diseases = True
    else:
      multi_diseases = False

    if args != None:
      # Let's check the args submitted to see if they match any of the diseases in this city
      args_match = False
      for disease in treatment_infections:
        # First check if they submitted a number
        if args == disease:
          args_match = True
          disease_to_treat = disease
          break
        
        # Then check if they typed the color exactly
        if args == game_diseases[disease]["color"]:
          args_match == True
          break

        # Then check if the first three letters of their string match the first three letters of the color
        if args[0:3] == game_diseases[disease]["color"][0:3]:
          args_match = True
          disease_to_treat = disease
          break

        # Then check if maybe they tried to type the name of the disease
        if args[0:7].lower() == game_diseases[disease]["name"][0:7].lower():
          args_match = True
          disease_to_treat = disease
          break

        print("treatment plan instructions not understood")


    if multi_diseases == True and args == None:
      print("specify disease for treatment plan review")
      return

    if game_diseases[disease_to_treat]["cured"] == True:
      treatment_level = 3
    else:
      treatment_level = player["treat"]

    if multi_diseases == True and args_match:
      self.L.treat(treatment_loc, disease_to_treat, treatment_level)

    if not multi_diseases:
      for key in treatment_infections:
        self.L.treat(treatment_loc, key, treatment_level)

  def cure(self, args, player):
    pass

  def ride_or_ferry(self, args, player):
    args = args.upper()

    self.L.move_p(player, args)


  def book_a_flight(self, args, player):
    pass

  def shuttle(self, args, player):
    pass

  def construct_station(self, args, player):
    pass

  def review(self, args, player):
    pass

  def status(self, args, player):
    pass

  def apply_grant(self, args, player):
    pass

  def transmit(self, args, player):
    pass

  def dispatch_other_player(self, args, player):
    pass

  def re_apply_grant(self, args, player):
    pass

  def __setitem__(self, key, value):
    self.values[key] = value

  def __getitem__(self, key):
    return self.values[key]





L = GameSpace()
print(L.infected_cities)
print(L.player_dex)

for player in L.players:
  print(player, L.players[player]["research"])

for disease in L.diseases:
  print(L.diseases[disease]["name"], L.diseases[disease]["cubes_left"])

