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
