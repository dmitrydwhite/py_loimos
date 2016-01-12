class Command_Line_View:
  """
  This Class is the Initial Pass at making a view for the Loimos app.
  Here is a backwards-working list of methods:

  =~Main Class Required Methods~=
  select_players:
    Gathers info from user;
    Selects players;
    Returns either a List of Strings of Player roles ["SCIENCE", "MEDICAL"] or a number of players;

  =~Controller Required Methods~=
  prompt_action:
    Gathers info from user;
    Central input from user;
  select_discard:
    Gathers info from user;
    Returns String of card in player's hand ("ALL CAPS");
  choose_research_to_give:
    Gathers info from user;
    Accepts (Player who's turn it is, Research Team Player);
    Returns String "LOCATION";
  show_construction_start:
    Displays info to user;
    Accepts Boolean, "LOCATION";
    Displays results of attempt to build a research station;
  no_players_to_collaborate_with:
    Displays info to user;
    Accepts "LOCATION";
    Displays that there are no other teams in "LOCATION";
  offer_eligible_players_to_collaborate:
    Displays info to user;
    Accepts List of Strings ["PLAYER", "TEAMS"];
    Displays those player teams to user;
  show_treatment_success:
    Displays info to user;
    Accepts boolean, disease, location, new disease level;
    Displays success or failure (based on boolean) of user's treatment action;
  accept_cure:
    Displays info to user;
    Displays success of cure;
  reject_cure_no_station:
    Displays info to user;
    Displays cure not valid due to user not at Research Station;
  reject_cure_no_cards:
    Displays info to user;
    Displays cure not valid due to user doesn't have enough cards to cure;
  invalid_ride:
    Displays info to user;
    Displays that user's move to adjacent city is invalid;
  invalid_action:
    Displays info to user;
    Displays generic message that user action is not valid;


  =~Loimos_Events Required Methods~=
  request_airlift_info: 
    Gathers info from user; 
    Returns a 2-Tuple of (player to move, new location);
  view_forecast:
    Gathers info from user;
    Shows all players the 1st 6 cities in the infection deck;
    Allows players to re-order those cities;
    Returns a List of the 6 cities in order;
  view_government_grant:
    Gathers info from user;
    Select a location to build a free Research Station;
    Returns a String("LOCATION");
  """
  
  def __init__(self, controller):
    self.ctrl = controller
    self.L = controller.L

  def select_players(self):
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

  def prompt_action(self, player):
    input_status = 0
    commands = {
      "collab": self.ctrl.collaborate, # Fully Extracted, 12/26/15
      "treat": self.view_treat, # Fully Extracted, 1/7/16
      "cure": self.ctrl.cure, # Fully Extracted, 1/7/16
      "ride": self.ctrl.ride_or_ferry, # Fully Extracted, 1/7/16
      "book": self.view_book_a_flight, # Fully Extracted, 1/7/16
      "shuttle": self.view_shuttle, # Fully Extracted, 1/12/16
      "station": self.ctrl.construct_station, #Fully Extracted, 12/26/15
      "review": self.review, # Optional Method, Complete, 12/26/15
      "status": self.status, # Optional Method, Complete, 12/26/15
      "cx": self.show_connections, # Optional Method, Complete, 12/26/15
      "apply": self.ctrl.apply_grant,
      "xm": self.ctrl.transmit, # Pass
      "dispatch": self.ctrl.dispatch_other_player,
      "reapply": self.ctrl.re_apply_grant,
      "skip": self.skip_turn # Optional Method, Complete, 12/26/15
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

  def offer_grant(self):
    print("Does any team wish to submit a grant?")

  def select_discard(self, player):
    research = player["research"]

    print()
    print("MSG::CDC==>@%s.TEAM[You must abandon some of your research or forego a grant to continue]:" % player["group"])
    self.review(self, player)
    abandon = int(input("Select a number to abandon: ")) - 1

    if abandon in range(len(research)):
      print("abandoning %s" % research[abandon])
      return research[abandon]
    else:
      return None

  def view_treat(self, args, player):
    game_diseases = self.L.diseases
    disease_to_treat = None
    treatment_loc = player["location"]
    treatment_infections = {}

    # If we have args, set it to match the UPPERCASE that our data is in
    if args != None:
      args = args.lower()
    
    # Check to see if there are any diseases present in this location, if so make that our infections obj
    if "infections" in self.L.cities[treatment_loc]:
      treatment_infections = self.L.cities[treatment_loc]["infections"]

    # First let's set disease_to_treat to the first disease in this city
    if len(treatment_infections) > 0:
      for disease in treatment_infections:
        if treatment_infections[disease] != 0:
          disease_to_treat = disease
          break

    if len(treatment_infections) > 1:     
      multi_diseases = True
    else:
      multi_diseases = False

    if multi_diseases == True:
    # In this block, there is more than one disease present in the city
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
            disease_to_treat = disease
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

    if disease_to_treat == None:
      self.show_no_diseases_here()
      return 0  
    else:
      self.ctrl.treat(disease_to_treat, player)
      return 1

  def view_book_a_flight(self, args, player):
    if args == None:
      print("destination information required to book flight")
      return 0

    args = args.upper()
    locs = (player["location"], args)
    discard = locs[1]

    if locs == discard:
      print("Cannot fly to your current location")
      return 0

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
          correct_selection = 0

      discard = locs[int(selection) - 1]
      print("%s selected as booking document for flight", discard)

    self.ctrl.book_a_flight(locs[1], player, discard)
    print("COMMERCIAL FLIGHT booked to %s" % locs[1])
    print("Logging out at %s" % locs[0])
    print("...Logging in at %s" % locs[1])
    return 1

  def view_shuttle(self, args, player):
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
      if player["fly_from_station"] == True:
        self.ops_shuttle(args, player)
      else:
        print("No available shuttle locations")
        return 0

    if args != None and args.upper() in self.L.cities:
      arg_destination = args.upper()
    else:
      arg_destination = None

    if args == None or arg_destination not in other_stations:
      if player["fly_from_station"] == True:
        self.ops_shuttle(args, player)
      else:
        print("The following are valid shuttle locations")
        for city_name in other_stations:
          print(city_name)
        return 0
    
    if arg_destination in other_stations:
      self.ctrl.shuttle(arg_destination, player)
      print("SHUTTLE FLIGHT booked to %s" % arg_destination)
      print("Logging out at %s" % origin_loc)
      print("...Logging in at %s" % arg_destination)
      return 1

  def ops_shuttle(self, args, player):
    destination = args.upper()
    print("select any booking document to fly from this research station to %s" % destination)
    self.review(self, player)
    valid_input = False
    while valid_input == False:
      discard = int(input("select document > ")) - 1
      if discard in range(len(player["research"])):
        valid_input = True

    print("SHUTTLE FLIGHT booked to %s" % destination)
    print("Logging out at %s" % player["location"])
    print("...Logging in at %s" % destination)
    self.ctrl.book_a_flight(destination, player, player["research"][discard])

  def choose_research_to_give(self, this_turn_player, research_player):
    print("Select Research from the %s TEAM to transfer:" % research_player["group"])
    self.review(self, research_player)
    correct_input = 0
    while correct_input == 0:
      research_selection = int(input("Select a number}>")) - 1
      if research_selection in range(len(research_player["research"])):
        correct_input = 1
    return research_player["research"][research_selection]
   

  def show_treatment_success(self, boolean, disease, location, new_level):
    if boolean == True:
      disease_name = disease["name"]
      level_string = str(new_level)
      if new_level > 0:
        level_string += ' in 1000.'

      print("submitting treatment plan for %s ..." % disease_name)
      print("RESULTS: %s incidences in %s reduced to %s" % (disease_name, location, level_string))
    else:
      print("treatment of %s in %s was invalid" % (disease_name, location))

  def accept_cure(self, disease):
    print ("CONGRATULATIONS! Your collation of research has led to the cure for %s." % disease["name"])
    return 1

  def reject_cure_no_station(self):
    print("No Research Station here to implement your findings")
    return 0

  def reject_cure_no_cards(self):
    print("You do not have enough research to cure any disease")
    return 0

  def invalid_ride(self):
    print("destination is not on a ferry or shuttle route from here")
    return 0

  def show_construction_start(self, boolean, location):
    if boolean == True:
      print("Construction contract submitted for RESEARCH STATION in %s.  Construction underway." % location)
    else:
      print("Resources are unavailable to build a RESEARCH STATION here.")

  def offer_eligible_players_to_collaborate(self, player_array):
    print("You must specify a team in this location to collaborate with")
    for team in player_array:
      print(team["group"])
    return 0

  def no_cards_to_trade(self, here):
    print("No baseline Research data in %s for collaboration" % here)
    return 0

  def show_research_transfer(self, giving_player, receiving_player, location):
    print("Transferring research gathered in %s from %s TEAM to %s TEAM" % (location, giving_player, receiving_player))

  def show_no_diseases_here(self):
    print("no diseases suitable for treatment at this location")

  ### Optional Methods ###
  def skip_turn(self, args, player):
    return 4

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

  def review(self, args, player):
    for idx, card in enumerate(player["research"]):
      counter = idx + 1
      if card in self.L.cities:
        print("%d. RESEARCH from %s on %s" % (counter, card, self.L.diseases[self.L.cities[card]["group"]]["name"]))
      else:
        print("%d. GRANT for %s" % (counter, card))

    return 0
