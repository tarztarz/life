import pygame as pg
import land as ld
import living as lv
import collections
from typing import Dict, List, Iterable

Point = collections.namedtuple('Point', ('x', 'y'))

class Draw_Info:
	def __init__(self, color:pg.Color):
		self.color = color
		self.redraw = True

class Living_Info:
	def __init__(self, color:pg.Color, img:pg.Surface):
		self.color = color
		self.redraw = True
		self.img = img

def main():

	screen_size = 800
	land_radius = 5
	world_pace_ms = 1000

	pg.init()

	land, life = initialize_world(screen_size, land_radius)

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
				update_world(life, land)
			elapsed_time = mod
		terrain_highlights = handle_events(events, land, life)
		draw(screen, land, life, terrain_highlights)
		clock.tick(60)

def living_img(text:str, text_size:int):
	font = pg.font.SysFont(None, text_size)
	return font.render(text, True, (255, 255, 255))


def initialize_world(screen_size:int, land_radius:int):
	land = {'land': ld.Land(land_radius, screen_size, 20),
			'info': Draw_Info(pg.Color(255, 255, 255))}

	life = {}

	pos1 = land['land'].map[(0, 0)]
	l1 = lv.Living('Adam', 'Adam', pos1)
	l1.state = lv.LivingState.SEARCHING
	p10 = list(l1.position.neighbors.values())[0]
	p11 = list(p10.neighbors.values())[0]
	p12 = list(p11.neighbors.values())[0]
	p13 = list(p12.neighbors.values())[0]
	l1.path = [p10, p11, p12, p13]
	life[l1] = Living_Info(pg.Color(0, 255, 0), living_img(l1.uid, land['land'].terrain_size))

	pos2 = list(land['land'].map.values())[-10]
	l2 = lv.Living('Eve', 'Eve', pos2)
	life[l2] = Living_Info(pg.Color(255, 0, 0), living_img(l2.uid, land['land'].terrain_size))

	pos3 = list(land['land'].map.values())[12]
	l3 = lv.Living('Plissken', 'Plissken', pos3)
	life[l3] = Living_Info(pg.Color(0, 0, 255), living_img(l3.uid, land['land'].terrain_size))

	return land, life

def update_world(life: Dict[lv.Living, Draw_Info], land:Dict):
	for terrain in land['land'].map.values():
		terrain.decay()
		terrain.broadcast()

	for terrain in land['land'].map.values():
		terrain.update()

	for l, l_info in life.items():
		l.move()
		l_info.redraw = True

	for l, l_info in life.items():
		l.act()

	land['info'].redraw = True

def handle_events(events:List,
				land:Dict,
				life:Dict[lv.Living, Living_Info]
				):

	t_highlights = {}
	for e in events:
		if e.type == pg.MOUSEBUTTONDOWN: # move to update_state
			if e.button == 1: # left click
				p = Point(*pg.mouse.get_pos())
				tar_terrain = land['land'].pixel_to_terrain(p)
				tar_terrain_neighbors = tar_terrain.neighbors if tar_terrain is not None else {}
				h_color = pg.Color(100, 100, 100)
				t_highlights = {t:Draw_Info(h_color) for (k, t) in tar_terrain_neighbors.items()}
				land['info'].redraw = True
				for living_info in life.values():
					living_info.redraw = True

	
	for t in land['land'].map.values():
		if t.smells:
			max_smell_strength = max(s.strength for s in t.smells.values())
			strongest_smell = next(smell for smell in t.smells.values() if smell.strength == max_smell_strength)
			l = strongest_smell.source
			color = pg.Color(life[l].color)
			inv_strength = round((100 -  max_smell_strength) * 2.55)
			color.r = max(0, color.r - inv_strength)
			color.g = max(0, color.g - inv_strength)
			color.b = max(0, color.b - inv_strength)
			t_highlights[t] = Draw_Info(color)

	return t_highlights
	

def draw(screen:pg.Surface,
		land:Dict,
		life: Dict[lv.Living, Living_Info],
		terrain_highlights:Dict[ld.Terrain, Draw_Info]
		):

	if land['info'].redraw or any(info.redraw for info in life.values()):
		screen.fill((0, 0, 0))
		draw_highlighted_terrain(screen, terrain_highlights, land['land'])
		draw_life(screen, life, land['land'])
		draw_land(screen, land)
		pg.display.flip()

def draw_land(screen:pg.Surface, land:Dict):
	if land['info'].redraw:
		for t in land['land'].map.values():
			pg.draw.polygon(screen, land['info'].color, land['land'].polygon_corners(t), width=1)
		land['info'].redraw = False

def draw_highlighted_terrain(screen:pg.Surface, terrain:Dict[ld.Terrain, Draw_Info], land:ld.Land):
	for t, t_info in terrain.items():
		pg.draw.polygon(screen, t_info.color, land.polygon_corners(t), width=0)

def draw_life(screen:pg.Surface, life:Dict[lv.Living, Draw_Info], land:ld.Land):
	for liv, info in life.items():
		if info.redraw:
			draw_living(screen, liv.position, info.color, info.img, land)
			info.redraw = False

def draw_living(screen:pg.Surface, position:ld.Terrain, color:pg.Color, img:pg.Surface, land:ld.Land):
	#pg.draw.polygon(screen, color, land.polygon_corners(position), width=0)

	l_x, l_y = land.polygon_center(position)
	img_w, img_h = img.get_size()
	img_coord = (l_x - img_w//2, l_y - img_h//2)
	screen.blit(img, img_coord)

if __name__ == "__main__":
	main()