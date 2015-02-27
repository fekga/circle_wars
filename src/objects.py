import uuid
import pyglet
import math
from pyglet.gl import *
from managers import *

from contextlib import contextmanager

debug=False

@contextmanager
def gl(attributes=None):
	if attributes:
		glPushAttrib(attributes)
	glPushMatrix()
	try:
		yield
	except Exception as e:
		print e
	glPopMatrix()
	if attributes:
		glPopAttrib()

class Object(object):
	window 				= None
	max_speed 			= 300.0
	default_turn_speed 	= 2.0
	default_friction 	= 1.0
	default_slowdown 	= 0.0

	@staticmethod
	def init(window):
		Object.window = window
		Hero.init()

	def __init__(self, 
				pos					= (0,0), 
				velocity			= (0,0), 
				acceleration		= (0,0), 
				facing				= 0.0, 
				turn_speed			= default_turn_speed, 
				friction			= default_friction,
				slowdown 			= default_slowdown):
		self.pos 			= pos
		self.velocity 		= velocity
		self.acceleration 	= acceleration
		self.facing 		= facing
		self.turn_speed 	= turn_speed
		self.friction 		= friction
		self.slowdown		= slowdown
		
		self.observers		= set()
		self.focus_point 	= self.pos
		
		self.id 			= uuid.uuid4()

	def circle(self):
		return dict(p=self.pos,r=0.0)

	def _update_movement(self,dt):
		self.pos = (self.pos[0]+self.velocity[0]*dt,
					self.pos[1]+self.velocity[1]*dt)
					
		self.velocity = ((self.velocity[0]+self.acceleration[0]*0.5*dt)*self.friction,
						 (self.velocity[1]+self.acceleration[1]*0.5*dt)*self.friction)
						 
		self.acceleration = (self.acceleration[0],
							 self.acceleration[1])

		self.focus_point = (self.pos[0] + self.velocity[0] * 0.5,
							self.pos[1] + self.velocity[1] * 0.5)

		speed = self.get_speed() - self.slowdown*dt
		speed_mod = 1.0 if not self.get_speed() else speed/self.get_speed();
		if speed > Object.max_speed:
			speed_mod = speed_mod * Object.max_speed/speed
		self.velocity = (self.velocity[0]*speed_mod,
						 self.velocity[1]*speed_mod)
		
							 
	def get_speed(self):
		return (self.velocity[0]**2+self.velocity[1]**2)**0.5

	def update(self,dt):
		self._update_movement(dt)
		self._notify()

	def _notify(self):
		for o in self.observers:
			o.notify(self)

	def add_observer(self, observer):
		self.observers.add(observer)

	def remove_observer(self, observer):
		self.observers.remove(observer)
		
	def draw(self):
		pass

class Hero(Object):
	inner_radius = 0
	outer_radius = 12.5
	friction = 0.99
	acceleration_modifier = 500
	turn_speed = 4.5
	
	@staticmethod
	def init():
		Hero.sprite = GamePrimitiveManager.create_hero_sprite(0,Hero.inner_radius,Hero.outer_radius)
		Indicator.init()
	
	def __init__(self,pos=(0,0),facing=0,color=(1.0,1.0,1.0,1.0)):
		super(Hero,self).__init__(pos=pos,
									facing=facing,
									turn_speed=Hero.turn_speed,
									friction=Hero.friction)
		
		self.maxlife = 100
		self.life = self.maxlife
		self.life_regen = -1.5
		
		self.color = color
		self.indicator = Indicator(self)
		
		print('Hero ' + str(self.id) + ' created.')

	def circle(self):
		return dict(p=self.pos,r=Hero.outer_radius)

	def set_move_position(self,pos):
		self.move_pos = pos

	def _update_movement(self,dt):
		super(Hero,self)._update_movement(dt)
		
		events = self.window.get_events()
		mouse_events = events['mouse']

		if mouse_events['buttons'] & pyglet.window.mouse.LEFT:
			
			move_pos = self.window.get_world_coord(mouse_events['pos'])

			angle = math.atan2(move_pos[1]-self.pos[1],
							   move_pos[0]-self.pos[0])
			
			difference = angle-self.facing
			if difference > math.pi:
				difference = 2*math.pi - difference
			if difference < -math.pi:
				difference = 2*math.pi + difference
			
			self.facing +=  difference * self.turn_speed * dt
			if self.facing > 2*math.pi:
				self.facing -= 2*math.pi
			if self.facing < 0:
				self.facing += 2*math.pi
		
			self.acceleration = (Hero.acceleration_modifier*math.cos(angle),
								 Hero.acceleration_modifier*math.sin(angle))
		else:
			self.acceleration = (0,0)
		
	def _update_stats(self,dt):
		self.life += self.life_regen * dt
		self.life = max(0,min(self.maxlife,self.life))
		
	def update(self,dt):
		self._update_movement(dt)
		self._update_stats(dt)
		self._notify()
		
	def draw(self):
		#DEBUG
		if debug:
			glLineWidth(3)
			
			#Velocity
			glColor4f(1,0,0,1)
			glBegin(GL_LINES)
			glVertex2f(*self.pos)
			glVertex2f(self.pos[0]+self.velocity[0],self.pos[1]+self.velocity[1])
			glEnd()
			
			#Acceleration
			glColor4f(0,0,1,1)
			glBegin(GL_LINES)
			glVertex2f(*self.pos)
			glVertex2f(self.pos[0]+self.acceleration[0],self.pos[1]+self.acceleration[1])
			glEnd()
			
			#Facing
			with gl():
				glTranslatef(self.pos[0],self.pos[1],0)
				glRotatef(math.degrees(self.facing),0,0,1)
				glColor4f(0,1,0,1)
				glBegin(GL_LINES)
				glVertex2f(0,0)
				glVertex2f(Hero.max_speed,0)
				glEnd()
		#DEBUG END
		
		with gl():
			glTranslatef(self.pos[0],self.pos[1],0)
			with gl():
				glRotatef(math.degrees(self.facing),0,0,1)
				#Outline
				with gl():
					glScalef(1.125,1.125,1.125)
					glColor4f(0,0,0,1)
					GamePrimitiveManager.draw(Hero.sprite)
				#Color
				glColor4f(*self.color)
				GamePrimitiveManager.draw(Hero.sprite)
			self.indicator.draw()
		
