import pyglet
import math
import random
import os
import os.path
import uuid

import profile

from contextlib import contextmanager

from pyglet.gl import *
from pyglet.window import *
pyglet.options['audio'] = ('openal', 'directsound', 'pulse', 'silent')
from pyglet.media import *

from ctypes import *

#from pyglet.resource import *

from shader import Shader

from managers import *
from objects import *

from PIL import Image
from PIL import BmpImagePlugin,GifImagePlugin,Jpeg2KImagePlugin,JpegImagePlugin,PngImagePlugin,TiffImagePlugin,WmfImagePlugin # added this line

Image._initialized=2 # added this line


@contextmanager
def opened_w_error(filename, mode="r"):
	try:
		f = open(filename, mode)
	except IOError, err:
		yield None, err
	else:
		try:
			yield f, None
		finally:
			f.close()

def load_file(path,filename,extension,default='default'):
	data = None
	with opened_w_error(path+filename+extension) as (f,err):
		if err:
			with opened_w_error(path+default+extension) as (f,err):
				if err:
					print 'IOError: ', err
					return
				else:
					data = f.read()
		else:
			data = f.read()
	return data

def normalize(vec):
	s = sum(vec)
	if s != 0.0:
		vec = [x/float(s) for x in vec]
	return vec

class GameEventHandler(object):

	def __init__(self, window):
		self.window = window
		self.camera = self.window.camera
		self.player = self.window.player
		self.keys = pyglet.window.key.KeyStateHandler()
		self.mouse = dict(pos=(0,0),delta=(0,0),buttons=0,moved=False)
		self.window.push_handlers(self)

	def on_key_press(self, symbol, modifiers):
		key = pyglet.window.key
		if symbol == key.ESCAPE:
			pyglet.app.exit()
		elif symbol == key.SPACE:
			self.window.toggle_pause()
			'''try:
				pyglet.image.get_buffer_manager().get_color_buffer().save('screenshot.png')
			except:
				pass'''
			
		return True
	
	def on_key_release(self, symbol, modifiers):
		return True

	def on_mouse_press(self, x, y, button, modifiers):
		self.mouse.update(dict(pos=(x,y),buttons=self.mouse['buttons'] | button))
		return True
		
	def on_mouse_release(self, x, y, button, modifiers):
		self.mouse.update(dict(pos=(x,y),buttons=self.mouse['buttons'] ^ button))
		return True
		
	def on_mouse_motion(self, x, y, dx, dy):
		self.mouse.update(dict(pos=(x,y),delta=(dx,dy),moved=(dx != 0 or dy != 0)))
		return True
	
	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		self.mouse.update(dict(pos=(x,y),delta=(dx,dy),buttons=buttons,moved=(dx != 0 or dy != 0)))
		if buttons & pyglet.window.mouse.LEFT:
			pass
		return True

	def get_events(self):
		return dict(keys=self.keys,mouse=self.mouse)
		
