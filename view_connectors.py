def define_connectors():
  connectors = {}

  # Define 'N' Connectors
  connectors["n_3"] =["  |  ",
                      "  |  ",
                      "  o  ",
                      "   \ ",
                      "    \\"]

  connectors["n_4"] =["  |  ",
                      "  |  ",
                      "  o  ",
                      " /   ",
                      "/    "]

  # Define 'S' Connectors
  connectors["s_1"] =["\    ",
                      " \   ",
                      "  o  ",
                      "  |  ",
                      "  |  "]

  connectors["s_2"] =["    /",
                      "   / ",
                      "  o  ",
                      "  |  ",
                      "  |  "]                      

  # Define 'E' Connectors
  connectors["e_1"] =["\\    ",
                      " \\   ",
                      "  o--",
                      "     ",
                      "     "]

  connectors["e_4"] =["     ",
                      "     ",
                      "  o--",
                      " /   ",
                      "/    "]

  # Define 'W' Connectors
  connectors["w_2"] =["    /",
                      "   / ",
                      "--o  ",
                      "     ",
                      "     "]

  connectors["w_3"] =["     ",
                      "     ",
                      "--o  ",
                      "   \\ ",
                      "    \\"]

  # define straight Connectors
  connectors["bar"] =["     ",
                      "     ",
                      "-----",
                      "     ",
                      "     "]

  connectors["lin"] =["  |  ",
                      "  |  ",
                      "  |  ",
                      "  |  ",
                      "  |  "]

  connectors["tpl"] =["\    ",
                      " \   ",
                      "  \  ",
                      "   \ ",
                      "    \\"]

  connectors["btr"] =["    /",
                      "   / ",
                      "  /  ",
                      " /   ",
                      "/    "]

  connectors["z"] =["     ",
                    "     ",
                    "     ",
                    "     ",
                    "     "]

  return connectors

def city_square(text):
  middle = text if len(text) == 5 else "|"+text+"|"

  return ["#---#",
          "|   |",
          middle,
          "|   |",
          "#---#"]

def create_board(file_path):
  file_lines = []
  board = []
  pattern_map = {
    "N4": "n_4",
    "N3": "n_3",
    "S1": "s_1",
    "S2": "s_2",
    "E1": "e_1",
    "E4": "e_4",
    "W2": "w_2",
    "W3": "w_3",
    "--": "bar",
    "|" : "lin",
    "/" : "btr",
    "\\": "tpl"
  }

  f = open(file_path, 'rU')
  for line in f:
    file_lines.append(line,)
  f.close()

  for line in file_lines:
    squares = line.split(",")
    for idx,value in enumerate(squares):
      if value == "":
        squares[idx] = "z"
      if value in pattern_map:
        squares[idx] = pattern_map[value]
    squares.pop()
    board.append(squares)

  return board



  # board = [[]] * 8
  # board[0] = ["z", "z", "e_4", "bar", "CHI", "bar", "TRN", "bar", "N.Y"]
  # board[1] = ["bar", "SFO", "z", "z", "lin", "z", "lin", "z", "lin"]
  # board[2] = ["btr", "lin", "z", "z", "n_3", "z", "n_3", "z", "n_4"]
  # board[3] = ["z", "LAX", "z", "z", "z", "ATL", "bar", "WSH", "z"]
  # board[4] = ["btr", "z", "tpl", "z", "z", "n_3", "z", "n_4", "z"]
  # board[5] = ["z", "z", "z", "s_1", "z", "e_4", "MIA", "z", "z"]
  # board[6] = ["z", "z", "z", "MDF", "w_2", "z", "lin", "z", "z"]
  # board[7] = ["z", "z", "z", "z", "e_1", "bar", "BGT", "z", "z"]

  # return board

def print_board(board, connectors):
  LINES = 5
  for row in board:
    line_to_print = [""] * LINES
    for index in range(LINES):
      for square in row:
        if square in connectors:
          line_to_print[index] += connectors[square][index]
        else:
          line_to_print[index] += city_square(square)[index]

      print(line_to_print[index])



print_board(create_board('classic_board.csv'), define_connectors())
