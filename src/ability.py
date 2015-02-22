
class Ability(object):

	def __init__(self, name, **kwargs):
		self.name = name
		self.level = 0
		self.maxlevel = kwargs.get('maxlevel',1)
		self.cooldown = kwargs.get('cooldown',0.0)
		self.type = kwargs.get('type',None)
		self.manacost = kwargs.get('manacost',0.0)
		self.hpcost = kwargs.get('hpcost',0.0)
		self.icon = kwargs.get('icon',None)
		self.tooltip = kwargs.get('tooltip',None)
		self.disabled = False
		self.hidden = False

	def set_level(self, level):
		self.level = level

	def add_level(self, level):
		if self.level < self.maxlevel:
			self.level += 1

	def enable(self):
		self.disabled = False

	def disable(self):
		self.disabled = True

	def update_stats(self, **kwargs):
		self.__init__(self.name, kwargs)


class PassiveAbility(Ability):

	def __init__(self, name, **kwargs):
		kwargs['type'] = 'Passive'
		Ability.__init__(self,name,kwargs)


if __name__ == '__main__':
	pass
