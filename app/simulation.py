import pygame as pg
import terrain as te
import land as ld
import living as lv

import collections
from typing import Dict, List, Iterable
from dataclasses import dataclass

Point = collections.namedtuple('Point', ('x', 'y'))

@dataclass
class Terrain_package:
	terrain: te.Terrain
	color: pg.Color

@dataclass
class Land_package:
	land: ld.Land
	color: pg.Color
	redraw: bool = True

@dataclass
class Living_package:
	living: lv.Living
	color: pg.Color
	img: pg.Surface
	redraw: bool = True

def main():

	screen_size = 800
	land_radius = 5
	world_pace_ms = 1000

	pg.init()

	land_pack, life_packs = initialize_world(screen_size, land_radius)

	clock = pg.time.Clock()
	screen = pg.display.set_mode((screen_size, screen_size))

	elapsed_time = 0
	while True:
		events = pg.event.get()
		terrain_highlights = {}

		for e in events:
			if e.type == pg.QUIT:
				return
		
		elapsed_time += clock.get_time()
		q, mod = divmod(elapsed_time, world_pace_ms)
		if (q >= 1):
			print('elapsed_time: {}'.format(elapsed_time))
			print('q: {}, mod: {}'.format(q, mod))
			for i in range(q):
				update_world(life_packs, land_pack)
			elapsed_time = mod
		terrain_highlights = handle_events(events, land_pack, life_packs)
		draw(screen, land_pack, life_packs, terrain_highlights)
		clock.tick(60)

def living_img(text:str, text_size:int):
	font = pg.font.SysFont(None, text_size)
	return font.render(text, True, (255, 255, 255))


def initialize_world(screen_size:int, land_radius:int):
	land_pack = Land_package(land = ld.Land(land_radius, screen_size, 20),
				color = pg.Color(255, 255, 255))

	life_packs = {}

	pos1 = land_pack.land.map[(0, 0)]
	l1 = lv.Living('Adam', 'Adam', pos1)
	l1.state = lv.LivingState.SEARCHING
	p10 = list(l1.position.neighbors.values())[0]
	p11 = list(p10.neighbors.values())[0]
	p12 = list(p11.neighbors.values())[0]
	p13 = list(p12.neighbors.values())[0]
	l1.path = [p10, p11, p12, p13]
	life_packs[l1] = Living_package(living = l1,
							color = pg.Color(0, 255, 0),\
							img = living_img(l1.uid, land_pack.land.terrain_size))

	pos2 = list(land_pack.land.map.values())[-10]
	l2 = lv.Living('Eve', 'Eve', pos2)
	life_packs[l2] = Living_package(living = l2,
							color = pg.Color(255, 0, 0),
							img = living_img(l2.uid, land_pack.land.terrain_size))

	pos3 = list(land_pack.land.map.values())[12]
	l3 = lv.Living('Plissken', 'Plissken', pos3)
	life_packs[l3] = Living_package(living = l3,
							color = pg.Color(0, 0, 255),
							img = living_img(l3.uid, land_pack.land.terrain_size))

	return land_pack, life_packs

def update_world(life_packs: Dict[lv.Living, Living_package],
				land_pack:Land_package
				):

	for terrain in land_pack.land.map.values():
		terrain.decay()
		terrain.broadcast()

	for terrain in land_pack.land.map.values():
		terrain.update()

	life_packs = {l:i for l,i in life_packs.items() if l.state != lv.LivingState.DEAD}

	for l, l_info in life_packs.items():
		l.move()
		l_info.redraw = True

	for l, l_info in life_packs.items():
		l.act()

	land_pack.redraw = True

def handle_events(events:List,
				land_pack:Land_package,
				life_packs:Dict[lv.Living, Living_package]
				):

	t_highlights = {}
	for e in events:
		if e.type == pg.MOUSEBUTTONDOWN: # move to update_state
			if e.button == 1: # left click
				p = Point(*pg.mouse.get_pos())
				tar_terrain = land_pack.land.pixel_to_terrain(p)
				tar_terrain_neighbors = tar_terrain.neighbors if tar_terrain is not None else {}
				h_color = pg.Color(100, 100, 100)
				t_highlights = {t:Terrain_package(terrain = t, color = h_color) for (k, t) in tar_terrain_neighbors.items()}
				land_pack.redraw = True
				for living_info in life_pack.values():
					living_info.redraw = True

	
	for t in land_pack.land.map.values():
		if t.smells:
			max_smell_strength = max(s.strength for s in t.smells.values())
			strongest_smell = next(smell for smell in t.smells.values() if smell.strength == max_smell_strength)
			l = strongest_smell.source
			color = pg.Color(life_packs[l].color)
			inv_strength = round((100 -  max_smell_strength) * 2.55)
			color.r = max(0, color.r - inv_strength)
			color.g = max(0, color.g - inv_strength)
			color.b = max(0, color.b - inv_strength)
			t_highlights[t] = Terrain_package(terrain = t, color = color)

	return t_highlights
	

def draw(screen:pg.Surface,
		land_pack:Land_package,
		life_packs: Dict[lv.Living, Living_package],
		terrain_highlights:Dict[te.Terrain, Terrain_package]
		):

	if land_pack.redraw or any(l_pack.redraw for l_pack in life_packs.values()):
		screen.fill((0, 0, 0))
		draw_highlighted_terrain(screen, terrain_highlights, land_pack.land)
		draw_life(screen, life_packs, land_pack.land)
		draw_land(screen, land_pack)
		pg.display.flip()

def draw_land(screen:pg.Surface, land_pack:Land_package):
	if land_pack.redraw:
		for t in land_pack.land.map.values():
			pg.draw.polygon(screen, land_pack.color, land_pack.land.polygon_corners(t), width=1)
		land_pack.redraw = False

def draw_highlighted_terrain(screen:pg.Surface, terrain:Dict[te.Terrain, Terrain_package], land:ld.Land):
	for t, t_info in terrain.items():
		pg.draw.polygon(screen, t_info.color, land.polygon_corners(t), width=0)

def draw_life(screen:pg.Surface, life_packs:Dict[lv.Living, Living_package], land:ld.Land):
	for liv, l_pack in life_packs.items():
		if l_pack.redraw:
			draw_living(screen, liv.position, l_pack.color, l_pack.img, land)
			l_pack.redraw = False

def draw_living(screen:pg.Surface, position:te.Terrain, color:pg.Color, img:pg.Surface, land:ld.Land):
	#pg.draw.polygon(screen, color, land.polygon_corners(position), width=0)

	l_x, l_y = land.polygon_center(position)
	img_w, img_h = img.get_size()
	img_coord = (l_x - img_w//2, l_y - img_h//2)
	screen.blit(img, img_coord)

if __name__ == "__main__":
	main()