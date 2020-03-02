import config
import pygame
import math
from random import seed
from random import choice
from snap_to_grid import SnaptoGrid
class Map:
	'''load images for map generation,
	generate random x between 1 and window width - rounded object width
	random y between 1 and window height - rounded object height'''
	pyg = pygame.image
	sprites = {'bike shop':pyg.load('sprites/Objects/mart.png'),
		'department store':pyg.load('sprites/Objects/departmentStore.png'),
		'door_house':pyg.load('sprites/Objects/doorHouse.png'),
		'game corner':pyg.load('sprites/Objects/gameCorner.png'),
		'grass':pyg.load('sprites/Objects/grass_patch.jpg'),#72x51
		'mart':pyg.load('sprites/Objects/mart.png'), #64x62
		'oaks lab': pyg.load('sprites/Objects/oaksLab.png'), #112x71
		'water': pyg.load('sprites/Objects/pool.png'), #130,114
		'pokemon center': pyg.load('sprites/Objects/pokemonCenter.png'), #80x70
		'purple_house':pyg.load('sprites/Objects/purpleHouse.png'),
		'tree':pyg.load('sprites/Objects/tree.png') #30x45
	}
	objects = []
	nodes = set() #all traversable nodes
	movement_cost_area = {} #movement has a cost - grass/water
	def __init__(self):
		self.window_width = config.window_width
		self.window_height = config.window_height
		self.spacing = config.grid_spacing
		self.objs_area = set() #no movement through here - (x,y) area in use by all objects
		for x in range(0,self.window_width,self.spacing): #col
			for y in range(0,self.window_height,self.spacing): #row
				self.nodes.add((x,y))
		seed(341) #***seed for testing only***

	def generate_map(self, grass=20, trees=20, water=2):
		obj_features = []
		# ['tree']*200
		items = ['water']*10+['grass']*12+['tree']*70+['pokemon center']*5

		for item in items:
			obj = self.sprites[item]

			#get obj dimensions according to our grid
			obj_width = SnaptoGrid.snap(obj.get_width())
			obj_height = SnaptoGrid.snap(obj.get_height())
			square_width = int(obj_width / self.spacing)
			square_height = int(obj_height / self.spacing)

			#1) Keep obj in bounds
			#--> x must be in range ~[0, (window width - obj width)] and y in range ~[0, (window height - obj height)]
			not_oob  = set()
			for x in range(0,self.window_width-obj_width,self.spacing):
				for  y in range(0,self.window_height-obj_height,self.spacing):
					not_oob.add((x,y))

			#2) choose xy from available nodes such that obj doesnt touch any other object
			available_nodes = not_oob - self.objs_area
			rand_xy = choice(tuple(available_nodes))
			rand_x, rand_y = rand_xy[0], rand_xy[1]

			colliding = True
			if len(obj_features):
				while(colliding and len(available_nodes)):
					for features in obj_features:
						#if any of these conditions are true for all objects then we are not colliding with anything
						#we arent setting <= or >= to keep 1 square distance between objects
						rules =[(rand_x + obj_width) <= features['x'], #new obj is to the left
								rand_x >= (features['x']+ features['width']), #new obj is to the right
								(rand_y + obj_height) <= features['y'], #new obj is above
								rand_y >= (features['y'] + features['height'])] #new obj is below
						if any(rules):
							failed = False
						else: #colliding, choose a new x,y pair
							failed = True
							available_nodes.remove(rand_xy)
							if not(len(available_nodes)): break
							rand_xy = choice(tuple(available_nodes))
							rand_x, rand_y = rand_xy[0], rand_xy[1]
							break	

					colliding = False if not failed else True

			if not(len(available_nodes)): break

			self.objects.append([obj,rand_xy])

			obj_coords_x = [rand_x+(i*self.spacing) for i in range(square_width)]
			obj_coords_y = [rand_y+(i*self.spacing) for i in range(square_height)]

			#get square area used by object or movement cost if grass/water
			for x in obj_coords_x:
				for y in obj_coords_y:
					if item != 'grass' and item != 'water': 
						self.objs_area.add((x,y)) 
					else: 
						self.movement_cost_area[(x,y)] = 600 if item == 'grass' else 400
			features = {
				'x': rand_x,
				'y': rand_y,
				'width': obj_width,
				'height': obj_height
			}
			obj_features.append(features)

		#update available nodes for pathfinding to exclude nodes used for objects
		self.nodes = [n for n in self.nodes if n not in self.objs_area]
		obj_features.clear()

	@classmethod
	def draw(cls, win):
		for obj in cls.objects:
			item = obj[0]
			x,y = obj[1][0], obj[1][1]
			win.blit(item, (x,y))