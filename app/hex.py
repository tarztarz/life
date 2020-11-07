# huge props to https://www.redblobgames.com/grids/hexagons/
import collections
import math
from typing import List, Callable, Any, Iterable

class Hex:
	def __init__(self, q:int, r:int, s:int):
		assert type(q) is int and type(r) is int and type(s) is int, 'Hex coordinates must be integers'
		assert q + r + s == 0, 'q({})+ r({}) + s({}) must be 0'.format(q, r, s)
		self.q = q
		self.r = r
		self.s = s

	def __str__(self):
		return 'Hex: ({}, {}, {})'.format(self.q, self.r, self.s)
	
	def __repr__(self):
		return "{q: '{}', r: '{}', s: '{}'}".format(self.q, self.r, self.s)

	def __add__(self, val:'Hex'):
		assert(type(val) is Hex), 'cannot add {} to Hex'.format(type(val))
		return Hex(self.q + val.q, self.r + val.r, self.s + val.s)
	
	def __sub__(self, val:'Hex'):
		assert(type(val) is Hex), 'cannot subtract {} from Hex'.format(type(val))
		return Hex(self.q - val.q, self.r - val.r, self.s - val.s)

	def __mul__(self, val:int):
		assert(type(val) is int), 'cannot multiple Hex by {}'.format(type(val))
		return Hex(self.q * val, self.r * val, self.s * val)
	
	def rotate_right(self):
		return Hex(-self.r, -self.s, -self.q)

	def __rshift__(self, val:int):
		# rotates Hex to the right 'val' ammount of times
		assert(type(val) is int), 'cannot right-shift Hex by {}'.format(type(val))
		h = self
		for i in range(val):
			h = h.rotate_right()
		return h
	
	def rotate_left(self):
		return Hex(-self.s, -self.q, -self.r)

	def __lshift__(self, val:int):
		# rotates Hex to the left 'val' ammount of times
		assert(type(val) is int), 'cannot left-shift Hex by {}'.format(type(val))
		h = self
		for i in range(val):
			h = h.rotate_left()
		return h

	def neighbor(self, direction:int):
		assert type(direction) is int, 'Hex direction must be an integer'
		assert direction in range(6), 'Hex only has 6 possible directions. {} was given'.format(direction)
		return self + Directions[direction]

	def diagonal(self, direction:int):
		assert type(direction) is int, 'Hex diagonal direction must be an integer'
		assert direction in range(6), 'Hex only has 6 possible diagonal directions. {} was given'.format(direction)
		return self + Diagonals[direction]

	def length(self):
		return (abs(self.q) + abs(self.r) + abs(self.s)) // 2

	def distanceTo(self, target:'Hex'):
		assert(type(target) is Hex), 'cannot calculate a distance between Hex and {}'.format(type(target))
		return (self - target).length()

class FractionalHex:
	def __init__(self, q:float, r:float, s:float):
		self.q = q
		self.r = r
		self.s = s

	def __str__(self):
		return 'FractionalHex: ({}, {}, {})'.format(self.q, self.r, self.s)
	
	def __repr__(self):
		return "{q: '{}', r: '{}', s: '{}'}".format(self.q, self.r, self.s)

	def round(self):
		qi = round(self.q)
		ri = round(self.r)
		si = round(self.s)
		q_diff = abs(qi - self.q)
		r_diff = abs(ri - self.r)
		s_diff = abs(si - self.s)
		if q_diff > r_diff and q_diff > s_diff:
			qi = -ri - si
		else:
			if r_diff > s_diff:
				ri = -qi - si
			else:
				si = -qi - ri
		return Hex(qi, ri, si)

Directions = (Hex(1, 0, -1), Hex(1, -1, 0), Hex(0, -1, 1), Hex(-1, 0, 1), Hex(-1, 1, 0), Hex(0, 1, -1))
Diagonals = (Hex(2, -1, -1), Hex(1, -2, 1), Hex(-1, -1, 2), Hex(-2, 1, 1), Hex(-1, 2, -1), Hex(1, 1, -2))

def hex_lerp(a:Hex, b:Hex, t:float):
	return FractionalHex(a.q * (1.0 - t) + b.q * t, a.r * (1.0 - t) + b.r * t, a.s * (1.0 - t) + b.s * t)

def draw_hex_line(a:Hex, b:Hex):
	dist = a.distanceTo(b)
	a_nudged = FractionalHex(a.q + 1e-06, a.r + 1e-06, a.s - 2e-06)
	b_nudged = FractionalHex(b.q + 1e-06, b.r + 1e-06, b.s - 2e-06)
	results = []
	step = 1.0 / max(dist, 1)
	for i in range(dist + 1):
		results.append(hex_lerp(a_nudged, b_nudged, step * i).round())
	return results

Orientation = collections.namedtuple("Orientation", ["f0", "f1", "f2", "f3", "b0", "b1", "b2", "b3", "start_angle"])
Layout = collections.namedtuple("Layout", ["orientation", "size", "origin"])

layout_pointy = Orientation(math.sqrt(3.0), math.sqrt(3.0) / 2.0, 0.0, 3.0 / 2.0, math.sqrt(3.0) / 3.0, -1.0 / 3.0, 0.0, 2.0 / 3.0, 0.5)
layout_flat = Orientation(3.0 / 2.0, 0.0, math.sqrt(3.0) / 2.0, math.sqrt(3.0), 2.0 / 3.0, 0.0, -1.0 / 3.0, math.sqrt(3.0) / 3.0, 0.0)

