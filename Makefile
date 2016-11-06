tests:
	nosetests -v test/

coverage:
	nosetests --with-coverage --cover-package=tools,findgame,addgame,game,delete,editgame,notify,sanear
