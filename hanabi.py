import random

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

    def tellAbout(self, info):
        #note: need to check if info is int first to avoid exception
        #from checking if an int is in a string
        if info in range(1,6):
            if self.num == info:
                self.setNum(info)
            else:
                self.setNotNum(info)
        elif info in "rbygw":
            if self.color == info:
                self.setColor(info)
            else:
                self.setNotColor(info)
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

    def addPlayer(self, name):
        self.players.append(name.lower())

    def randomizePlayers(self):
        random.shuffle(self.players)

    def viewHands(self):
        for p in self.players:
            print(p + ':', ' '.join([str(c) for c in self.hands[p]]))

    def notifyPlayer(self, player, msg):
        print(player + ':', msg)

    def notifyAll(self, msg):
        #for player in self.players:
        #    self.notifyPlayer(player, msg)
        print("All:", msg)

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
        return input()

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
            for card in self.hands[action[1]]:
                card.tellAbout(action[2])
            self.notifyAll(player + " told " + action[1] + " about " + str(action[2]))
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
        pileStr = "Piles: " + ' '.join([color+str(num) for color,num in self.piles.items()])
        discardStr = "Discard: " + ' '.join([color+':'+''.join([str(i) for i in nums]) for color, nums in self.discard.items()])

        handStrs = []
        for p in self.players:
            if p != player:
                handStrs.append(p + ': ' + ' '.join([str(c) for c in self.hands[p]]))
            else:
                handStrs.append(p + ': ' + ' '.join([c.getKnownInfoStr() for c in self.hands[p]]))

        for nStr in [cardStr, tokenStr, bombStr, pileStr, discardStr] + handStrs:
            self.notifyPlayer(player, nStr)

    def takeTurn(self):
        print()
        player = self.players[self.curPlayerIdx]
        self.notifyGameState(player)
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
        self.notifyAll("Player order is " + str(self.players))

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


h = Hanabi()
h.addPlayer('Frank')
h.addPlayer('Alison')
h.addPlayer('Arthur')
h.playGame()