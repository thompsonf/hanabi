import random

CARDNUMS = '1'*15 + '2'*10 + '3'*10 + '4'*10 + '5'*5
CARDCOLS = 'RBGYW'*10

class Card():
	num = ''
	color = ''

	notColors = set()
	notNums = set()

	def __init__(self, info):
		self.num = info[0]
		self.color = info[1]
		self.notColors = set()
		self.notNums = set()

	def __str__(self):
		return str(self.num) + self.color

	def setNotColor(self, color):
		self.notColors.add(color)

	def setNotNum(self, num):
		self.notNums.add(num)

	def setColor(self, color):
		#should fix this later
		for col in 'RBGYW':
			if col != color:
				self.notColors.add(col)

	def setNum(self, num):
		#should fix this later
		for i in '12345':
			if num != i:
				self.notNums.add(i)


class Hanabi():
	deck = []
	discard = []

	piles = {}

	players = []
	hands = {}
	
	numTokens = 0
	numBombs = 0

	def __init__(self):
		self.deck = [Card(c) for c in zip(CARDNUMS, CARDCOLS)]

	def shuffle(self):
		random.shuffle(self.deck)

	def draw(self, numCards):
		cardsDrawn = []
		while len(self.deck) > 0 and len(cardsDrawn) < numCards:
			cardsDrawn.append(self.deck.pop())
		return cardsDrawn

	def addPlayer(self, name):
		self.players.append(name)

	def randomizePlayers(self):
		random.shuffle(self.players)

	def playGame(self):
		self.shuffle()
		self.randomizePlayers()
		if len(self.players) < 4:
			handSize = 5
		else:
			handSize = 4
		for p in self.players:
			self.hands[p] = self.draw(handSize)

	def viewHands(self):
		for p in self.players:
			print(p + ':', ' '.join([str(c) for c in self.hands[p]]))

	def notify(self, player, msg):
		print(player + ':', msg)

	#asks player for input continually until valid move is given
	#returns easily-parseable action of TBD formatting
	def getInput(self, player):
		pIn = input()
		while not self.isValid(pIn):
			self.notify(p, "invalid input!")
		return pIn

	def doAction(player, action):
		if action[0] == "discard":
			pass
		elif action[0] == "play":
			pass
		elif action[0] == "tell":
			pass
		else:
			print("OOPS!")
			pass


h = Hanabi()
h.addPlayer('Frank')
h.addPlayer('Alison')
h.addPlayer('Arthur')
h.playGame()
h.viewHands()