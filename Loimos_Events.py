class Card_Events:
  def __init__(self):
    # self.values = {}
    self._provide_events()

  def _provide_events(self):
    own_methods = dir(self)
    signed_events = []
    for method in own_methods:
      if method[0] != '_':
        print(method)
        this_method = getattr(self, method)
        signed_events.append(this_method(None))

    print signed_events

  def one_quiet_night(self, game):
    name = 'ONE QUIET NIGHT'
    print('in %s', name)
    if game == None:
      return name
    else:
      pass

  def airlift(self, game):
    name = 'AIRLIFT'
    print('in %s', name)
    if game == None:
      return name
    else:
      pass

  def forecast(self, game):
    name = 'FORECAST'
    print('in %s', name)
    if game == None:
      return name
    else:
      pass

  def government_grant(self, game):
    name = 'GOVERNMENT GRANT'
    print('in %s', name)
    if game == None:
      return name
    else:
      pass

  def resilient_pop(self, game):
    name = 'RESILIENT POPULATION'
    print('in %s', name)
    if game == None:
      return name
    else:
      pass

  # def __setitem__(self, key, value):
  #   self.values[key] = value

  # def __getitem__(self, key):
  #   return self.values[key]

L = Card_Events()
print(dir(L))