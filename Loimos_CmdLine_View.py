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
      "treat": self.ctrl.treat,
      "cure": self.ctrl.cure,
      "ride": self.ctrl.ride_or_ferry,
      "book": self.ctrl.book_a_flight,
      "shuttle": self.ctrl.shuttle,
      "station": self.ctrl.construct_station, #Fully Extracted, 12/26/15
      "review": self.review, # Optional Method, Complete, 12/26/15
      "status": self.status, # Optional Method, Complete, 12/26/15
      "cx": self.show_connections, # Optional Method, Complete, 12/26/15
      "apply": self.ctrl.apply_grant,
      "xm": self.ctrl.transmit,
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

  def choose_research_to_give(self, this_turn_player, research_player):
    print("Select Research from the %s TEAM to transfer:" % research_player["group"])
    self.review(self, research_player)
    correct_input = 0
    while correct_input == 0:
      research_selection = int(input("Select a number}>")) - 1
      if research_selection in range(len(research_player["research"])):
        correct_input = 1
    return research_player["research"][research_selection]
   

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
