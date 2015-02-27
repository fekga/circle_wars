import __builtin__
__builtin__.isserver = True

import ability

class Server(object):
	pass
	
if __name__ == '__main__':
	ability.ToggleAbility('test_ability').use()
	ability.ToggleAbility('test_ability').use()
	ability.ToggleAbility('test_ability').use()
	ability.ToggleAbility('test_ability').use()
	ability.ToggleAbility('test_ability').use()

