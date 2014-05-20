import random
import socket

HOST = ""
PORT = 8888

CARDNUMS = [1]*15 + [2]*10 + [3]*10 + [4]*10 + [5]*5
CARDCOLS = 'rbygw'*10

class Card():
    num = 0
    color = ''

    possibColors = set()
    possibNums = set()

    def __init__(self, info):
        self.num = info[0]
        self.color = info[1]
        self.possibColors = set(['r', 'b', 'y', 'g', 'w'])
        self.possibNums = set([1,2,3,4,5])

    def __str__(self):
        return str(self.num) + self.color

    def getKnownInfoStr(self):
        if len(self.possibNums) == 5:
            numStr = '*'
        else:
            numStr = ''.join([str(x) for x in sorted(self.possibNums)])
        if len(self.possibColors) == 5:
            colorStr = '*'
        else:
            colorStr = ''.join(sorted(self.possibColors))
        return numStr + colorStr

    def setNotColor(self, color):
        self.possibColors.discard(color)

    def setNotNum(self, num):
        self.possibNums.discard(num)

    def setColor(self, color):
        #should fix this later
        self.possibColors = {color}

    def setNum(self, num):
        #should fix this later
        self.possibNums = {num}

    #player holding this card was just told info, which is a number
    #or a color. Update possible numbers and colors for this card
    #based on info received
    #return True if card was the same number/color as info received
    #return False otherwise
    def tellAbout(self, info):
        #note: need to check if info is int first to avoid exception
        #from checking if an int is in a string
        if info in range(1,6):
            if self.num == info:
                self.setNum(info)
                return True
            else:
                self.setNotNum(info)
                return False
        elif info in "rbygw":
            if self.color == info:
                self.setColor(info)
                return True
            else:
                self.setNotColor(info)
                return False
        else:
            print("OOPS!")



