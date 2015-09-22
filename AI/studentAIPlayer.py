# -*- coding: latin-1 -*-
import random
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import *
from Move import Move
from GameState import addCoords
from AIPlayerUtils import *


##
# AIPlayer
# Description: The responsbility of this class is to interact with the game by
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
        super(AIPlayer, self).__init__(inputPlayerId, "ALPHA")

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
                        # Just need to make the space non-empty. So I threw whatever I felt like in there.
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
                        # Just need to make the space non-empty. So I threw whatever I felt like in there.
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

        for move in moveList:
            moveEvals.append(self.prediction(currentState.clone(), currentState.clone(), move))

        bestMove = 0.0
        bestIndex = 0
        for i in range(0, len(moveEvals)):
            if moveEvals[i] == 1.0:
                return moveList[i]
            elif moveEvals[i] > bestMove:
                bestMove = moveEvals[i]
                bestIndex = i
        print moveEvals[bestIndex]
        return moveList[bestIndex]


    def prediction(self, prevState, currentState, move):
        if move.moveType == MOVE_ANT:
            startCoord = move.coordList[0]
            endCoord = move.coordList[-1]

            #take ant from start coord
            antToMove = currentState.board[startCoord[0]][startCoord[1]].ant
            #change ant's coords and hasMoved status
            antToMove.coords = (endCoord[0], endCoord[1])
            antToMove.hasMoved = True
            #remove ant from location
            currentState.board[startCoord[0]][startCoord[1]].ant = None
            #put ant at last loc in coordList
            currentState.board[endCoord[0]][endCoord[1]].ant = antToMove
            return self.pointValue(prevState, currentState)
        elif move.moveType == BUILD:
            coord = move.coordList[0]
            currentPlayerInv = currentState.inventories[currentState.whoseTurn]

            #subtract the cost of the item from the player's food count
            if move.buildType == TUNNEL:
                currentPlayerInv.foodCount -= CONSTR_STATS[move.buildType][BUILD_COST]

                tunnel = Building(coord, TUNNEL, currentState.whoseTurn)
                currentState.board[coord[0]][coord[1]].constr = tunnel
            else:
                currentPlayerInv.foodCount -= UNIT_STATS[move.buildType][COST]

                ant = Ant(coord, move.buildType, currentState.whoseTurn)
                ant.hasMoved = True
                currentState.board[coord[0]][coord[1]].ant = ant
                currentState.inventories[currentState.whoseTurn].ants.append(ant)

            return self.pointValue(prevState, currentState)

    def pointValue(self, prevState, currentState):
        myID = self.playerId
        oppID = PLAYER_ONE

        if myID == PLAYER_ONE:
            oppID = PLAYER_TWO

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

        # Better
        if currentState.inventories[myID].getQueen().health > \
            currentState.inventories[oppID].getQueen().health:
            runTotal += 0.85
            numChecks += 1
            print "better than other queen"

        # Good
        if currentState.inventories[myID].foodCount > \
                prevState.inventories[oppID].foodCount:
            runTotal += 0.65
            numChecks += 1
            #print "more food"

        #enemy before and after inventories
        enemyInvPrev = prevState.inventories[oppID]
        enemyInvAft = currentState.inventories[oppID]

        #my before and after inventories
        myInvPrev = prevState.inventories[myID]
        myInvAft = currentState.inventories[myID]
        #my ant list
        myAntListPrev = myInvPrev.ants
        myAntListAft = myInvAft.ants
        #workers before and after
        workerPrev = []
        workerAft = []
        workerPrevCarrying = []
        workerPrevNot = []
        workerAftCarrying = []
        workerAftNot = []
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

        #kill enemy ant
        enemyAntCountPrev = len(enemyInvPrev.ants)
        enemyAntCountAft = len(enemyInvAft.ants)
        if enemyAntCountAft < enemyAntCountPrev:
            runTotal+= 0.65
            numChecks += 1
            print "killed enemy ant"

        #enemy structure health reduced
        enemyTunnelPrevHealth = enemyInvPrev.constrs[1].captureHealth
        enemyTunnelAftHealth = enemyInvAft.constrs[1].captureHealth

        enemyHillPrevHealth = enemyInvPrev.constrs[0].captureHealth
        enemyHillAftHealth = enemyInvAft.constrs[0].captureHealth

        if enemyTunnelAftHealth < enemyTunnelPrevHealth or enemyHillPrevHealth < enemyHillAftHealth:
            runTotal+=0.65
            numChecks +=1
            print "damaged enemy ant hill"
        #get closer to ant on own side


        #ants that aren't carrying get closer to food
        if len(workerPrevNot) < len(workerAftNot):
            runTotal += 0.9
            numChecks +=1
            print "ant is now carrying"

        closestFoodDist = 99999
        closestFoodCoord = None
        foodCoords = []
        for x in range(0, 10):
            for y in range(0,4):
                currItem = getConstrAt(currentState, (x,y))
                #print(currItem)
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
                    closestFoodCoord = coord
            closestDistancesPrev.append(closestFoodDist)
            closestCoordsPrev.append(closestFoodCoord)
            sumPrev += closestFoodDist
        closestFoodDist = 99999
        closestFoodCoord = None
        closestDistancesAft = []
        closestCoordsAft = []
        for ant in workerAftNot:
            for coord in foodCoords:
                currDist = stepsToReach (currentState, ant.coords, coord)
                if currDist < closestFoodDist:
                    closestFoodDist = currDist
                    closestFoodCoord = coord
            closestDistancesAft.append(closestFoodDist)
            closestCoordsAft.append(closestFoodCoord)
            sumAft += closestFoodDist
        if sumAft < sumPrev:
            runTotal+=0.8
            numChecks +=1

        #ants that are carrying get closer to tunnel
        #workerPrevCarrying
        #worerAftCarrying
        tunnelCoords = []
        for x in range(0, 10):
            for y in range(0,4):
                currItem = getConstrAt(currentState, (x,y))
                #print(currItem)
                if currItem != None and (currItem.type == ANTHILL or currItem.type == TUNNEL):
                    tunnelCoords.append(currItem.coords)
        closestTunnDist = 99999
        closestPrevDist = 0
        for ant in workerPrevCarrying:
            for coord in tunnelCoords:
                currDist = stepsToReach(prevState, ant.coords, coord)
                if currDist < closestTunnDist:
                    closestTunnDist = currDist
            closestPrevDist += closestTunnDist

        closestTunnDist = 99999
        closestAftDist = 0
        for ant in workerAftCarrying:
            for coord in tunnelCoords:
                currDist = stepsToReach(currentState, ant.coords, coord)
                if currDist < closestTunnDist:
                    closestTunnDist = currDist
            closestAftDist += closestTunnDist

        if closestAftDist < closestPrevDist:
            runTotal+=0.8
            numChecks +=1


        # for ant in workerPrevCarrying:
        #     for coord in tunnelCoords:
                #currDist = stepsToReach()





        # Neutral


        # Bad


        # Worse

        if numChecks == 0:
            print "zeroooo"
            return 0.01
        return (runTotal/numChecks)

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
        return None


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
