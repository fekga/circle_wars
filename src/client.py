import __builtin__
__builtin__.isserver = False

import ability

class Client(object):
	pass
	
if __name__ == '__main__':
	ability.PassiveAbility('test_ability').use()
