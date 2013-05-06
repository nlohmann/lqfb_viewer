all:
	@echo "install:  download all required packages and statics"
	@echo "clean:    clean up folder"
	@echo "verclean: bring folder back to original state"
	@echo "serve:    start a server"
	@echo "test:     run test cases"

install: vienv pip_packages bower_packages config.py app.db

vienv:
	# virtual environment
	wget https://raw.github.com/pypa/virtualenv/master/virtualenv.py
	python virtualenv.py --no-site-packages venv

pip_packages:
	# python packages
	venv/bin/pip install sqlalchemy==0.7.9
	venv/bin/pip install MarkupSafe flask iso8601 pytz flask-sqlalchemy sqlalchemy-migrate flask-mail python-dateutil
	
bower_packages:
	# bower packages
	npm install bower
	node_modules/bower/bin/bower install bootstrap font-awesome jquery.tablesorter
	node_modules/bower/bin/bower install https://github.com/arnab/jQuery.PrettyTextDiff.git
	cd components/bootstrap ; npm install ; make build bootstrap
	cp -fr components/bootstrap/bootstrap app/static/bootstrap
	cp -fr components/jquery app/static
	cp -fr components/font-awesome app/static
	cp -fr components/jquery.tablesorter app/static
	cp -fr components/jQuery.PrettyTextDiff app/static

app.db:
	./db_create.py

config.py:
	test -f config.py || echo "WARNING: USING DEFAULT CONFIGURATION. PLEASE EDIT config.py!"
	test -f config.py || cp config.py.default config.py

clean:
	rm -fr virtualenv.py virtualenv.pyc node_modules components
	rm -fr *.pyc app/*.pyc

veryclean: clean
	rm -fr venv
	rm -fr app/static/bootstrap app/static/jquery app/static/font-awesome app/static/jquery.tablesorter app/static/jQuery.PrettyTextDiff

dbclean:
	rm -fr db_repository app.db

serve:
	./run.py

check:
	./test.py
