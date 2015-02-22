import pyglet
from pyglet.app import EventLoop
from pyglet.gl import *

class EventLoop(pyglet.app.EventLoop):
	def idle(self):
		pyglet.clock.tick(poll=True)
		return pyglet.clock.get_sleep_time(sleep_idle=True)
		
	def run(self):
		super(EventLoop,self).run()

class GamePrimitiveManager:
	list_max = 10
	display_list = glGenLists(list_max)
	anchor_list_v = ['top','center','bottom']
	anchor_list_h = ['left','center','right']

	@staticmethod
	def ring(inner, outer, slices=0):
		q = gluNewQuadric()
		_slices = int(min(360, 6*outer)) if slices is 0 else slices
		gluDisk(q, inner, outer, _slices, 2)
		gluDeleteQuadric(q)

	@staticmethod
	def arc(inner, outer, start=0, sweep=180, slices=0):
		q = gluNewQuadric()
		_slices = int(min(360, 6*outer)) if slices is 0 else slices
		gluPartialDisk(q, inner, outer, _slices, 1, 90-start, -sweep)
		gluDeleteQuadric(q)

	@staticmethod
	def create_ring(index, inner, outer):
		glNewList(GamePrimitiveManager.display_list+index, GL_COMPILE)
		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		GamePrimitiveManager.ring(inner,outer)
		glEndList()
		return index

	@staticmethod
	def create_arc(index, inner, outer, start=0, sweep=180):
		glNewList(GamePrimitiveManager.display_list+index, GL_COMPILE)
		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		GamePrimitiveManager.arc(inner,outer,start,sweep)
		glEndList()
		return index
		
	@staticmethod
	def create_hero_sprite(index, inner, outer):
		glNewList(GamePrimitiveManager.display_list+index, GL_COMPILE)
		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		GamePrimitiveManager.ring(inner,outer)
		glBegin(GL_TRIANGLES)
		glVertex2f(1.45*outer,0)
		glVertex2f(0.85*outer,0.5*outer)
		glVertex2f(0.85*outer,-0.5*outer)
		glEnd()
		glEndList()
		return index
		
	@staticmethod
	def draw(index):
		glCallList(GamePrimitiveManager.display_list+index)