class Camera:
	def __init__(self, window, eye=(0,0,1),target=(0,0,-1), fov = 60.0, near=0.1, far=1000.0):
		self.window = window
		self.fov = fov
		self.near = near
		self.far = far
		self.eye = eye
		self.target = target
		self.width = self.window.width
		self.height = self.window.height
		self.center = (self.width//2,self.height//2)
		self._update_vectors()
		
	def _update_vectors(self):
		self.target_direction = normalize([a-b for a,b in zip(self.target,self.eye)])

	def set_target_object(self, obj):
		obj.add_observer(self)

	def notify(self, obj):
		self.move_to((obj.focus_point[0],obj.focus_point[1],0))
		
	def focus_2d(self):
		glViewport(0,0,self.width,self.height)
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluOrtho2D(-self.center[0], self.center[0], -self.center[1], self.center[1])
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		gluLookAt(self.eye[0],self.eye[1],self.eye[2],
				  self.target[0],self.target[1],self.target[2],
				  0.0,1.0,0.0)
		#glTranslatef(0.375,0.375,0.0) possible pixel rasterization optimization
		glShadeModel(GL_SMOOTH)
		glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
		glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
		glDisable(GL_LIGHTING)
		glDisable(GL_DEPTH_TEST)


		glEnable(GL_BLEND)
		glEnable(GL_POINT_SMOOTH)
		glEnable(GL_LINE_SMOOTH)
		glEnable(GL_POLYGON_SMOOTH)
		glHint(GL_POINT_SMOOTH_HINT,GL_NICEST)
		glHint(GL_LINE_SMOOTH_HINT,GL_NICEST)
		glHint(GL_POLYGON_SMOOTH_HINT,GL_NICEST)

	def convert_to_world_coordinates(self, location):
		return (self.eye[0]+location[0]-self.center[0],
				self.eye[1]+location[1]-self.center[1])
				  
	def set_direction(self, vec):
		self.target_direction = normalize(vec)
	
	def move_to_target(self,amount):
		self.eye = [sum(x) for x in zip(self.eye,offset)]
	
	def move(self,new_eye):
	   self.eye = new_eye 
	
	def move_by(self, offset,move_target=True):
		self.eye = [sum(x) for x in zip(self.eye,offset)]
		if move_target:
			self.move_target_by(offset)

	def move_to(self, new_eye,move_target=True):
		offset = [a-b for a,b in zip(new_eye,self.eye)]
		self.eye = new_eye
		if move_target:
			self.move_target_by(offset)

	def move_target_to(self, new_target):
		self.target = new_target
		self._update_vectors()
	
	def move_target_by(self, offset):
		self.target = [sum(x) for x in zip(self.target,offset)]
		self._update_vectors()

class GameWindow(pyglet.window.Window):

	def __init__(self, fps=60,*args, **kwargs):
		platform = pyglet.window.get_platform()
		display = platform.get_default_display()
		screen = display.get_default_screen()

		template = pyglet.gl.Config(alpha_size=8, sample_buffers=1, samples=8)
		config = screen.get_best_config(template)
		context = config.create_context(None)
		kwargs['context'] = context
		super(GameWindow,self).__init__(*args,**kwargs)
		
		self.set_location( (screen.width-self.width)//2, (screen.height-self.height)//2)

		self.fps = fps
		self.elapsed_time = 0.0
		
		self.players = list()
		self.players.append(Hero(pos=(0,0),
								 color=(random.random(),random.random(),random.random(),1),
								 facing=0.0))

		self.camera = Camera(window=self)
		self.camera.set_target_object(self.players[0])
		
		
		pyglet.clock.schedule_interval(self.update,1.0/float(self.fps))
		pyglet.clock.schedule_interval(self.update_physics,1.0/60.0)

		Object.init(self)
		
		#music = pyglet.media.load('../res/DST-Azimuth.mp3')
		self.player = pyglet.media.Player()
		self.player.volume = 0.3
		#self.player.queue(music)
		#self.player.play()
		
		self.event_handler = GameEventHandler(window=self)
		
		self.labels = dict()
		self.labels['debug'] = pyglet.text.Label(text='',
									   multiline=True,
									   font_name='Times New Roman',
									   bold=True,
									   font_size=16,
									   width=100,
									   x=-self.width//2,y=self.height//2,
									   color=(0,240,200,255),
									   anchor_x='left',
									   anchor_y='top')

		self.labels['pause'] = pyglet.text.Label(text='PAUSED',
									   multiline=False,
									   font_name='Mono Free',
									   bold=True,
									   font_size=24,
									   width=self.width/4,
									   x=0,y=0,
									   color=(255,255,255,128),
									   anchor_x='center',
									   anchor_y='center')

		
		self.shaders = dict()
		
		self.load_shader('popcorn')
		self.load_shader('scrolling')
		self.load_shader('arena_ground_001','arena_ground')
		self.load_shader('concentric')

		self.map_radius = 1200.0
		self.map_size = 3000.0
		self.crack_radius = 50.0

		self.paused = False

		pyglet.app.event_loop = EventLoop()

	def toggle_pause(self):
		self.paused = not self.paused

	def load_shader(self, name, alias=None):
		frag = load_file('../res/',name,'.frag')
		vert = load_file('../res/',name,'.vert')
		self.shaders[alias or name] = Shader(vert=[vert],frag=[frag])

	def get_events(self):
		return self.event_handler.get_events()

	def get_world_coord(self, loc):
		return self.camera.convert_to_world_coordinates(loc)
	
	'''
	def setup_lights(self):
		
		glShadeModel(GL_SMOOTH) 
		glEnable(GL_LIGHTING)
		glEnable(GL_LIGHT0)
		glClearDepth(1.0) 
		glEnable(GL_DEPTH_TEST) 
		glDepthFunc(GL_LEQUAL) 
		glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
		
		ambient = (GLfloat*4)(1.0, 0.0, 0.0, 0.0)
		diffuse = (GLfloat*4)(1.0, 0.5, 0.0, 0.0)
		specular = (GLfloat*4)(1.0, 1.0, 1.0, 1.0)
		shininess = (GLfloat*1)(50.0)
		light_position = (GLfloat*4)(*(self.light+[0.0]))
		
		glMaterialfv(GL_FRONT, GL_SPECULAR, specular)
		glMaterialfv(GL_FRONT, GL_SHININESS, shininess)
		glLightfv(GL_LIGHT0, GL_AMBIENT, ambient)
		glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse)
		glLightfv(GL_LIGHT0, GL_POSITION, light_position)
	
		
	def disable_lights(self):
		glDisable(GL_LIGHTING)
	'''
			
	def on_draw(self):
		glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
		glClearColor(0.5,0.5,0.5,1)
		glLoadIdentity()
		
		with gl():
			self.camera.focus_2d()

			shader = self.shaders['arena_ground']
			with gl():
				glScalef(self.map_size,self.map_size,1)
			
				shader.bind()
				shader.uniformf('time',self.elapsed_time)
				shader.uniformf('resolution',*(self.width,self.height))
				shader.uniformf('focus',*(self.camera.target[0:2]))
				shader.uniformf('map_radius',self.map_radius)
				shader.uniformf('crack_radius',self.crack_radius)
				glBegin(GL_QUADS)
				glColor3f(1.0,0.5,0.0)
				glVertex2f(-1,-1)
				glColor3f(0.0,1.0,0.5)
				glVertex2f(1,-1)
				glColor3f(0.2,0.0,1.0)
				glVertex2f(1,1)
				glColor3f(1.0,1.0,0.0)
				glVertex2f(-1,1)
				glEnd()
				shader.unbind()

			glColor3f(1,1,1)
			GamePrimitiveManager.ring(self.map_radius-1,self.map_radius+1,360)

			for player in self.players:
				player.draw()

		if self.paused:
			glColor4f(0,0,0,0.5)
			glBegin(GL_QUADS)
			glVertex2f(-self.width/2,-self.height/2)
			glVertex2f(self.width/2,-self.height/2)
			glVertex2f(self.width/2,self.height/2)
			glVertex2f(-self.width/2,self.height/2)
			glEnd()
			self.labels['pause'].draw()
				
	def update(self, dt):
		if not self.has_exit:
			self.elapsed_time += dt
			
			self.labels['debug'].text = 'Time: {:.2f}\nFPS: {:.2f}\nSpeed: {:.2f}\nEye: {:.2f},{:.2f}'.format(self.elapsed_time,1.0/dt,self.players[0].get_speed(),*(self.camera.eye[0:2]))
			self.dispatch_event('on_draw')
			self.flip()
	
	def update_physics(self, dt):
		if not self.has_exit:
			events = self.get_events()
			mouse_events = events['mouse']
			mouse_pos = mouse_events['pos']
			
			if not self.paused:
				self.map_radius -= 15.0*dt
			
				for player in self.players:
					player.update(dt)

if __name__ == '__main__':
	window = GameWindow(width=640,
						height=480,
						resizable=False,
						caption='circle_wars',
						vsync=False,
						fps=90)
	pyglet.app.run()
