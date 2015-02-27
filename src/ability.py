class Ability(object):
	
	@staticmethod
	def init(**kwargs):
		pass

	def __init__(self, name, **kwargs):
		self.name = name
		self.level = 0
		self.maxlevel = kwargs.get('maxlevel',1)
		self.cooldown = kwargs.get('cooldown',0.0)
		self.manacost = kwargs.get('manacost',0.0)
		self.hpcost = kwargs.get('hpcost',0.0)
		self.icon = kwargs.get('icon',None)
		self.ability_type = kwargs.get('ability_type',None)
		self.tooltip = kwargs.get('tooltip',None)
		self.disabled = False
		self.hidden = False

	def set_level(self, level):
		self.level = min(0,max(level,self.maxlevel))

	def add_level(self, level):
		if self.level < self.maxlevel:
			self.level += 1

	def enable(self):
		self.disabled = False

	def disable(self):
		self.disabled = True
		
	def set_enabled(self, enabled):
		self.disabled = not enabled
		
	def set_disabled(self, disabled):
		self.disabled = disabled
	
	def hide(self):
		self.hidden = True
		
	def unhide(self):
		self.hidden = False
		
	def set_hidden(self, hidden):
		self.hidden = hidden

	def update_stats(self, **kwargs):
		self.__init__(self.name, kwargs)
	
	def use(self):
		print 'Not implemented'

class PassiveAbility(Ability):

	def __init__(self, name, **kwargs):
		kwargs['ability_type'] = 'passive'
		Ability.__init__(self,name,**kwargs)
		
	if isserver:
		def use(self):
			print self.name
		
class ActiveAbility(Ability):
	
	def __init__(self, name, **kwargs):
		kwargs['ability_type'] = 'active'
		Ability.__init__(self,name,**kwargs)
		
	if isserver:
		def use(self):
			print self.name
		
class ToggleAbility(Ability):
	
	def __init__(self, name, **kwargs):
		kwargs['ability_type'] = 'toggle'
		Ability.__init__(self,name,**kwargs)
		
	def toggle(self):
		self.disabled = not self.disabled
		print self.name, 'is now', 'disabled' if self.disabled else 'enabled'
		
	if isserver:
		def use(self):
			self.toggle()


if __name__ == '__main__':
	a = PassiveAbility('critical strike')
	try:
		a.use()
	except Exception as e:
		print e
