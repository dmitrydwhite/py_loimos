#!/usr/bin/python

import json

from random import randint

"The central operation of each game instance"
class GameSpace:
  MAX_OUTBREAKS = 7
  NUMBER_OF_DISEASES = 4
  DISEASE_COLORS = ["yellow", "red", "blue", "gray"]
  DISEASE_CUBES = 24
  STARTING_STATION = "ATLANTA"

  "initialize GameSpace values"
  def __init__(self):
    config = self.init_user_interface()

    self.cities = self.cities()
    self.players = self.init_players(config.players)
    self.outbreak_counter = self.init_outbreak_counter(config.outbreak_counter);
    self.player_dex = self.init_player_deck()
    self.infection_dex = self.init_infection_deck()
    self.infected_cities = []
    self.diseases = self.init_diseases(config.diseases)

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
    pass

  "Initialize Players"
  def init_players(self):
    pass

  "Initialize the outbreak counter"
  def init_outbreak_counter(self, config):
    counter = {
      "outbreaks": config.outbreaks or 0,
      "maximum": config.max_outbreaks or self.MAX_OUTBREAKS
    }

    return counter

  def init_player_deck(self):
    pass

  def init_infection_deck(self):
    pass

  def init_diseases(self):
    diseases = {}
    disease_names = self.generate_disease_names(self.NUMBER_OF_DISEASES)

    for idx, dizeez in enumerate(disease_names):
      diseases[idx] = {
        "name": dizeez,
        "cubes_left": self.DISEASE_CUBES,
        "color": self.DISEASE_COLORS[idx],
        "cured": False
      }

    return diseases

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

L = GameSpace()

print(L.diseases)
print(L.cities)