class Hanabi():
    #deck is a list of cards left in the deck
    deck = []
    
    #discard has keys as colors, and numbers in the list
    discard = {color:[] for color in 'rbygw'}
    #piles has keys as colors and a number representing
    #the current top card in the pile. 0 means empty
    piles = {color:0 for color in 'rbygw'}

    #players is a list of names of players in the game
    #they should be unique
    players = []
    #playerSockets maps player names to way to contact them
    playerSockets = {}
    #hands lists the hands of each player
    hands = {}
    
    #store number of tokens available
    numTokens = 8
    #store number of bombs available
    #note: loss is at 0 bombs instead of 1
    numBombs = 3

    #player whose turn is next
    curPlayerIdx = 0

    def shuffle(self):
        random.shuffle(self.deck)

    def draw(self):
        if len(self.deck) > 0:
            return self.deck.pop()
        else:
            return None

    def addPlayer(self, name, conn):
        self.players.append(name.lower())
        self.playerSockets[name.lower()] = conn

    def randomizePlayers(self):
        random.shuffle(self.players)

    def viewHands(self):
        for p in self.players:
            print(p + ':', ' '.join([str(c) for c in self.hands[p]]))

    def notifyPlayer(self, player, msg):
        self.playerSockets[player].send((msg + '\n').encode())

    def notifyAll(self, msg):
        for player in self.players:
            self.notifyPlayer(player, msg)

    #asks player for input continually until valid move is given
    #returns easily-parseable action of TBD formatting
    def getAction(self, player):
        inp = self.requestMove(player)
        parsed = self.validateAndParseInput(inp)
        while not parsed:
            self.notifyPlayer(player, "Invalid move!")
            inp = self.requestMove(player)
            parsed = self.validateAndParseInput(inp)
        return parsed

    def requestMove(self, player):
        self.playerSockets[player].send("Please enter your next move:".encode())
        return self.playerSockets[player].recv(1024).decode()

    def validateAndParseInput(self, inp):
        action = inp.lower().split()
        if action[0] == "discard" or action[0] == "d":
            if len(action) != 2:
                return False
            action[0] = "discard"
            try:
                action[1] = int(action[1])
            except ValueError:
                return False
        elif action[0] == "play" or action[0] == "p":
            if len(action) != 2:
                return False
            action[0] = "play"
            try:
                action[1] = int(action[1])
            except ValueError:
                return False
        elif action[0] == "tell" or action[0] == "t":
            if len(action) != 3:
                return False
            action[0] = "tell"
            if self.numTokens < 1:
                return False
            if action[1] not in self.players:
                return False
            if action[2] in "12345":
                action[2] = int(action[2])
            elif action[2] in "rbygw":
                pass
            else:
                return False
        else:
            return False
        return action


    def doAction(self, player, action):
        if action[0] == "discard":
            discarded = self.hands[player][action[1] - 1]
            self.discard[discarded.color].append(discarded.num)
            self.hands[player][action[1] - 1] = self.draw()
            if self.numTokens < 8:
                self.numTokens += 1

            self.notifyAll(player + " discarded " + str(discarded))
        elif action[0] == "play":
            played = self.hands[player][action[1] - 1]
            if self.piles[played.color] == played.num - 1:
                self.piles[played.color] = played.num
                if played.num == 5 and self.numTokens < 8:
                    self.numTokens += 1
                wasSuccessful = True
            else:
                self.discard[played.color].append(played.num)
                self.numBombs -= 1
                wasSuccessful = False
            self.hands[player][action[1] - 1] = self.draw()
            
            notifyStr = player + " played " + str(played) + " and "
            if wasSuccessful:
                notifyStr += "succeeded"
            else:
                notifyStr += "failed"
            self.notifyAll(notifyStr)
        elif action[0] == "tell":
            if self.numTokens > 0:
                self.numTokens -= 1
            else:
                print("OOPS!")
            cardNumsToldAbout = []
            for num, card in enumerate(self.hands[action[1]]):
                if card.tellAbout(action[2]):
                    cardNumsToldAbout.append(num)
            
            notifyStr = player + " tells " + action[1] + " that card"
            if len(cardNumsToldAbout) > 1:
                notifyStr += 's'
            notifyStr += ' ' + ' '.join([str(n+1) for n in cardNumsToldAbout])
            if len(cardNumsToldAbout) > 1:
                notifyStr += " are "
            else:
                notifyStr += " is "
            notifyStr += str(action[2])

            self.notifyAll(notifyStr)
        else:
            print("OOPS!")
            pass

    def setupGame(self):
        self.deck = [Card(c) for c in zip(CARDNUMS, CARDCOLS)]
        discard = {color:[] for color in 'rbygw'}
        piles = {color:0 for color in 'rbygw'}

        self.shuffle()
        self.randomizePlayers()
        if len(self.players) < 4:
            handSize = 5
        else:
            handSize = 4
        for p in self.players:
            self.hands[p] = [self.draw() for i in range(handSize)]
        self.numBombs = 3
        self.numTokens = 8

    def viewGameState(self):
        print("Tokens left:", self.numTokens)
        print("Bombs left:", self.numBombs + 1)
        print("Piles", self.piles)
        print("Discard", self.discard)
        self.viewHands()

    def notifyGameState(self, player):
        cardStr = "Cards left: " + str(len(self.deck))
        tokenStr = "Tokens left: " + str(self.numTokens)
        bombStr = "Bombs left: " + str(self.numBombs + 1)
        discardStr = "Discard: " + ' '.join([color+':'+''.join([str(i) for i in nums]) for color, nums in sorted(self.discard.items())])
        pileStr = "Piles: " + ' '.join([color+str(num) for color,num in self.piles.items()])

        knownInfoStrs = ["Known info for other players:"]
        for p in self.players:
            if p != player:
                knownInfoStrs.append(p + ': ' + ' '.join([c.getKnownInfoStr() if c is not None else "None" for c in self.hands[p]]))

        handStrs = ["Player hands:"]
        for p in self.players:
            if p != player:
                handStrs.append(p + ': ' + ' '.join([str(c) for c in self.hands[p]]))
            else:
                handStrs.append(p + ': ' + ' '.join([c.getKnownInfoStr() if c is not None else "None" for c in self.hands[p]]))

        notifyStr = '\n'.join([cardStr, tokenStr, bombStr, discardStr, '', pileStr] + [''] + knownInfoStrs + [''] + handStrs + [''])
        self.notifyPlayer(player, notifyStr)

    def notifyAllGameState(self):
        for player in self.players:
            self.notifyGameState(player)

    def takeTurn(self):
        print()
        player = self.players[self.curPlayerIdx]
        self.notifyAll("--------------------------------------")
        self.notifyAllGameState()
        self.notifyAll(player + "'s turn")
        act = self.getAction(player)
        self.doAction(player, act)
        if self.numBombs == 0:
            self.notifyAll("The fireworks explode! 0 points.")
            self.endGame()
        self.curPlayerIdx = (self.curPlayerIdx + 1) % len(self.players)

    def endGame(self):
        exit()

    def playGame(self):
        self.setupGame()
        self.notifyAll("Player order is " + ", ".join([str(p) for p in self.players]))

        curPlayerIdx = 0
        #play until there are no cards left in the deck
        while len(self.deck) > 0:
            self.takeTurn()
        #then everybody gets one more turn
        for i in range(len(self.players)):
            self.takeTurn()

        notifyStr = "Game over! Final score is " + str(sum(self.piles.values()))
        self.notifyAll(notifyStr)
        self.endGame()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(10)

numPlayers = 3
playerNames = []
conns = []
for i in range(numPlayers):
    print("Waiting for player", i+1)
    conn, addr = s.accept()
    conn.send("Please enter your name: ".encode())
    name = conn.recv(1024).decode()
    conns.append(conn)
    playerNames.append(name.strip())

h = Hanabi()
for p, c in zip(playerNames, conns):
    h.addPlayer(p, c)
h.playGame()