Point = collections.namedtuple('Point', ('x', 'y'))

def hex_to_pixel(layout:Layout, h:Hex):
	M = layout.orientation
	size = layout.size
	origin = layout.origin
	x = (M.f0 * h.q + M.f1 * h.r) * size.x
	y = (M.f2 * h.q + M.f3 * h.r) * size.y
	return Point(x + origin.x, y + origin.y)

def pixel_to_hex(layout:Layout, p:Point):
	M = layout.orientation
	size = layout.size
	origin = layout.origin
	pt = Point((p.x - origin.x) / size.x, (p.y - origin.y) / size.y)
	q = M.b0 * pt.x + M.b1 * pt.y
	r = M.b2 * pt.x + M.b3 * pt.y
	return FractionalHex(q, r, -q - r).round()

def hex_corner_offset(layout:Layout, corner:int):
	M = layout.orientation
	size = layout.size
	angle = 2.0 * math.pi * (M.start_angle - corner) / 6.0
	return Point(size.x * math.cos(angle), size.y * math.sin(angle))

def polygon_corners(layout:Layout, h:Hex):
	corners = []
	center = hex_to_pixel(layout, h)
	for i in range(0, 6):
		offset = hex_corner_offset(layout, i)
		corners.append(Point(center.x + offset.x, center.y + offset.y))
	return corners




# Tests

def complain(name:str):
	print("FAIL {0}".format(name))

def equal_hex(name:str, a:Hex, b:Hex):
	if not (a.q == b.q and a.s == b.s and a.r == b.r):
		complain(name)

def equal_int(name:str, a:int, b:int):
	if not (a == b):
		complain(name)

def equal_hex_array(name:str, a:List[Hex], b:List[Hex]):
	equal_int(name, len(a), len(b))
	for i in range(0, len(a)):
		equal_hex(name, a[i], b[i])

def test_hex_arithmetic():
	equal_hex("hex_add", Hex(4, -10, 6), Hex(1, -3, 2) + Hex(3, -7, 4))
	equal_hex("hex_subtract", Hex(-2, 4, -2), Hex(1, -3, 2) - Hex(3, -7, 4))

def test_hex_direction():
	equal_hex("hex_direction", Hex(0, -1, 1), Directions[2])

def test_hex_neighbor():
	equal_hex("hex_neighbor", Hex(1, -3, 2), Hex(1, -2, 1).neighbor(2))

def test_hex_diagonal():
	equal_hex("hex_diagonal", Hex(-1, -1, 2), Hex(1, -2, 1).diagonal(3))

def test_hex_distance():
	equal_int("hex_distance", 7, Hex(3, -7, 4).distanceTo(Hex(0, 0, 0)))

def test_hex_rotate_right():
	equal_hex("hex_rotate_right", Hex(1, -3, 2) >> 1, Hex(3, -2, -1))

def test_hex_rotate_left():
	equal_hex("hex_rotate_left", Hex(1, -3, 2) << 1, Hex(-2, -1, 3))

def test_hex_round():
	a = FractionalHex(0.0, 0.0, 0.0)
	b = FractionalHex(1.0, -1.0, 0.0)
	c = FractionalHex(0.0, -1.0, 1.0)
	equal_hex("hex_round 1", Hex(5, -10, 5), hex_lerp(FractionalHex(0.0, 0.0, 0.0), FractionalHex(10.0, -20.0, 10.0), 0.5).round())
	equal_hex("hex_round 2", a.round(), hex_lerp(a, b, 0.499).round())
	equal_hex("hex_round 3", b.round(), hex_lerp(a, b, 0.501).round())
	equal_hex("hex_round 4", a.round(), FractionalHex(a.q * 0.4 + b.q * 0.3 + c.q * 0.3, a.r * 0.4 + b.r * 0.3 + c.r * 0.3, a.s * 0.4 + b.s * 0.3 + c.s * 0.3).round())
	equal_hex("hex_round 5", c.round(), FractionalHex(a.q * 0.3 + b.q * 0.3 + c.q * 0.4, a.r * 0.3 + b.r * 0.3 + c.r * 0.4, a.s * 0.3 + b.s * 0.3 + c.s * 0.4).round())

def test_hex_linedraw():
	equal_hex_array("draw_hex_line", [Hex(0, 0, 0), Hex(0, -1, 1), Hex(0, -2, 2), Hex(1, -3, 2), Hex(1, -4, 3), Hex(1, -5, 4)], draw_hex_line(Hex(0, 0, 0), Hex(1, -5, 4)))

def test_layout():
	h = Hex(3, 4, -7)
	flat = Layout(layout_flat, Point(10.0, 15.0), Point(35.0, 71.0))
	equal_hex("layout", h, pixel_to_hex(flat, hex_to_pixel(flat, h)))
	pointy = Layout(layout_pointy, Point(10.0, 15.0), Point(35.0, 71.0))
	equal_hex("layout", h, pixel_to_hex(pointy, hex_to_pixel(pointy, h)))

def test_all():
	test_hex_arithmetic()
	test_hex_direction()
	test_hex_neighbor()
	test_hex_diagonal()
	test_hex_distance()
	test_hex_rotate_right()
	test_hex_rotate_left()
	test_hex_round()
	test_hex_linedraw()
	test_layout()

if __name__ == '__main__':
	test_all()