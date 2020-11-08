import pygame as pg
import land as ld
import collections
from typing import Dict, List, Any

Point = collections.namedtuple('Point', ('x', 'y'))

def main():

	screen_size = 800
	terrain_radius = 10

	land = ld.Land(terrain_radius, screen_size)

	pg.init()
	clock = pg.time.Clock()
	screen = pg.display.set_mode((screen_size, screen_size))
	
	while True:
		redraw_land = True
		for e in pg.event.get():
			if e.type == pg.QUIT:
				return
			
			if e.type == pg.MOUSEBUTTONDOWN:
				if e.button == 1: # left click
					screen.fill((0, 0, 0))
					p = Point(*pg.mouse.get_pos())
					draw_highlight_neighbors(screen, land.pixel_to_terrain(p), land)
					redraw_land = True
		
		#pg.draw.rect(screen, (0, 128, 255), pg.Rect(30, 30, 60, 60))
		if redraw_land:
			draw_land(screen, land)
			redraw_land= False

		pg.display.flip()
		clock.tick(60)

def draw_land(screen:pg.Surface, land:ld.Land):
	for t in land.map.values():
		pg.draw.polygon(screen, (255, 255, 255), land.polygon_corners(t), width=1)

def draw_highlight_terrain(screen:pg.Surface, terrain:Dict[Any, ld.Terrain], land:ld.Land):
	for t in terrain.values():
		pg.draw.polygon(screen, (100, 100, 100), land.polygon_corners(t), width=0)

def draw_highlight_neighbors(screen:pg.Surface, t:ld.Terrain, land:ld.Land):
	draw_highlight_terrain(screen, t.neighbors, land)

if __name__ == "__main__":
	main()