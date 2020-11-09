import living
import hex as pl
import collections
from typing import Dict

Emission = collections.namedtuple('Emission', ('smells', 'placeholder'))

class Land:
	def __init__(self, radius:int, screen_size:int):
		self.layout = pl.Layout(pl.layout_pointy, pl.Point(10, 10), pl.Point(screen_size // 2, screen_size // 2))

		# replace this map to switch from hexes to i.e. squares
		self.map = {p:Terrain(p) for p in pl.generate_hex_map(radius)}
		for k, v in self.map.items():
			v.neighbors = self.neighborhood(k, v)
		
	def neighborhood(self, p:'Polygon', t:'Terrain'):
		neighborhood = {}
		for d in range(len(pl.Directions)):
			n_key = p.neighbor(d)
			if (n_key in self.map):
				neighborhood[n_key] = self.map[n_key]
		return neighborhood

	def polygon_corners(self, t:'Terrain'):
		return pl.polygon_corners(self.layout, t.polygon)

	def pixel_to_terrain(self, p:pl.Point):
		polygon = pl.pixel_to_hex(self.layout, p)
		if polygon in self.map:
			return self.map[polygon]
		return None

class Terrain:
	def __init__(self, p:'Polygon'):
		self.polygon = p
		self.smells = {}
		self.emission = Emission({}, {})
		self.neighbors = {}

	def __str__(self):
		return 'TUnit: ({})'.format('')
	
	def __repr__(self):
		return repr(self.polygon)

	def __hash__(self):
		return hash(self.polygon)

	def __eq__(self, other:'Terrain'):
		return (self.polygon) == (other.polygon)

	def update_broadcast(self):
		# update myself
		for smell in self.smells.values():
			smell.update()
		# broadcast updates
		em_smells = self.smells
		self.emission = Emission(em_smells, {})

	def receive_update(self):
		# receive information from neighbors' borders and update own stuff accordingly
		for n in self.neighbors():
			pass

	def update_smells(self):
		pass


		# list of smells, update all smells then send them to "border" (update 1)
		# On update 2 check borders of neighbors to update my own stuff (update 2)
		# location is then a hex. neighbors can be found by location.neighbors or smtg