class Indicator(object):
	radius = Hero.outer_radius*0.5
	
	@staticmethod
	def init():
		#Indicator.sprite = GamePrimitiveManager.create_ring(1,10,100)
		pass
	
	def __init__(self, unit):
		unit.add_observer(self)
		self.life_percent = 1.0
		self.label = pyglet.text.Label(text='',
									   multiline=False,
									   font_name='Free Mono',
									   bold=True,
									   font_size=12,
									   width=40,
									   x=0,y=0,
									   color=(255,255,255,255),
									   anchor_x='center',
									   anchor_y='center')
		self.size = (60.0,5.0)
		self.border_size = 1

	def notify(self, obj):
		self.life_percent = obj.life / float(obj.maxlife)
		self.label.text = str(int(100*self.life_percent))

	def get_color(self, use_int=False):
		c = (1.0-self.life_percent,self.life_percent,0.0)
		return (int(255*c[0]),int(255*c[1]),int(255*c[2])) if use_int else c
		
	def draw(self):
		with gl(GL_POINT_BIT|GL_LINE_BIT|GL_POLYGON_BIT|GL_HINT_BIT|GL_ENABLE_BIT|GL_TEXTURE_BIT):
			glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST)
			glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST)
			glDisable (GL_BLEND)
			glDisable(GL_POINT_SMOOTH)
			glDisable(GL_LINE_SMOOTH)
			glDisable(GL_POLYGON_SMOOTH)
			glHint(GL_LINE_SMOOTH_HINT,GL_DONT_CARE)
			glHint(GL_POINT_SMOOTH_HINT,GL_DONT_CARE)
			glHint(GL_POLYGON_SMOOTH_HINT,GL_DONT_CARE)


			glTranslatef(-self.size[0]/2.0,25,0)
			w = self.size[0]*self.life_percent
			b = self.border_size
			glBegin(GL_QUADS)
			glColor3f(0,0,0)
			glVertex2i(int(0),				int(0))
			glVertex2i(int(self.size[0]),	int(0))
			glVertex2i(int(self.size[0]),	int(self.size[1]))
			glVertex2i(int(0),				int(self.size[1]))
			glColor3f(*self.get_color())
			glVertex2i(int(b),				int(b))
			glVertex2i(int(w-2*b),			int(b))
			glVertex2i(int(w-2*b),			int(self.size[1]-2*b))
			glVertex2i(int(b),				int(self.size[1]-2*b))
			glEnd()
		#self.label.draw()
		'''
		glPushMatrix()
		glTranslatef(self.pos[0],self.pos[1],0.0)
		scale = Indicator.radius
		glScalef(*((scale,)*3))
		glColor4f(1.0,1.0,1.0,1.0)
		GamePrimitiveManager.ring(inner=0.,
								  outer=1.,
								  slices=60)
		glColor4f(0.0,0.0,0.0,1.0)
		GamePrimitiveManager.ring(inner=1.,
								  outer=1.25,
								  slices=60)
		glColor4f(1.0-self.life_percent,self.life_percent,0.0,1.0)
		GamePrimitiveManager.arc(inner=0., 
								 outer=1., 
								 start=math.degrees(self.facing), 
								 sweep=180.0 * self.life_percent,
								 slices=60)
		GamePrimitiveManager.arc(inner=0., 
								 outer=1., 
								 start=math.degrees(self.facing), 
								 sweep=-180.0 * self.life_percent,
								 slices=60)
		glPopMatrix()
		'''

class Projectile(Object):

	def __init__(self, owner, pos, facing, movement_func=None,draw_func=None):
		super(Projectile,self).__init__(pos=pos,facing=facing)
		self.owner=owner
		self.movement_func=movement_func
		self.draw_func=draw_func

	def update(self,dt):
		if self.movement_func:
			self.movement_func(dt)

	def draw(self):
		if self.draw_func:
			self.draw_func()