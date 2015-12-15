#!/usr/bin/python

import json

import random
from random import randint
from random import shuffle

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

    self.inter = Loimos_Interface(self)
    
    config = self.inter.get_config()

    self.cities = self.cities()
    self.diseases = self.init_diseases(config)
    self.players = self.init_players(config['players'])
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
    # "treatment_abilities": {}
  }


  def __init__(self, config, diseases, group_name, values=None):
    if values is None:
      self.values = {}
    else:
      self.values = values

    # print("config", config)
    self.set_attributes(config, diseases, group_name)
    self.set_treatment_ability(diseases)

  def set_attributes(self, config, diseases, group_name):
    self["group"] = group_name

    for attribute in self.DEFAULT_ATTRIBUTES.keys():
      if attribute in config:
        self[attribute] = config[attribute]
      else:
        self[attribute] = self.DEFAULT_ATTRIBUTES[attribute]

  def set_treatment_ability(self, diseases):
    # TODO: Set a separate treat / solve value for each individual disease
    # Had problems iterating through the properties
    pass

  def __setitem__(self, key, value):
    self.values[key] = value

  def __getitem__(self, key):
    return self.values[key]

"""
This is the Controller
"""
class Loimos_Interface:
# TODO: Separate Controller functionality from View functionality better

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

    select_at_random = input("Choose players at random? (Y/N) ")
    if select_at_random.upper() == "Y":
      player_num = int(input("How many players? "))
    elif select_at_random.upper() == "N":
      add_player = True
      while add_player == True:
        next_player = input("Select Role: ").upper()
        if next_player not in ["SCIENCE", "MEDICAL", "OPERATIONS", "RESEARCH", "PLANNING", "DISPATCH", "QUARANTINE"]:
          print("Not a valid player Role.")
          continue
        else:
          player_num += 1
          player_list.append(next_player)
          if player_num >= 2:
            add_more = input("Add another player?(Y/N) ").upper()
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

  def require_discard(self, player):
    research = player["research"]

    if len(research) > 7:
      print()
      print("MSG::CDC==>@%s.TEAM[You must abandon some of your research or forego a grant to continue]:" % player["group"])
      self.review(self, player)
      abandon = int(input("Select a number to abandon: ")) - 1

      if abandon in range(len(research)):
        print("abandoning %s" % research[abandon])
        print()
        self.L.discard(player, research[abandon])
      else:
        self.require_discard(player)
    else:
      return


  def take_player_turn(self, player):
    turn_active = 0
    actions_rem = 4

    while turn_active == 0:
      actions_rem -= self.prompt_action(player)
      if actions_rem <= 0:
        turn_active = 1

  def prompt_action(self, player):
    input_status = 0
    commands = {
      "collab": self.collaborate,
      "treat": self.treat,  # In a good state as of 12/9
      "cure": self.cure,
      "ride": self.ride_or_ferry,
      "book": self.book_a_flight,
      "shuttle": self.shuttle,
      "station": self.construct_station,
      "review": self.review,
      "status": self.status,
      "cx": self.show_connections,
      "apply": self.apply_grant,
      "xm": self.transmit,
      "dispatch": self.dispatch_other_player,
      "reapply": self.re_apply_grant,
      "skip": self.skip_turn
    }
    while input_status == 0:
      raw_text = input(player["group"] + "@" + player["location"] + "}>")

      cmd = raw_text.split(' ', 1)
      if len(cmd) > 1:
        args = cmd[1]
      else:
        args = None

      if cmd[0] in commands:
        called_method = commands[cmd[0]]
        input_status = called_method(args, player)
      else:
        print("Command not recognized by L.O.I.M.O.System")

      return input_status

  def trade_research(self, l_player, r_player, direction, location):
    if direction == True:
      giving_player = l_player
      receiving_player = r_player
    else:
      giving_player = r_player
      receiving_player = l_player

    print("Transferring research gathered in %s from %s TEAM to %s TEAM" % ())
    giving_player["research"].remove(location)
    receiving_player["research"].append(location)
    if len(receiving_player["research"]) > 7:
      self.require_discard(self, receiving_player)

  def collaborate(self, args, player):
    if args != None:
      args = args.upper()

    game_players = self.L.players
    here = player["location"]
    other_players_here = []
    player_to_trade = None
    research_player = None
    player_giving = True

    for playa in game_players:
      if game_players[playa]["location"] == here and game_players[playa]["group"] != player["group"]:
        other_players_here.append(game_players[playa])

    print(other_players_here)
    if len(other_players_here) == 0:
      print("no other teams in %s to collaborate with" % here)
      return 0
    elif len(other_players_here) == 1:
      player_to_trade = other_players_here[0]
    elif args in other_players_here:
      player_to_trade = game_players[args]
    
    if player_to_trade != None:
      if player["transfer_any"] == True or player_to_trade["transfer_any"] == True:
        if player["transfer_any"] == True:
          research_player = Player
          player_giving = True
        else:
          research_player = player_to_trade
          player_giving = False

        print("Select Research from the %s TEAM to transfer:" % research_player["group"])
        self.review(self, research_player)
        correct_input = 0
        while correct_input == 0:
          research_selection = int(input("Select a number}>")) - 1
          if research_selection in range(len(research_player["research"])):
            self.trade_research(self, player, player_to_trade, player_giving, here)
            correct_input = 1
        return 1

      else:
        if here in player["research"]:
          player_giving = True
        elif here in player_to_trade["research"]:
          player_giving = False
        else:
          player_giving = None

        if player_giving != None:
          self.trade_research(player, player_to_trade, player_giving, here)
          return 1
        else:
          print("No baseline Research data in %s for collaboration" % here)
          return 0

    else:
      print("You must specify a team in this location to collaborate with")
      for team in other_players_here:
        print(team["group"])
      return 0
      



  """
  This Method handles the player treating a disease in the city they are in
  """
  def treat(self, args, player):
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
      return 0

    if len(treatment_infections) > 1:
      multi_diseases = True
    else:
      multi_diseases = False

    if args != None:
      # Let's check the args submitted to see if they match any of the diseases in this city
      args_match = False
      for disease in treatment_infections:
        # First check if they submitted a number
        if args == str(disease):
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

        print("treatment plan instructions not understood or invalid")
        return 0


    if multi_diseases == True and args == None:
      print("specify disease for treatment plan review")
      return 0

    if game_diseases[disease_to_treat]["cured"] == True:
      treatment_level = 3
    else:
      treatment_level = player["treat"]

    if multi_diseases == True and args_match:
      self.L.treat(treatment_loc, disease_to_treat, treatment_level)
      self.show_treatment_success(game_diseases[disease_to_treat]["name"], treatment_loc, treatment_infections[disease_to_treat])
      return 1

    if not multi_diseases:
      for key in treatment_infections:
        self.L.treat(treatment_loc, key, treatment_level)
        self.show_treatment_success(game_diseases[key]["name"], treatment_loc, treatment_infections[key])
        return 1

  # Little helper function to show the results of treatment
  def show_treatment_success(self, disease_name, location, new_level):
    level_string = str(new_level)
    if new_level > 0:
      level_string += ' in 1000.'

    print("submitting treatment plan for %s ..." % disease_name)
    print("RESULTS: %s incidences in %s reduced to %s" % (disease_name, location, level_string))

  def cure(self, args, player):
    game_cities = self.L.cities
    cure_location = player["location"]
    like_cards = [0] * len(self.L.diseases)

    if "has_station" not in game_cities[cure_location] and game_cities[cure_location]["has_station"] != True:
      print("No Research Station here to implement your findings")
      return 0

    for card in player["research"]:
      if card in game_cities:
        like_cards[game_cities[card]["group"]] += 1

    has_cure = False
    for idx, val in enumerate(like_cards):
      if val >= player["solve"]:
        has_cure = True
        break

    if has_cure == True:
      self.L.cure(idx)
      print ("CONGRATULATIONS! Your collation of research has led to the cure for %s." % self.L.diseases[idx])
      return 1
    else:
      print("You do not have enough research to cure any disease")
      return 0


  """
  This Method handles a player moving to an adjacent city
  """
  def ride_or_ferry(self, args, player):
    if args == None:
      return 0

    args = args.upper()

    if args in self.L.cities[player["location"]]["connections"]:
      self.L.move_p(player, args)
      return 1
    else:
      print("destination is not on a ferry or shuttle route from here")
      return 0
      


  """
  This Method handles a player flying using one of their Research cards
  """
  def book_a_flight(self, args, player):
    if args == None:
      print("destination information required to book flight")
      return 0

    args = args.upper()
    locs = (player["location"], args)
    discard = locs[1]
    has_destination = args in player["research"]
    has_origin = player["location"] in player["research"]
    can_fly = has_origin or has_destination

    if not can_fly:
      print("no booking documents available for flight from %s to %s" % locs)
      return 0

    if has_destination:
      discard = locs[1]

    if has_origin:
      discard = locs[0]

    if has_origin and has_destination:
      correct_selection = 1
      print("You have booking documents for both %s and %s.  Which document would you like to use?" % locs)
      print("1. %s" % locs[0])
      print("2. %s" % locs[1])
      print("3. cancel")
      while correct_selection == 1:
        selection = input("Select 1 or 2}>")
        print(selection)
        if selection == "3":
          return 0
        if selection == "1" or selection == "2":
          print("We have a valid selection")
          correct_selection = 0

      discard = locs[int(selection) - 1]

    self.L.discard(player, discard)
    self.L.move_p(player, locs[1])
    print("COMMERCIAL FLIGHT booked to %s" % locs[1])
    print("Logging out at %s" % locs[0])
    print("...Logging in at %s" % locs[1])
    return 1

  def shuttle(self, args, player):
    origin = self.L.cities[player["location"]]
    origin_loc = origin["name"]

    if "has_station" not in origin or origin["has_station"] == False:
      print("ERROR: No Research Station here to shuttle from")
      return 0

    other_stations = []
    for city in self.L.cities:
      if "has_station" in self.L.cities[city] and self.L.cities[city]["has_station"] == True:
        other_stations.append(city)
    if origin_loc in other_stations:
      other_stations.remove(origin_loc)

    if len(other_stations) == 0:
      print("No available shuttle locations")
      return 0

    if args != None and args.upper() in self.L.cities:
      print("found args")
      arg_destination = args.upper()
    else:
      arg_destination = None

    if args == None or arg_destination not in other_stations:
      print("The following are valid shuttle locations")
      for city_name in other_stations:
        print(city_name)
      return 0
    
    if arg_destination in other_stations:
      print("SHUTTLE FLIGHT booked to %s" % arg_destination)
      print("Logging out at %s" % origin_loc)
      print("...Logging in at %s" % arg_destination)
      self.L.move_p(player, arg_destination)
      return 1

  def construct_station(self, args, player):
    can_build_here = False
    is_operations = False
    
    if player["build_here"] == True:
      can_build_here = True
      is_operations = True

    if player["location"] in player["research"]:
      can_build_here = True

    if player["location"] in self.L.cities_with_stations:
      can_build_here = False

    if can_build_here:
      self.show_construction_start(True, player["location"])
      self.L.build_station(player["location"])
      if not is_operations:
        self.L.discard(player, player["location"])
      return 1
    else:
      self.show_construction_start(False, player["location"])
      return 0

  def show_construction_start(self, boolean, location):
    if boolean == True:
      print("Construction contract submitted for RESEARCH STATION in %s.  Construction underway." % location)
    else:
      print("Resources are unavailable to build a RESEARCH STATION here.")

  def review(self, args, player):
    for idx, card in enumerate(player["research"]):
      counter = idx + 1
      if card in self.L.cities:
        print("%d. RESEARCH from %s on %s" % (counter, card, self.L.diseases[self.L.cities[card]["group"]]["name"]))
      else:
        print("%d. GRANT for %s" % (counter, card))

    return 0


  def status(self, args, player):
    print()
    print("===~ DISEASE STATUS ~===")
    for disease in self.L.diseases:
      affected_cities = []
      current_disease = self.L.diseases[disease]
      current_disease_info = (current_disease["name"], current_disease["color"], current_disease["cured"])

      for city in self.L.cities:
        if "infections" in self.L.cities[city] and disease in self.L.cities[city]["infections"] and self.L.cities[city]["infections"][disease] > 0:
          affected_cities.append(self.L.cities[city])

      affected_cities_string = ""
      for city in affected_cities:
        city_string = city["name"] + '(' + str(city["infections"][disease]) + ' in 1000): '
        affected_cities_string += city_string
      print("( )%s, color: %s, cured: %s" % current_disease_info)
      print("Cities Affected: " + affected_cities_string)

    print()
    print("===~ TEAM STATUS ~===")
    for player in self.L.players:
      this_location = self.L.players[player]["location"]
      this_city = self.L.cities[this_location]
      game_diseases = self.L.diseases

      print(player + " TEAM:")
      print("Currently located in " + this_location)
      if "infections" in this_city:
        infected_string = ""
        for key in this_city["infections"]:
          if this_city["infections"][key] > 0:
            infected_string += "(" + game_diseases[key]["name"] + ":" + game_diseases[key]["color"] + ":" + str(this_city["infections"][key]) +")"

      print("Connections: %s" % ','.join(this_city["connections"]))
      print()
    
    print("===~ RESEARCH STATIONS ~===")
    for station in self.L.cities_with_stations:
      print("[+] %s +-> %s" % (station, ', '.join(self.L.cities[station]["connections"])) )

    print()
    return 0

  def show_connections(self, args, player):
    if args == None:
      show_location = player["location"]
    elif args.upper() in self.L.cities:
      show_location = args.upper()
    else:
      show_location = None

    if show_location == None:
      print("input not understood")
      return 0

    spacer = "".join([" "] * len(show_location))
    print("nearby locatinos for %s" % show_location)
    print(show_location + " +")
    for cnx in self.L.cities[show_location]["connections"]:
      print("%s +-> %s +-> %s" % (spacer, cnx, ", ".join(self.L.cities[cnx]["connections"])))
    return 0

  def apply_grant(self, args, player):
    pass

  def transmit(self, args, player):
    pass

  def dispatch_other_player(self, args, player):
    pass

  def re_apply_grant(self, args, player):
    pass

  def skip_turn(self, args, player):
    return 4

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

