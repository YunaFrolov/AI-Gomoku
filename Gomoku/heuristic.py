import Queue as q
import time


__author__ = "Yuna Frolov"


# first and second pre-determined moves
def firstmove(board):
    x = board.size/2
    return x, x


def secondmove(board):
    (oy, ox) = board.black[0]
    if oy <= board.size/2:
        dy = 1
    else:
        dy = -1

    if ox <= board.size/2:
        dx = 1
    else:
        dx = -1
    return oy + dy, ox + dx


# evaluates each position on the board with significant weights
# the more connected colors the attacker has in a row - the more the position next to it weighs
# the function prefers to make a winning move than a defending move
def heuristic(board, position, attack):
    (y, x) = position
    color = board.turn() if attack else board.turn().getNot()
    total_consec = 0
    for pair in ((1, 0), (0, 1), (1, 1), (1, -1)):
        (dy, dx) = pair
        pathlist = ["."]
        for s in (1, -1):
            for i in range(1,board.connect):
                py = y+dy*i*s
                px = x+dx*i*s
                if (not board._inBoard((py, px)) or board[py][px] == color.getNot().symbol) or (i+1 == board.connect and
                    board._inBoard((py+dy*s,px+dx*s)) and board[py+dy*s][px+dx*s] == color.symbol):
                    break
                elif s > 0:  # append to back if right of position
                    pathlist.append(board[py][px])
                elif s < 0:  # insert to front if left of position
                    pathlist.insert(0, board[py][px])

        paths_num = len(pathlist) - len(board) + 1
        if paths_num > 0:
            for i in range(paths_num):
                consec = pathlist[i:i+board.connect].count(color.symbol)
                total_consec += consec**5 if consec != board.connect-1 else 100**(9 if attack else 8)
    return total_consec


# this function evaluates the attack power of the other player (max of min)
# the importance of a position is rated as:
# it's attack power + it's defense power, which is attack power for you + attack power for them.
def evaluate_position(board, position):
    return heuristic(board, position, True) + heuristic(board, position, False) if board._valid_move(position) else 0


# return the area that may be attacked by opponent from (y, x)
def attackArea((y,x), connect):
    area = []
    for pair in ((1, 0),(0, 1),(1, 1),(1, -1)):
        (dy, dx) = pair
        for s in (1, -1):
            for i in range(1, connect):
                py = y+dy*i*s
                px = x+dx*i*s
                area.append((py, px))
    return area


# returns the move limit as valued by evaluate_position
def moveLimit(board, limit):
    topqueue = q.PriorityQueue()
    spots = set()
    for t in board.black+board.white:
        for m in attackArea(t, len(board)):
            if board._inBoard(m):
                spots.add(m)
    for r in spots:
        topqueue.put((evaluate_position(board, r)*(-1), r))
    toplist = []       
    for x in range(limit):
        toplist.append(topqueue.get())
    return map(lambda (x, y): (-x, y), toplist)


# return the best valued moves by evaluate_position
def justBestMoves(board,limit):
    toplist = moveLimit(board, limit)
    topval = toplist[0][0]
    bestlist = []
    for atom in toplist:
        (val, move) = atom
        if val == topval:
            bestlist.append(move)
    return bestlist
            

# using Quiescent search - returns a move where search predicts a win or best move
def nextMove(board, tlimit, dive=1):
    checkTOP_ = 10
    checkDEPTH_ = 20
    atomlist = moveLimit(board, checkTOP_)
    mehlist = []
    bahlist = []
    
    tfract = (tlimit-((0.1)*(tlimit/10 + 1)))/float(len(atomlist))
    for atom in atomlist:
        (val,move) = atom
        nextboard = board.move(move)
        if nextboard.win:
            return move
        if dive == 1:
            score = -depth_1(nextboard, checkDEPTH_ - 1)
        elif dive == 2:
            score = -depth_2(nextboard, checkDEPTH_ - 1)
        elif dive == 3:
            score = -depth_3(nextboard, checkDEPTH_ - 1, time.time(), tfract)
        elif dive == 4:
            score = -depth_4(nextboard, time.time(), tfract)
        elif dive == 5:
            score = -depth_5(nextboard, checkDEPTH_ - 1)

        if score == 1:
            return move
        elif score == 0:
            mehlist.append((score, move))
        elif score > -1:
            bahlist.append((score, move))
        if len(mehlist):
            return mehlist[0][1]
        elif len(bahlist):
            bahlist.sort()
            return bahlist[-1][1]
        else:
            return atomlist[0][1]


# ----- depths used in quiescent search above -----

def depth_1(board, dlimit):
    bestmove = moveLimit(board, 1)[0][1]
    newboard = board.move(bestmove)
    if newboard.win:
        return 1
    elif not dlimit:
        return 0
    else:
        return -depth_1(newboard, dlimit - 1)


def depth_2(board, dlimit):
    bestmoves = justBestMoves(board, 5)
    overall = 0.0
    split_factor = 1.0/len(bestmoves)
    for bmove in bestmoves:
        newboard = board.move(bmove)
        if newboard.win:
            return 1
        elif not dlimit:
            continue
        else:
            score = -depth_2(newboard, dlimit - 1)
            if score == 1:
                return 1
            else: overall += split_factor*score
    return overall


def depth_3(board, dlimit, start_tyme, tlimit):
    bestmove = moveLimit(board, 1)[0][1]
    newboard = board.move(bestmove)
    if newboard.win:
        return 1
    elif time.time()-start_tyme > tlimit or not dlimit:
        return 0
    else:
        return -depth_3(newboard, dlimit - 1, start_tyme, tlimit)


def depth_4(board, start_time, tlimit):
    bestmove = moveLimit(board, 1)[0][1]
    newboard = board.move(bestmove)
    if newboard.win:
        return 1
    elif time.time()-start_time > tlimit:
        return 0
    else:
        return -depth_4(newboard, start_time, tlimit)


def depth_5(board, dlimit):
    TOPCHECK = 3
    bestmoves = moveLimit(board, TOPCHECK)
    overall = 0.0
    split_factor = 1.0/len(bestmoves)
    for bmove in bestmoves:
        newboard = board.move(bmove[1])
        if newboard.win:
            return 1
        elif not dlimit:
            return 0
        else:
            score = -depth_5(newboard, dlimit - 1)
            if score == 1:
                return 1
            elif not score:
                return 0
            else:
                overall += split_factor
    return overall
