import pygame as pg
import land as ld
import living as lv
import collections
from typing import Dict, List, Iterable

Point = collections.namedtuple('Point', ('x', 'y'))
Color = collections.namedtuple('Color', ('R', 'G', 'B'))

class Land_Info:
	def __init__(self, color:Color):
		self.color = color
		self.redraw = True

class Living_Info:
	def __init__(self, color:Color, position:ld.Terrain):
		self.color = color
		self.position = position
		self.redraw = True

def main():

	screen_size = 800
	land_radius = 10

	land, life = initialize_world(screen_size, land_radius)

	pg.init()
	clock = pg.time.Clock()
	screen = pg.display.set_mode((screen_size, screen_size))
	
	while True:
		events = pg.event.get()

		for e in events:
			if e.type == pg.QUIT:
				return
		
		terrain_highlights = update_world(events, land, life)
		draw(screen, land, life, terrain_highlights)
		clock.tick(60)


def initialize_world(screen_size:int, land_radius:int):
	land = {'land': ld.Land(land_radius, screen_size),
			'info': Land_Info(Color(255, 255, 255))}

	life = {}
	pos = list(land['land'].map.values())[0]
	life[lv.Living('Adam', 'Adam', pos)] = Living_Info(Color(255, 0, 0), pos)

	return land, life

def update_world(events:List, land:Dict, life:Dict[lv.Living, Living_Info]):
	t_highlights = []
	for e in events:
		if e.type == pg.MOUSEBUTTONDOWN: # move to update_state
			if e.button == 1: # left click
				p = Point(*pg.mouse.get_pos())
				tar_terrain = land['land'].pixel_to_terrain(p)
				t_highlights = tar_terrain.neighbors.values() if tar_terrain is not None else []
				land['info'].redraw = True
				for living_info in life.values():
					living_info.redraw = True
	return t_highlights
	

def draw(screen:pg.Surface, land:Dict, life: Dict[lv.Living, Living_Info], terrain_highlights:Iterable[ld.Terrain]):
	if land['info'].redraw or any(info.redraw for info in life.values()):
		screen.fill((0, 0, 0))
		draw_life(screen, life, land['land'])
		draw_highlighted_terrain(screen, terrain_highlights, land['land'])
		draw_land(screen, land)
		pg.display.flip()

def draw_land(screen:pg.Surface, land:Dict):
	if land['info'].redraw:
		for t in land['land'].map.values():
			pg.draw.polygon(screen, land['info'].color, land['land'].polygon_corners(t), width=1)
		land['info'].redraw = False

def draw_highlighted_terrain(screen:pg.Surface, terrain:Iterable[ld.Terrain], land:ld.Land):
	for t in terrain:
		pg.draw.polygon(screen, (100, 100, 100), land.polygon_corners(t), width=0)

def draw_life(screen:pg.Surface, life:Dict[lv.Living, Living_Info], land:ld.Land):
	for liv, info in life.items():
		if info.redraw:
			draw_living(screen, info.position, info.color, land)
			info.redraw = False

def draw_living(screen:pg.Surface, position:ld.Terrain, color:Color, land:ld.Land):
	pg.draw.polygon(screen, color, land.polygon_corners(position), width=0)

if __name__ == "__main__":
	main()