import random
import land as ld
from enum import Enum
from typing import NamedTuple

class LivingState(Enum): # TODO: implement as class with getter and setters
	SEARCHING = 1
	HUNTING = 2
	RESTING = 3
	FIGHTING = 4
	DEAD = 5

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

		# fighting variables
		self.targets = []
		self.max_hp = 10
		self.hp_regen = 1
		self.current_hp = self.max_hp
		self.attack_strength = 5
		self.defense_strength = 0
		self.incoming_damage = {} #Dict[Living(Source), int]

	def __repr__(self):
		return 'Living(uid:{}, name:{}, position:{}, state:{})'.format(self.uid, self.name, self.position, self.state)
	
	def __str__(self):
		return '{} at {} {}'.format(self.name, self.position, self.state)

	def __hash__(self):
		return hash(self.uid)

	def __eq__(self, other:'Living'):
		return self.uid == other.uid

	def generateSmell(self):
		return Smell(self, 100)

	def attack(self, source:'Living', damage:int):
		self.incoming_damage[source] = damage

	def follow_path(self):
		last_position = self.position
		if len(self.path) > 0:
			self.position = self.path.pop(0)
			self.last_direction = last_position.direction_to(self.position)

	def set_state(self, l_state:LivingState, aura:'Smell' = None, target:'Living' = None): #TODO smell, for now
		if l_state == LivingState.SEARCHING:
			self.hunt_smell = None
			self.targets = []
			self.state = LivingState.SEARCHING

		elif l_state == LivingState.HUNTING:
			self.hunt_smell = aura
			self.targets = []
			self.state = LivingState.HUNTING

		elif l_state == LivingState.RESTING:
			self.hunt_smell = None
			self.targets = []
			self.state = LivingState.RESTING

		elif l_state == LivingState.FIGHTING:
			self.hunt_smell = None
			self.targets.append(target)
			self.state = LivingState.FIGHTING

		elif l_state == LivingState.DEAD:
			self.state = LivingState.DEAD

	def update_state(self): # search for whatever it is that drives me. Implement simple any smell search first
		
		if self.current_hp <= 0:
			self.set_state(LivingState.DEAD)
			print(f'{self} died!')

		elif self.state == LivingState.SEARCHING:
			interesting_smells = list(x for x in self.position.smells.values() if x.source != self)
			if len(interesting_smells) > 0:
				strongest_smell = max(interesting_smells, key=lambda x: x.strength)
				self.set_state(LivingState.HUNTING, strongest_smell)
				print('{} caught a scent: {}'.format(self, self.hunt_smell))

		elif self.state == LivingState.HUNTING:
			prey = self.hunt_smell.source

			if prey.position in self.position.neighbors.values():
				self.set_state(LivingState.FIGHTING, target = prey)
				print(f'{self} engaged its prey!')

			elif prey not in self.position.smells:
				self.set_state(LivingState.SEARCHING)
				print('{} lost its prey!'.format(self))
				
			elif self.position.smells[prey].strength > self.hunt_smell.strength:
				self.hunt_smell = self.position.smells[prey]

		elif self.state == LivingState.FIGHTING:
			prey = self.targets[0] if len(self.targets) > 0 else None

			if prey is None or prey.state == LivingState.DEAD:
				self.set_state(LivingState.SEARCHING)
				print(f'{self} killed its prey!')

			else:
				if prey.position in self.position.neighbors.values():
					prey.attack(self, self.attack_strength)

				else:
					self.set_state(LivingState.HUNTING, self.position.smells[prey])


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
				print('candidates:')
				for candidate in step_candidates:
					print('{} (strength: {})'.format(candidate, candidate.smells[prey].strength))
				print('next_step: {}'.format(next_step))
			else:
				next_step = random.choice(list(pos_neighbors))
				print('{} struggles to find {}!'.format(self, prey))
			self.path = [next_step]

	def update_hp(self):
		self.current_hp = min(self.max_hp, self.current_hp + self.hp_regen)

		for dmg in self.incoming_damage.values():
			actual_dmg = max(0, dmg - self.defense_strength)
			self.current_hp = max(0, self.current_hp - actual_dmg)

		self.incoming_damage = {}

	def move(self):
		self.follow_path()
		self.position.smells[self] = self.generateSmell()

	def act(self):
		self.update_hp()
		self.update_state()
		self.update_path()

class Smell(NamedTuple):
	source: Living
	strength: int

	def __repr__(self):
		return 'Smell(source:{}, strength:{})'.format(self.source, self.strength)
	
	def __str__(self):
		return 'smell from {} with {} strength'.format(self.source, self.strength)

def decay_smell(smell:Smell):
	return Smell(smell.source, smell.strength - smell.source.smell_decay_strength)
