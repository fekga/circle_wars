import pyglet
pyglet.options['debug_gl'] = False
pyglet.options['audio'] = ('openal', 'directsound', 'pulse', 'silent')
import math
import random

from pyglet.gl import *
from pyglet.window import *
from pyglet.media import *
from pyglet.app import EventLoop

import cProfile

from shader import Shader

do_profile = False

class EventLoop(pyglet.app.EventLoop):
	def idle(self):
		pyglet.clock.tick(poll=True)
		return pyglet.clock.get_sleep_time(sleep_idle=True)
		
	def run(self):
		super(EventLoop,self).run()

class EventHandler(object):

	def __init__(self, window):
		self.window = window
		self.keys = pyglet.window.key.KeyStateHandler()
		self.window.push_handlers(self,self.keys)
		self.mouse = dict(pos=(0,0),delta=(0,0),buttons=0,moved=False)

	def on_key_press(self, symbol, modifiers):
		key = pyglet.window.key
		if key is pyglet.window.key.ESCAPE:
			pyglet.app.exit()
		return True
	
	def on_key_release(self, symbol, modifiers):
		return True

	def on_mouse_press(self, x, y, button, modifiers):
		self.mouse.update(dict(pos=(x,y),buttons=self.mouse['buttons'] | button))
		if button is pyglet.window.mouse.LEFT:
			self.window.click_counter+=1
		return True
		
	def on_mouse_release(self, x, y, button, modifiers):
		self.mouse.update(dict(pos=(x,y),buttons=self.mouse['buttons'] ^ button))
		return True
		
	def on_mouse_motion(self, x, y, dx, dy):
		self.mouse.update(dict(pos=(x,y),delta=(dx,dy),moved=(dx != 0 or dy != 0)))
		return True
	
	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		self.mouse.update(dict(pos=(x,y),delta=(dx,dy),buttons=buttons,moved=(dx != 0 or dy != 0)))
		return True

	def get_events(self):
		return dict(keys=self.keys,mouse=self.mouse)

class TestWindow(pyglet.window.Window):

	def __init__(self, fps=30,*args, **kwargs):
		super(TestWindow,self).__init__(*args,**kwargs)

		self.fps = fps
		self.elapsed_time = 0.0
		self.shaders = dict()

		#self.load_shader('popcorn')
		self.load_shader('raymarch')

		self.counter = 0

		pyglet.clock.schedule_interval(self.update,1.0/float(self.fps))
		pyglet.clock.set_fps_limit(self.fps)

		self.event_handler = EventHandler(window=self)

		self.batch = pyglet.graphics.Batch()
		self.batch.add(4, GL_QUADS, None, ('v2i', (-1, -1, 1, -1, 1, 1, -1, 1)))

		self.init = self.init_2d
		#self.buffer_manager = pyglet.image.get_buffer_manager()

		self.click_counter = 0

	def load_shader(self, name):
		with open('../res/'+name+'.frag','r') as f:
			frag = f.read()
		with open('../res/'+name+'.vert','r') as f:
			vert = f.read()
		self.shaders[name] = Shader(vert=[vert],frag=[frag])
		return self.shaders[name]

	def init_2d(self):
		glDisable(GL_DEPTH_TEST)
		glViewport(0,0,self.width,self.height)
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluOrtho2D(-1,1,-1,1)
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		self.init = lambda : None

	def on_draw(self):
		glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
		glClearColor(0,0,0,1)
		self.init()
		#glLoadIdentity()		

		events = self.event_handler.get_events()
		event_mouse = events['mouse']

		raymarch = self.shaders['raymarch']
		try:
			raymarch.bind()
			raymarch.uniformf('time',self.elapsed_time)
			raymarch.uniformf('resolution',self.width,self.height)
			raymarch.uniformf('touch',event_mouse['pos'][0],event_mouse['pos'][1])
			raymarch.uniformi('click',self.click_counter)
			self.batch.draw()
			raymarch.unbind()
		except:
			pass

	def update(self, dt):
		if not self.has_exit:
			self.elapsed_time += dt
			
			self.on_draw()
			#self.buffer_manager.get_color_buffer().save('screenshot.png')
			self.flip()
	
def main():
	platform = pyglet.window.get_platform()
	display = platform.get_default_display()
	screen = display.get_default_screen()

	template = pyglet.gl.Config(alpha_size=8, sample_buffers=1, samples=8)
	config = screen.get_best_config(template)
	context = config.create_context(None)
	window = TestWindow(context=context,
						width=480,
						height=320,
						resizable=False,
						caption='shadertest',
						vsync=False,
						fps=60)
	pyglet.app.event_loop = EventLoop()
	pyglet.app.run()

if __name__ == '__main__':
	if do_profile:
		cProfile.run('main()')
	else:
		main()