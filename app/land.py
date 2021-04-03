import terrain as te
import living as lv
import hex as pl
import collections
from typing import Dict

class Land:
	def __init__(self, radius:int, screen_size:int, terrain_size:int):
		self.terrain_size = terrain_size
		self.radius = radius
		self.layout = pl.Layout(pl.layout_pointy,
								pl.Point(terrain_size, terrain_size),
								pl.Point(screen_size // 2, screen_size // 2))

		# replace this map to switch from hexes to i.e. squares
		self.map = {p:te.Terrain(p) for p in pl.generate_hex_map(radius)}
		for k, v in self.map.items():
			v.neighbors = self.neighborhood(k, v)

	def __repr__(self):
		return 'Land(radius:{}, unit_size:{})'.format(self.radius, self.terrain_size)

	def __str__(self):
		return repr(self)
		
	def neighborhood(self, p:'Polygon', t:'te.Terrain'):
		neighborhood = {}
		for direction in range(len(pl.Directions)):
			n_coords = p.neighbor(direction)
			if (n_coords in self.map):
				neighborhood[pl.Directions[direction]] = self.map[n_coords]
		return neighborhood

	def polygon_corners(self, t:'te.Terrain'):
		return pl.polygon_corners(self.layout, t.polygon)

	def polygon_center(self, t:'te.Terrain'):
		return pl.hex_to_pixel(self.layout, t.polygon)

	def pixel_to_terrain(self, p:pl.Point):
		polygon = pl.pixel_to_hex(self.layout, p)
		if polygon in self.map:
			return self.map[polygon]
		return None

# Tests

def complain(name:str):
	print("FAIL {0}".format(name))

def equal_int(name:str, a:int, b:int):
	if not (a == b):
		complain(name)

def test_all():
	pass

if __name__ == '__main__':
	test_all()