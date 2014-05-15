import random

CARDNUMS = '1'*15 + '2'*10 + '3'*10 + '4'*10 + '5'*5
CARDCOLS = 'rbgyw'* 10

class Hanabi():
	deck = []
	discard = []

	piles = {}

	players = []
	hands = {}
	
	numTokens = 0
	numBombs = 0

	def __init__(self):
		self.deck = list(zip(CARDNUMS, CARDCOLS))

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

	def startGame(self):
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
			print(p, self.hands[p])

	def notify(self, player, msg):
		print(player + ':', msg)

	def getInput(self, player):
		pIn = input()
		while not self.isValid(pIn):
			self.notify(p, "invalid input!")

h = Hanabi()
h.addPlayer('Frank')
h.addPlayer('Alison')
h.addPlayer('Arthur')
self.startGame()
h.viewHands()