import pygame as pg
import land as ld
import collections
from typing import Dict, Any

def main():

	screen_size = 800
	terrain_radius = 10

	land = ld.Land(terrain_radius, screen_size)

	pg.init()
	screen = pg.display.set_mode((screen_size, screen_size))
	done = False
	
	while not done:
		for event in pg.event.get():
				if event.type == pg.QUIT:
						done = True
		
		#pg.draw.rect(screen, (0, 128, 255), pg.Rect(30, 30, 60, 60))
		draw_land(screen, land)

		pg.display.flip()

def draw_land(screen:pg.Surface, land:ld.Land):
	for p in land.map:
		pg.draw.polygon(screen, (255, 255, 255), land.polygon_corners(p), width=1)

if __name__ == "__main__":
	main()