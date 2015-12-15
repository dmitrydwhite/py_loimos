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
