import pygame as pg
import hex
from typing import Dict, Any

def main():

	terrain_radius = 3
	hex_map = hex.generate_hex_map(3)
	layout = hex.Layout(hex.layout_pointy, hex.Point(20, 20), hex.Point(200, 200))

	pg.init()
	screen = pg.display.set_mode((400, 400))
	done = False
	
	while not done:
		for event in pg.event.get():
				if event.type == pg.QUIT:
						done = True
		
		#pg.draw.rect(screen, (0, 128, 255), pg.Rect(30, 30, 60, 60))
		draw_terrain(screen, layout, hex_map)

		pg.display.flip()

def draw_terrain(screen:pg.Surface, layout:hex.Layout, hex_map:Dict[hex.Hex, Any]):
	for h in hex_map:
		pg.draw.polygon(screen, (255, 255, 255), hex.polygon_corners(layout, h), width=1)

if __name__ == "__main__":
	main()