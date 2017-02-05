import copy


__author__ = "Yuna Frolov"


# defines the board, and game elements
class Board:
    # define board
    def __init__(self, size, connect):
        self.white = []  # list of white's pieces
        self.black = []  # list of black's pieces
        self.board = [["." for x in range(size)] for x in range(size)]
        self.size = size
        self.connect = connect  # connect number needed to win
        self.win = False  # win status
        self.winstatement = ""  # what will be written at winning stage

    def __str__(self):
        string = ""
        if self.win:
            string += self.winstatement + "\n"
        string += "  "
        for i in range(self.size):
            string += "{0}{1}".format(i % 10, " " if i < 10 else "'")
        string += "\n"
        i = 0
        for x in self.board:
            string += "{0}{1}".format(i % 10, " " if i < 10 else "'")
            i += 1
            for y in x:
                string += "{0} ".format(y)
            string += "\n"
        return string

    def __len__(self): return self.connect  # len(board) returns connected number needed to win

    def __repr__(self): return str(self)

    def __getitem__(self, num): return self.board[num]

    def __eq__(self, other):
        return ( 
                type(self) == type(other) and
                self.white == other.white and self.black == other.black and self.size == other.size)

    def __ne__(self, other):
        return not (self == other)

    def turn(self):  # returns the color object of whoever's turn it is
        return Color(len(self.black) == len(self.white))

    # check if the move represents a valid space
    def _valid_move(self, (y, x)):
        return self._inBoard((y, x)) and self.board[y][x] == "."

    # is the coordinate on the board
    def _inBoard(self, (y, x)):
        return x >= 0 and x < self.size and y >= 0 and y < self.size

    # execution of a move
    def move(self, (y, x)):
        turn = self.turn()
        other = copy.deepcopy(self)
        if self.win:
            return other
        if not other._valid_move((y, x)):
            turn.swap()
            other.winstatement = "Invalid Move ({1},{2}) Played: {0} Wins by Default\n".format(str(turn), y, x)
            other.win = True
            return other
        
        other.board[y][x] = turn.symbol
        other.black.append((y,x)) if turn.isBlack else other.white.append((y, x))
        other.checkWinningMove()
        return other

    # return path to winning state of the winning color
    def _checkPath(self, color, (y, x), (py, px), counter):
        if not counter or not self._inBoard((y, x)) or self.board[y][x] != color.symbol:
            return 0
        return 1 + (self._checkPath(color, (y+py, x+px), (py, px), counter -1) if self._inBoard((y+py, x+px)) else 0)

    # if the last move won the game - all appropriate msgs are changed and win is announced
    def checkWinningMove(self):
        color = self.turn().getNot()
        pos = self.black[-1] if color.isBlack else self.white[-1]
        checklist = []
        depth = self.connect - 1
        for move in ((1, 0), (0, 1), (1, 1), (1, -1)):
            opp = tuple(map(lambda x: -x, move))
            checklist.append(1 + self._checkPath(color, tuple(sum(x) for x in zip(pos, move)), move, depth) +
                             self._checkPath(color, tuple(sum(x) for x in zip(pos, opp)), opp, depth))
        if self.connect in checklist:
            self.winstatement = "{0} wins!".format(str(color))
            self.win = True
        elif len(self.black)+len(self.white) == self.size**2:
            self.win = True
            self.winstatement = "It's a Draw (Defensive win for WHITE)"
            return


# a class to keep track of players turns - black and white
class Color:
    def __init__(self, isBlack):
        if isBlack:
            self.isBlack = True
            self.color = "BLACK"
            self.symbol = "B"
        else:
            self.isBlack = False
            self.color = "WHITE"
            self.symbol = "w"

    def __eq__(self, other):
        return type(self) == type(other) and self.color == other.color

    def __ne__(self, other): return not (self == other)

    def __str__(self): return self.color

    def __repr__(self): return str(self)

    def swap(self):  # swaps a color object from Black->White or reverse
        self.__init__(not self.isBlack)

    def getNot(self):  # returns a color object != self
        return Color(not self.isBlack)
