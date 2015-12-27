#!/usr/bin/python

# Import JSON
import json

# Import random and some specific Modules
import random
from random import randint
from random import shuffle

# Import Loimos Classes
from Loimos_Player import Player as Player
from Loimos_Controller import Loimos_Controller as Controller
from Loimos_Events import Card_Events as Grants

"The central operation of each game instance"
class GameSpace:
  MAX_OUTBREAKS = 7
  NUMBER_OF_DISEASES = 4
  NUMBER_OF_EPIDEMICS = 5
  DISEASE_COLORS = ["yellow", "red", "blue", "gray"]
  DISEASE_CUBES = 24
  STARTING_STATION = "ATLANTA"
  INFECTION_RATE_INCREMENT = 1

  infection_rate = 2
  game_status = 0
  one_quiet_night = False
  outbreak_chain = []

  "initialize GameSpace values"
  def __init__(self):
    # self.values = {}

    self.inter = Controller(self)
    self.grants = Grants(self.inter.view)
    
    config = self.inter.get_config()

    self.cities = self.cities()
    self.diseases = self.init_diseases(config)
    self.players = self.init_players(config['players'])
    self.events = self.grants._provide_events()
    self.outbreak_counter = self.init_outbreak_counter(config);
    self.player_dex = self.init_player_deck()
    self.infection_dex = self.init_infection_deck()
    self.infected_cities = []
    self.player_discard = []
    self.cities_with_stations = []

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
    turn_order = random.sample(list(self.players), len(self.players))
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
      player_set = random.sample(list(players), config)

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
    player_deck = random.sample(list(self.cities), stack)

    player_deck += self.events

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
    divisions = int(stack / self.NUMBER_OF_EPIDEMICS)
    new_dex = []
    stack_start = 0
    stack_end = divisions

    for count in range(self.NUMBER_OF_EPIDEMICS):
      this_stack = self.player_dex[stack_start:stack_end]
      epidemic_loc = randint(0, divisions)
      this_stack.insert(epidemic_loc, "EPIDEMIC")
      new_dex += this_stack
      stack_start += divisions
      stack_end += divisions

    self.player_dex = new_dex
    print(self.player_dex)

  def init_infection_deck(self):
    infection_dex = random.sample(list(self.cities), len(self.cities))
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
        "cured": False,
        "eradicated": False
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

  def discard(self, player, discard):
    player["research"].remove(discard)

    self.player_discard += discard

  def treat(self, location, disease, cubes):
    starting_cubes = self.cities[location]["infections"][disease]

    if starting_cubes < cubes:
      cubes = starting_cubes

    self.cities[location]["infections"][disease] -= cubes
    self.diseases[disease]["cubes_left"] += cubes

  def cure(self, disease):
    all_cured = True
    self.diseases[disease]["cured"] = True
    for dx in self.diseases:
      if self.diseases[dx]["cured"] == False:
        all_cured = False

    if all_cured == True:
      self.set_game_status(1)


  def build_station(self, location):
    self.cities[location]["has_station"] = True
    self.cities_with_stations.append(location)

  def quarantine_surrounding(self, location, protect):
    for city in self.cities[location]["connections"]:
        self.cities[city]["is_quarantined"] = protect
    self.cities[location]["is_quarantined"] = protect

  def draw_player_cards(self, player):
    print(self.player_dex)
    for i in range(0,2):
      next_card = self.player_dex.pop()
      print("%s draws %s" % (player["group"], next_card))
      if len(self.player_dex) == 0:
        self.set_game_status(1)
      if next_card == "EPIDEMIC":
        print("Drew an EPIDEMIC")
        self.epidemic()
      else:
        player["research"].append(next_card)

    if len(player["research"]) > 7:
      for i in range(len(player["research"]) - 7):
        self.inter.require_discard(player)

  ## Gameplay Game Methods ##
  
  def epidemic(self):
    self.increase_rate()
    self.intensify()
    # self.infect_cities()

  def increase_rate(self):
    self.infection_rate += self.INFECTION_RATE_INCREMENT

  def intensify(self):
    new_location = self.infection_dex.pop()
    print("EPIDEMIC reported in %s" % new_location)
    self.infect(new_location, 3, None)
    self.infected_cities.append(new_location)
    random.shuffle(self.infected_cities)
    re_stacked_deck = self.infected_cities + self.infection_dex
    self.infection_dex = re_stacked_deck
    self.infected_cities = []

  def infect(self, city_name, cubes, disease):
    if cubes is None:
      cubes = 1

    print("Cubes %d" % cubes)
    if "is_quarantined" in self.cities[city_name] and self.cities[city_name]["is_quarantined"] == True:
      return

    if disease is None:
      print("disease is None")
      infecting_disease = self.cities[city_name]["group"]
    else:
      infecting_disease = disease

    for player in self.players:
      if self.players[player]["treat_all_on_enter"] == True and self.players[player]["location"] == city_name and self.diseases[infecting_disease]["cured"] == True:
        return

    if "infections" not in self.cities[city_name]:
      self.cities[city_name]["infections"] = {}

    if not infecting_disease in self.cities[city_name]["infections"]:
      self.cities[city_name]["infections"][infecting_disease] = 0

    self.cities[city_name]["infections"][infecting_disease] += cubes
    self.diseases[infecting_disease]["cubes_left"] -= cubes

    if self.diseases[infecting_disease]["cubes_left"] <= 0:
      self.set_game_status(1)

    if self.cities[city_name]["infections"][infecting_disease] > 3:
      self.cities[city_name]["infections"][infecting_disease] = 3
      self.outbreak_from(city_name, infecting_disease)

  def outbreak_from(self, origin_city, disease):
    self.outbreak_chain.append(origin_city)
    did_outbreak = False

    self.outbreak_counter["outbreaks"] += 1

    print("OUTBREAK of %s from %s to %s" % (self.diseases[disease]["name"], origin_city, ', '.join(self.cities[origin_city]["connections"])))

    if self.outbreak_counter["outbreaks"] > self.outbreak_counter["maximum"]:
      self.set_game_status(1)

    print(self.cities[origin_city]["connections"])
    for city_name in self.cities[origin_city]["connections"]:
      if city_name not in self.outbreak_chain:
        print(city_name)
        self.infect(city_name, 1, disease)
        did_outbreak = True

    if did_outbreak == False:
      self.outbreak_chain = []

  def advance_game(self, one_quiet_night):
    if one_quiet_night == True:
      self.one_quiet_night = False
      return
    else:
      self.infect_cities()

  def infect_cities(self):
    for count in range(self.infection_rate):
      next_city = self.infection_dex[0]
      print("Infecting %s" % next_city)
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







L = GameSpace()
print(L.infected_cities)
print(L.player_dex)

for player in L.players:
  print(player, L.players[player]["research"])

for disease in L.diseases:
  print(L.diseases[disease]["name"], L.diseases[disease]["cubes_left"])

