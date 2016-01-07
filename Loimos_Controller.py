from Loimos_CmdLine_View import Command_Line_View as cl_view

"""
This is the Controller
"""
class Loimos_Controller:
# TODO: Separate Controller functionality from View functionality better

  def __init__(self, gameObj, values=None):
    if values is None:
      self.values = {}
    else:
      self.values = values

    self.L = gameObj
    self.view = cl_view(self)
    self.players = self.init_players()

    self.options = self.init_options()

  def get_config(self):
    config = {
      "players": self.players
    }

    return config

  def init_players(self):
    return self.view.select_players()

  def init_options(self):
    pass

  def offer_grant(self):
    return self.view.offer_grant()

  def require_discard(self, player):
    research = player["research"]

    if len(research) > 7:
      discard = self.view.select_discard(player)
      
      if discard in research:
        self.L.discard(player, discard)
      else:
        self.require_discard(player)
    else:
      return


  def take_player_turn(self, player):
    turn_active = 0
    actions_rem = 4

    while turn_active == 0:
      actions_rem -= self.view.prompt_action(player)
      if actions_rem <= 0:
        turn_active = 1

  def trade_research(self, l_player, r_player, direction, location):
    if direction == True:
      giving_player = l_player
      receiving_player = r_player
    else:
      giving_player = r_player
      receiving_player = l_player

    self.view.show_research_transfer(giving_player, receiving_player, location)
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

    if len(other_players_here) == 0:
      self.view.no_players_to_collaborate_with(here)
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

        research_selection = self.view.choose_research_to_give(player, research_player["group"])
        if research_selection in research_player["research"]:
          self.trade_research(self, player, player_to_trade, player_giving, research_selection)

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
          self.view.no_cards_to_trade(here)

    else:
      self.view.offer_eligible_players_to_collaborate(other_players_here)
      

  """
  This Method handles the player treating a disease in the city they are in
  """
  def treat(self, args, player):
    treatment_loc = player["location"]
    
    if "infections" in self.L.cities[treatment_loc] and str(args) in self.L.cities[treatment_loc]["infections"]:
      game_diseases = self.L.diseases
      treatment_infections = self.L.cities[treatment_loc]["infections"]
      
      if game_diseases[args]["cured"] == True:
        treatment_level = 3
      else:
        treatment_level = player["treat"]

      self.L.treat(treatment_loc, args, treatment_level)
      self.view.show_treatment_success(True, game_diseases[args], treatment_loc, treatment_infections[args])
    else:
      self.view.show_treatment_success(False, game_diseases[args], treatment_loc, treatment_infections[args])


  def cure(self, args, player):
    game_cities = self.L.cities
    cure_location = player["location"]
    like_cards = [0] * len(self.L.diseases)

    if "has_station" not in game_cities[cure_location] and game_cities[cure_location]["has_station"] != True:
      self.view.reject_cure_no_station()

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
      self.view.accept_cure(self.L.diseases[idx])
    else:
      self.view.reject_cure_no_cards()

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
      self.view.invalid_ride()
      
  """
  This Method handles a player flying using one of their Research cards
  """
  def book_a_flight(self, dest, player, discard):
    if dest == None:
      self.view.invalid_action()
    else:
      self.L.discard(player, discard)
      self.L.move_p(player, dest)

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
      self.view.show_construction_start(True, player["location"])
      self.L.build_station(player["location"])
      if not is_operations:
        self.L.discard(player, player["location"])
      return 1
    else:
      self.view.show_construction_start(False, player["location"])
      return 0


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
