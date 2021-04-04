import living as lv
import collections

Emission = collections.namedtuple('Emission', ('smells',))

class Terrain:
	def __init__(self, p:'Polygon'):
		self.polygon = p
		self.smells = {}
		self.emission = Emission({})
		self.neighbors = {} #Dict[Polygon, Terrain]

	def __repr__(self):
		return 'Terrain(coords:{}, smells:{})'.format(self.polygon, len(self.smells))

	def __str__(self):
		return '{}'.format(self.polygon)

	def __hash__(self):
		return hash(self.polygon)

	def __eq__(self, other:'Terrain'):
		return (self.polygon) == (other.polygon)

	def decay(self):
		self.smells = {source: lv.decay_smell(s) for (source, s) in self.smells.items() if lv.decay_smell(s).strength > 0}

	def broadcast(self):
		em_smells = {k:lv.Smell(k, v.strength) for (k, v) in self.smells.items()}
		self.emission = Emission(em_smells)

	def update(self):
		self.update_smells()

	def update_smells(self):
		inc_smells = {}
		for n in self.neighbors.values():
			for n_source, n_smell in n.emission.smells.items():
				if n_source not in inc_smells:
					inc_smells[n_source] = lv.Smell(n_source, n_smell.strength)
				else:
					max_inc_strength = max(inc_smells[n_source].strength, n_smell.strength)
					inc_smells[n_source] = lv.Smell(n_source, max_inc_strength)

		for k in (set(inc_smells.keys()) | set(self.smells.keys())):
			if k not in self.smells:
				self.smells[k] = inc_smells[k]
			elif k in inc_smells:
				self.smells[k] = inc_smells[k] if inc_smells[k].strength > self.smells[k].strength else self.smells[k]
			elif k not in inc_smells:
				pass

	def direction_to(self, neighbor:'Terrain'):
		return neighbor.polygon - self.polygon

	def neighbor(self, direction:'Polygon'):
		return self.neighbors[direction]



# Tests

def complain(name:str):
	print("FAIL {0}".format(name))

def equal_terrain(name:str, a:Terrain, b:Terrain):
	if not (a == b):
		complain(name)

def equal_int(name:str, a:int, b:int):
	if not (a == b):
		complain(name)

def equal_emission(name:str, a:Emission, b:Emission):
	if not (a == b):
		complain(name)

class test_polygon:
	def __init__(self, q:int, r:int, s:int):
		self.q = q
		self.r = r
		self.s = s

	def __hash__(self):
		return hash((self.q, self.r))

	def __eq__(self, other:'Any'):
		if (isinstance(other, test_polygon)):
			return (self.q, self.r) == (other.q, other.r)
		else:
			return (self.q, self.r) == (other[0], other[1])

def test_terrain():
	a = Terrain(test_polygon(0, 0, 0))
	b = Terrain(test_polygon(0, 0, 0))
	equal_terrain('terrain comparison', a, b)

	l = lv.Living(0, 'Test Living', a)
	a.smells[l] = lv.Smell(l, 100)
	a.decay()
	equal_int('decay', a.smells[l].strength, 80)
	a.decay()
	equal_int('decay', a.smells[l].strength, 60)

	a.broadcast()
	equal_int('broadcast', a.emission.smells[l].strength, 60)

	a.decay()
	equal_int('decay', a.smells[l].strength, 40)
	equal_int('broadcast after decay', a.emission.smells[l].strength, 60)

def test_terrain_update():
	a = Terrain(test_polygon(0, 0, 0))
	b = Terrain(test_polygon(0, -1, 1))
	c = Terrain(test_polygon(0, -2, 2))
	d = Terrain(test_polygon(0, -3, 3))

	a.neighbors = {b.polygon:b, c.polygon:c}
	b.neighbors = {a.polygon:a, c.polygon:c, d.polygon:d}
	c.neighbors = {a.polygon:a, b.polygon:b, d.polygon:d}
	d.neighbors = {b.polygon:b, c.polygon:c}

	l = lv.Living(0, 'Test Living', a)

	a.smells[l] = lv.Smell(l, 100)
	a.decay()
	b.decay()
	c.decay()
	d.decay()
	equal_int('decay a1', a.smells[l].strength, 80)

	a.broadcast()
	b.broadcast()
	c.broadcast()
	d.broadcast()
	equal_int('broadcast a1', a.emission.smells[l].strength, 80)

	a.update()
	b.update()
	c.update()
	d.update()
	equal_int('update a1', a.smells[l].strength, 80)
	equal_int('update b1', b.smells[l].strength, 80)
	equal_int('update c1', c.smells[l].strength, 80)

	a.smells[l] = lv.Smell(l, 100)
	a.decay()
	b.decay()
	c.decay()
	d.decay()
	equal_int('decay a2', a.smells[l].strength, 80)
	equal_int('decay b2', b.smells[l].strength, 60)
	equal_int('decay c2', c.smells[l].strength, 60)

	a.broadcast()
	b.broadcast()
	c.broadcast()
	d.broadcast()
	equal_int('broadcast a2', a.emission.smells[l].strength, 80)
	equal_int('broadcast b2', b.emission.smells[l].strength, 60)
	equal_int('broadcast c2', c.emission.smells[l].strength, 60)

	a.update()
	b.update()
	c.update()
	d.update()

	equal_int('update a2', a.smells[l].strength, 80)
	equal_int('update b2', b.smells[l].strength, 80)
	equal_int('update c2', c.smells[l].strength, 80)
	equal_int('update d2', d.smells[l].strength, 60)

def test_all():
	test_terrain()
	test_terrain_update()

if __name__ == '__main__':
	test_all()