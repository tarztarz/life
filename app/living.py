import collections
import land as ld

class Living:
	def __init__(self, uid:int, name:str, position:'ld.Terrain'):
		self.uid = uid
		self.name = name
		self.position = position
		self.smell_decay_strength = 20

	def __str__(self):
		return 'LIVING(name: {})'.format(self.name)
	
	def __repr__(self):
		return str(self)

	def __hash__(self):
		return hash(self.uid)

	def __eq__(self, other:'Living'):
		return self.uid == other.uid

	def generateSmell(self):
		return Smell(self, 100)

	def generateSound(self):
		return 100
	
	def update(self):
		#self.move()
		self.position.smells[self] = self.generateSmell()

Smell = collections.namedtuple('Smell', ('source', 'strength'))
def decay_smell(smell:Smell):
	return Smell(smell.source, smell.strength - smell.source.smell_decay_strength)
