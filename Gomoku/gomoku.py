import Board as b
import heuristic as ef
import time


__author__ = "Yuna Frolov"


# play the game, launched from the main
def Gomoku(board_size=0, connect_size=0, tlimit=0):

    # first moves are made on a clean board
    board = b.Board(board_size, connect_size)
    print("Black moves first")
    move = ef.firstmove(board)
    board = board.move(move)
    print("Black moved {0}".format(move))
    print(board)
    move = ef.secondmove(board)
    board = board.move(move)
    print("White moved {0}".format(move))
    print(board)

    # while no winner is announced, make moves in turns
    while not board.win:
        # Black Moves
        t = time.time()
        move = ef.nextMove(board, tlimit, 3)
        print(time.time() - t)
        board = board.move(move)
        print("Black moves {0}".format(move))
        print(board)

        if board.win:
            break

        # White Moves
        t = time.time()
        move = ef.nextMove(board, tlimit, 3)
        print(time.time() - t)
        board = board.move(move)
        print("White moves {0}".format(move))
        print(board)

    print("GAME OVER")
    return

# launch main
if __name__ == "__main__":
    # (board_size=15, connect_size=5, tlimit=60) - this is the standard setup for Gomoku
    Gomoku(15, 5, 60)
