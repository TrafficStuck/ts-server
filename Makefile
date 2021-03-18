lint:
	pylint --rcfile=.pylintrc ./server/ --init-hook='sys.path.extend(["./server/"])'
