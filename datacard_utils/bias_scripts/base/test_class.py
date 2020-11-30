from sys import path as spath
baserepodir = "/nfs/dust/cms/user/pkeicher/projects/base/classes"
if not baserepodir in spath:
	spath.append(baserepodir)
from test_class import test_class
class test_class(test_class):
	def __init__(self):
		super(test_class, self).__init__()