# -*- coding: latin-1 -*-
import sys
import unittest
sys.path.append("..")
import random
from Player import *
from Constants import *
from Construction import *
from Ant import *
from Move import Move
from GameState import *
from AIPlayerUtils import *
from Building import *
from Location import *
from Inventory import *


##
# AIPlayer
# Descriptiorundll32.exe sysdm.cpl,EditEnvironmentVariablesrundll32.exe sysdm.cpl,EditEnvironmentVariablesrundll32.exe sysdm.cpl,EditEnvironmentVariablesrundll32.exe sysdm.cpl,EditEnvironmentVariablesrundll32.exe sysdm.cpl,EditEnvironmentVariablesrundll32.exe sysdm.cpl,EditEnvironmentVariablesrundll32.exe sysdm.cpl,EditEnvironmentVariablesrundll32.exe sysdm.cpl,EditEnvironmentVariablesn: The responsbility of this class is to interact with the game by
# deciding a valid move based on a given game state. This class has methods that
# will be implemented by students in Dr. Nuxoll's AI course.
#
# Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):
    # __init__
    # Description: Creates a new Player
    #
    # Parameters:
    #   inputPlayerId - The id to give the new player (int)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer, self).__init__(inputPlayerId, "ALPHA TEAM (burnsl17 and alconcel16")

    def closerTo(self, prevState, currentState, target):
        myAntsPrev = prevState.inventories[self.playerId].ants
        myAntsAft = currentState.inventories[self.playerId].ants
        for i in range(0, len(myAntsPrev)):
            if stepsToReach(currentState, myAntsAft[i].coords, target) < \
                stepsToReach(prevState, myAntsPrev[i].coords, target):
                return True
        return False
    ##
    # getPlacement
    # Description: The getPlacement method corresponds to the
    # action taken on setup phase 1 and setup phase 2 of the game.
    # In setup phase 1, the AI player will be passed a copy of the
    # state as currentState which contains the board, accessed via
    # currentState.board. The player will then return a list of 10 tuple
    # coordinates (from their side of the board) that represent Locations
    # to place the anthill and 9 grass pieces. In setup phase 2, the player
    # will again be passed the state and needs to return a list of 2 tuple
    # coordinates (on their opponent’s side of the board) which represent
    # Locations to place the food sources. This is all that is necessary to
    # complete the setup phases.
    #
    # Parameters:
    #   currentState - The current state of the game at the time the Game is 
    #       requesting a placement from the player.(GameState)
    #
    # Return: If setup phase 1: list of ten 2-tuples of ints -> [(x1,y1), (x2,y2),…,(x10,y10)]
    #       If setup phase 2: list of two 2-tuples of ints -> [(x1,y1), (x2,y2)]
    ##
    def getPlacement(self, currentState):
        numToPlace = 0
        # implemented by students to return their next move
        if currentState.phase == SETUP_PHASE_1:  # stuff on my side
            numToPlace = 11
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    # Choose any x location
                    x = random.randint(0, 9)
                    # Choose any y location on your side of the board
                    y = random.randint(0, 3)
                    # Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        # Just need to make the space non-empty. 
                        # So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        elif currentState.phase == SETUP_PHASE_2:  # stuff on foe's side
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    # Choose any x location
                    x = random.randint(0, 9)
                    # Choose any y location on enemy side of the board
                    y = random.randint(6, 9)
                    # Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        # Just need to make the space non-empty. 
                        # So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        else:
            return [(0, 0)]


    ##
    # getMove
    # Description: The getMove method corresponds to the play phase of the game
    # and requests from the player a Move object. All types are symbolic
    # constants which can be referred to in Constants.py. The move object has a
    # field for type (moveType) as well as field for relevant coordinate
    # information (coordList). If for instance the player wishes to move an ant,
    # they simply return a Move object where the type field is the MOVE_ANT constant
    # and the coordList contains a listing of valid locations starting with an Ant
    # and containing only unoccupied spaces thereafter. A build is similar to a move
    # except the type is set as BUILD, a buildType is given, and a single coordinate
    # is in the list representing the build location. For an end turn, no coordinates
    # are necessary, just set the type as END and return.
    #
    # Parameters:
    #   currentState - The current state of the game at the time the Game is
    #       requesting a move from the player.(GameState)
    #
    # Return: Move(moveType [int], coordList [list of 2-tuples of ints], buildType [int]
    ##
    def getMove(self, currentState):
        moveList = listAllLegalMoves(currentState)
        moveEvals = []

        # Evaluate every move and store the value in a list
        for move in moveList:
            moveEvals.append(self.prediction(currentState.fastclone(),\
                currentState.fastclone(), move))

        bestMove = 0.0
        bestIndex = 0
        # Iterate through the move evaluations to find the best
        for i in range(0, len(moveEvals)):
            # If move has an eval of 1.0 (win condition, or other 
            # top priority move) then execute that move
            if moveEvals[i] == 1.0:
                return moveList[i]
            elif moveEvals[i] > bestMove:
                bestMove = moveEvals[i]
                bestIndex = i

        # If the best move found is 0.0 (lose condition, or very bad move), do nothing
        if moveEvals[bestIndex] == 0.0:
            return Move(END, None, None)

        return moveList[bestIndex]

    ##
    # prediction
    # Description: Function that parses given moves and applies them to a fastClone()
    # of the gameState in order to predict the outcome of each move.
    #
    # Parameters:
    #   currentState - A fastClone of the current state of the game at the time, which
    #       will be updated with the given move.(GameState)
    #   prevState - A faslClone of the current state, which will not be modified, used to 
    #       compare result of move with state of game before that move. (GameState)
    #   move - A move object which is used to tell what move is being performed.
    #
    # Return: Result of pointValue assessment of given move [double]
    ##
    def prediction(self, prevState, currentState, move):
        if move.moveType == MOVE_ANT:
            initCoord = move.coordList[0]
            finalCoord = move.coordList[-1]
            inventories = currentState.inventories[self.playerId]
            myAnts = inventories.ants
            index = 0
            for ant in currentState.inventories[self.playerId].ants:
                if ant.coords == initCoord:
                    ant.coords = finalCoord
                    ant.hasMoved = True
                index +=1
            return self.pointValue(prevState, currentState)
        elif move.moveType == BUILD:
            coord = move.coordList[0]
            currentPlayerInv = currentState.inventories[currentState.whoseTurn]
            tunnel = currentPlayerInv.getAnthill()
            tunnelCoords = tunnel.coords
            if move.buildType == TUNNEL:
                currentPlayerInv.foodCount -= CONSTR_STATS[move.buildType][BUILD_COST]

                tunnel = Building(coord, TUNNEL, currentState.whoseTurn)
                currentPlayerInv.constrs.append(tunnel)
            else:
                currentPlayerInv.foodCount -= UNIT_STATS[move.buildType][COST]
                ant = Ant(coord, move.buildType, currentState.whoseTurn)
                ant.hasMoved = True
                currentState.inventories[self.playerId].ants.append(ant)
                currentState.inventories[currentState.whoseTurn].ants.append(ant)

            return self.pointValue(prevState, currentState)

    ##
    # pointValue
    # Description: Function that takes two gameStates and evaluates the 
    #       move that has been performed
    #
    # Parameters:
    #   currentState - A fastClone of the current state of the game at the time, which
    #       has been updated with a move.(GameState)
    #   prevState - A faslClone of the current state, which was not modified, used to 
    #       compare result of move with state of game before that move. (GameState)
    #   
    # Return: 0.0 to 1.0 evaluation of the executed move [double]
    ##
    def pointValue(self, prevState, currentState):
        myID = self.playerId
        oppID = PLAYER_ONE

        if myID == PLAYER_ONE:
            oppID = PLAYER_TWO

        # Variables to hold data to assess the move quality
        runTotal = 0.0
        numChecks = 0

        # Win Conditions
        if currentState.inventories[myID].foodCount >= FOOD_GOAL:
            return 1.0
        elif currentState.inventories[oppID].getQueen() == None:
            return 1.0
        elif currentState.inventories[oppID].getAnthill().captureHealth <= 0:
            return 1.0

        # Lose Conditions
        if currentState.inventories[oppID].foodCount >= FOOD_GOAL:
            return 0.0
        elif currentState.inventories[myID].getQueen() == None:
            return 0.0
        elif currentState.inventories[myID].getAnthill().captureHealth <= 0:
            return 0.0

        # enemy before and after inventories
        enemyInvPrev = prevState.inventories[oppID]
        enemyInvAft = currentState.inventories[oppID]

        # my before and after inventories
        myInvPrev = prevState.inventories[myID]
        myInvAft = currentState.inventories[myID]

        # my ant list
        myAntListPrev = myInvPrev.ants
        myAntListAft = myInvAft.ants

        # my workers before and after
        workerPrev = []
        workerAft = []
        workerPrevCarrying = []
        workerPrevNot = []
        workerAftCarrying = []
        workerAftNot = []

        # Constructions on own side
        myAntHill = currentState.inventories[myID].getAnthill()
        myTunnels = currentState.inventories[myID].getTunnels()
        myConstr = []
        myConstr.append(myAntHill)
        for tunnel in myTunnels:
            myConstr.append(tunnel)

        # If an ant has the chance to attack the queen, high value move
        surroundingOpp = listAdjacent(currentState.inventories[oppID].getQueen().coords)
        for space in surroundingOpp:
            for ant in myAntListAft:
                if ant.coords == space:
                    runTotal += 0.9
                    numChecks += 1

        # Organizational: separates carrying an non-carrying ants
        for ant in myAntListPrev:
            if ant.type == WORKER:
                if ant.carrying:
                    workerPrevCarrying.append(ant)
                else:
                    workerPrevNot.append(ant)
                workerPrev.append(ant)

        for ant in myAntListAft:
              if ant.type == WORKER:
                if ant.carrying:
                    workerAftCarrying.append(ant)
                else:
                    workerAftNot.append(ant)
                workerAft.append(ant)          

        # kill enemy ant
        enemyAntCountPrev = len(enemyInvPrev.ants)
        enemyAntCountAft = len(enemyInvAft.ants)
        if enemyAntCountAft < enemyAntCountPrev:
            runTotal+= 0.65
            numChecks += 1

        # enemy structure health reduced
        enemyTunnelPrevHealth = enemyInvPrev.constrs[1].captureHealth
        enemyTunnelAftHealth = enemyInvAft.constrs[1].captureHealth

        enemyHillPrevHealth = enemyInvPrev.constrs[0].captureHealth
        enemyHillAftHealth = enemyInvAft.constrs[0].captureHealth

        if enemyTunnelAftHealth < enemyTunnelPrevHealth or enemyHillPrevHealth < enemyHillAftHealth:
            runTotal+=0.65
            numChecks +=1


        # ants that aren't carrying get closer to food

        # if there are more ants carrying than before, then that's a good thing
        if len(workerPrevNot) < len(workerAftNot):
            runTotal += 0.65
            numChecks +=1

        closestFoodDist = 99999
        foodCoords = []
        for x in range(0, 10):
            for y in range(0,4):
                currItem = getConstrAt(currentState, (x,y))
                if currItem != None and currItem.type == FOOD:
                    foodCoords.append(currItem.coords)

        closestDistancesPrev = []
        closestCoordsPrev = []
        sumPrev = 0
        sumAft = 0
        for ant in workerPrevNot:
            for coord in foodCoords:
                currDist = stepsToReach (prevState, ant.coords, coord)
                if currDist < closestFoodDist:
                    closestFoodDist = currDist
            sumPrev += closestFoodDist

        closestFoodDist = 99999
        for ant in workerAftNot:
            for coord in foodCoords:
                currDist = stepsToReach (currentState, ant.coords, coord)
                if currDist < closestFoodDist:
                    closestFoodDist = currDist
            sumAft += closestFoodDist
        if sumAft < sumPrev:
            runTotal+=0.5+(sumPrev-sumAft)#score depends on how much closer the ant got
            numChecks +=1

        #ants that are carrying get closer to tunnel
        tunnelCoords = []
        #find out where the tunnel is
        for x in range(0, 10):
            for y in range(0,4):
                currItem = getConstrAt(currentState, (x,y))
                if currItem != None and (currItem.type == ANTHILL or currItem.type == TUNNEL):
                    tunnelCoords.append(currItem.coords)

        closestTunnDist = 99999
        closestPrevDist = 0
        #find out how far the carrying workers are before the move
        for ant in workerPrevCarrying:
            for coord in tunnelCoords:
                currDist = stepsToReach(prevState, ant.coords, coord)
                if currDist < closestTunnDist:
                    closestTunnDist = currDist
            closestPrevDist += closestTunnDist

        closestTunnDist = 99999
        closestAftDist = 0
        #find out how far the carrying workers are after the move
        for ant in workerAftCarrying:
            for coord in tunnelCoords:
                currDist = stepsToReach(currentState, ant.coords, coord)
                if currDist < closestTunnDist:
                    closestTunnDist = currDist
            closestAftDist += closestTunnDist

        if closestAftDist < closestPrevDist:
            runTotal+=0.65+(closestPrevDist-closestAftDist)#how "good" the move is depends on how
            numChecks +=1#much closer they got

        #prevent overextension of workers
        if len(workerAft) > 3:
            runTotal +=0.1
            numChecks+=1
            
        #prevent overextension of ants in general
        if len(myAntListAft) > 4:
            runTotal +=0.1
            numChecks +=1

        # If there are already 3 ants owned by the AI, 
        # and the next move would make more, don't make more
        if len(myInvAft.ants) > 3 and len(myInvPrev.ants) < len(myInvAft.ants):
            return 0.0


        surroundingMe = listAdjacent(currentState.inventories[myID].getQueen().coords)
        enemyAntList = enemyInvAft.ants
        # If there are enemy ants within a space of the queen, move away
        for ant in enemyAntList:
            for space in surroundingMe:
                if ant.coords != space:
                    runTotal += 0.85
                    numChecks += 1
                else:
                    runTotal += 0.15
                    numChecks += 1

        # Finds the locations of all constructions owned by the AI
        onConst = []
        for const in myConstr:
            onConst.append(const.coords)

        # Finds if an enemy ant is on one of the AI's constructions
        for ant in enemyAntList:
            for coord in onConst:
                # If enemy is ON construction
                if ant.coords == coord:
                    if self.closerTo(prevState, currentState, coord):
                        runTotal += 0.99
                        numChecks += 1
                    else:
                        runTotal += 0.01
                        numChecks += 1

        # If the queen is standing on food, move
        for food in foodCoords:
            if food == currentState.inventories[myID].getQueen().coords:
                runTotal += 0.15
                numChecks += 1
            else:
                runTotal += 0.5
                numChecks += 1

        # PREVENT DIVIDE BY 0 ERROR
        if numChecks == 0:
            return 0.0

        # Return average move value
        return (runTotal / numChecks)

    ##
    # getAttack
    # Description: The getAttack method is called on the player whenever an ant completes
    # a move and has a valid attack. It is assumed that an attack will always be made
    # because there is no strategic advantage from withholding an attack. The AIPlayer
    # is passed a copy of the state which again contains the board and also a clone of
    # the attacking ant. The player is also passed a list of coordinate tuples which
    # represent valid locations for attack. Hint: a random AI can simply return one of
    # these coordinates for a valid attack.
    #
    # Parameters:
    #   currentState - The current state of the game at the time the Game is requesting
    #       a move from the player. (GameState)
    #   attackingAnt - A clone of the ant currently making the attack. (Ant)
    #   enemyLocation - A list of coordinate locations for valid attacks (i.e.
    #       enemies within range) ([list of 2-tuples of ints])
    #
    # Return: A coordinate that matches one of the entries of enemyLocations. ((int,int))
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]


    ##
    # registerWin
    # Description: The last method, registerWin, is called when the game ends and simply
    # indicates to the AI whether it has won or lost the game. This is to help with
    # learning algorithms to develop more successful strategies.
    #
    # Parameters:
    #   hasWon - True if the player has won the game, False if the player lost. (Boolean)
    #
    def registerWin(self, hasWon):
        # method templaste, not implemented
        pass

#Unit Test #1:
#verifies that a MOVE move updates the state properly.
#ant starts at (4,4) and moves to (4,3)
board = [[Location((col, row)) for row in xrange(0,BOARD_LENGTH)] for col in xrange(0,BOARD_LENGTH)]
neutralInventory = Inventory(NEUTRAL, [], [], 0)
oneAnt = Ant((4,4), WORKER, 1)
antArray = [oneAnt]
p1Inventory = Inventory(PLAYER_ONE, [], [], 0)
p2Inventory = Inventory(PLAYER_TWO, antArray, [], 3)
state = GameState(board, [p1Inventory, p2Inventory, neutralInventory], PLAY_PHASE, PLAYER_ONE)
move = Move(MOVE_ANT, [(4,4), (4,3)], PLAYER_TWO)
player = AIPlayer(PLAYER_TWO)
val = player.prediction(state, state, move)
twoAnt = Ant((4,3), WORKER, 1)
oneAntAft = state.inventories[PLAYER_TWO].ants[0]
if oneAntAft.coords == (4,3):
    print "Unit Test #1 passed"
else:
    print "Unit test did not pass."
    print "Ant should have been at (4,3), but instead, it is at:"
    print oneAntAft.coords