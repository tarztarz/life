import collections
import random
import land as ld
from enum import Enum

class LivingState(Enum): # TODO: implement as class with getter and setters
	SEARCHING = 1
	HUNTING = 2
	RESTING = 3

class Living:
	def __init__(self, uid:int, name:str, position:'ld.Terrain'):
		self.uid = uid #str
		self.name = name #str
		self.position = position #Terrain
		self.last_direction = None #ld.Directions
		self.path = [] #List[Terrain]
		self.state = LivingState.RESTING
		self.hunt_smell = None #Smell / change to aura later
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

	def follow_path(self):
		last_position = self.position
		if len(self.path) > 0:
			self.position = self.path.pop(0)
			self.last_direction = last_position.direction_to(self.position)

	def update_state(self): # search for whatever it is that drives me. Implement simple any smell search first
		if self.state == LivingState.SEARCHING:
			interesting_smells = list(x for x in self.position.smells.values() if x.source != self)
			if len(interesting_smells) > 0:
				self.hunt_smell = max(interesting_smells, key=lambda x: x.strength)
				print('{} caught a scent! {}'.format(self, self.hunt_smell))
				self.state = LivingState.HUNTING

		elif self.state == LivingState.HUNTING:
			prey = self.hunt_smell.source
			if prey not in self.position.smells:
				self.hunt_smell = None
				self.state = LivingState.SEARCHING
				print('{} lost its prey!'.format(self))
				
			elif self.position.smells[prey].strength > self.hunt_smell.strength:
				self.hunt_smell = self.position.smells[prey]

	def update_path(self):
		if self.state == LivingState.RESTING:
			self.path = []
		elif self.state == LivingState.SEARCHING:
			self.path = [random.choice(list(self.position.neighbors.values()))]
		elif self.state == LivingState.HUNTING:
			prey = self.hunt_smell.source
			pos_neighbors = self.position.neighbors.values()
			step_candidates = list(x for x in pos_neighbors if prey in x.smells and x.smells[prey].strength >= self.hunt_smell.strength)
			if len(step_candidates) > 0:
				next_step = max(step_candidates, key=lambda x: x.smells[prey].strength)
				print('current: {} ({})'.format(self.position, self.position.smells[prey].strength))
				print('candidates:\n')
				for candidate in step_candidates:
					print('{} (strength: {})'.format(candidate, candidate.smells[prey].strength))
				print('next_step: {}'.format(next_step))
			else:
				next_step = random.choice(list(pos_neighbors))
				print('{} struggles to find {}!'.format(self, prey))
			self.path = [next_step]

	def move(self):
		self.follow_path()
		self.position.smells[self] = self.generateSmell()

	def act(self):
		self.update_state()
		self.update_path()

Smell = collections.namedtuple('Smell', ('source', 'strength'))
def decay_smell(smell:Smell):
	return Smell(smell.source, smell.strength - smell.source.smell_decay_strength)
