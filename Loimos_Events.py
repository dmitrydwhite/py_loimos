class Card_Events:
  def __init__(self, view):
    self._event_map = {}
    self._provide_events()
    self._view = view

  def _provide_events(self):
    own_methods = dir(self)
    signed_events = []
    for method in own_methods:
      if method[0] != '_':
        this_method = getattr(self, method)
        this_key = this_method(None)
        self._event_map[this_key] = this_method
        signed_events.append(this_key)

    return signed_events

  def _apply(self, card_name, game_obj):
    self._event_map[card_name](game_obj)


  """
  To create more events, include the methods here.  The method name should be snake case and should not
  begin with an underscore(_).  The method should accept a 'game' argument, and should return identifying
  information about the event if 'game' is None.
  """
  def one_quiet_night(self, game):
    name = 'ONE QUIET NIGHT'
    if game == None:
      return name
    else:
      game.one_quiet_night = True

  def airlift(self, game):
    name = 'AIRLIFT'
    if game == None:
      return name
    else:
      airlift_info = self.view.request_airlift_info()
      game.move_p(airlift_info[0], airlift_info[1])


  def forecast(self, game):
    name = 'FORECAST'
    if game == None:
      return name
    else:
      replace = self.view.view_forecast(game.infection_dex[0:6] if len(game.infection_dex >= 6) else game.infection_dex)
      game.infection_dex[0:len(replace)] = replace


  def government_grant(self, game):
    name = 'GOVERNMENT GRANT'
    if game == None:
      return name
    else:
      new_station = self.view.view_government_grant()
      game.build_station(new_station)

  def resilient_pop(self, game):
    name = 'RESILIENT POPULATION'
    if game == None:
      return name
    else:
      pop_to_remove = self.view.view_resilient_pop(game.infected_cities)
      game.infected_cities.remove(pop_to_remove)
