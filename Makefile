all:
	@echo "install:  download all required packages and statics"
	@echo "clean:    clean up folder"
	@echo "verclean: bring folder back to original state"
	@echo "serve:    start a server"

install:
	# virtual environment
	wget https://raw.github.com/pypa/virtualenv/master/virtualenv.py
	python virtualenv.py flask

	# python packages
	flask/bin/pip install flask iso8601 pytz
	
	# bower packages
	npm install bower
	node_modules/bower/bin/bower install bootstrap font-awesome jquery.tablesorter
	cd components/bootstrap ; npm install ; make build bootstrap
	cp -fr components/bootstrap/bootstrap app/static/bootstrap
	cp -fr components/jquery app/static
	cp -fr components/font-awesome app/static
	cp -fr components/jquery.tablesorter app/static

clean:
	rm -fr virtualenv.py virtualenv.pyc node_modules components
	rm -fr app/*.pyc

veryclean: clean
	rm -fr flask
	rm -fr app/static/bootstrap app/static/jquery app/static/font-awesome app/static/jquery.tablesorter

serve:
	./run.py
