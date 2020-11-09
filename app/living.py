import land as ld

class Living:
	def __init__(self, uid:int, name:str, position:'ld.Terrain'):
		self.uid = uid
		self.name = name
		self.position = position

	def __str__(self):
		return 'LIVING: (name: {})'.format(self.name)
	
	def __repr__(self):
		return "{uid: '{}', name: '{}}".format(self.uid, self.name)

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
		#self.position.smells.append(self.generateSmell())
		pass

class Smell:
	def __init__(self, source:Living, strength:int):
		self.source = source
		self.strength = strength

	def __str__(self):
		return 'SMELL: (source: {}, strength: {})'.format(self.source.name, self.strength)
	
	def __repr__(self):
		return "{source: '{}', strength: '{}}".format(self.source.name, self.strength)

	def decay(self):
		self.strength = round(0.9 * self.strength)

	def update(self):
		self.decay()
