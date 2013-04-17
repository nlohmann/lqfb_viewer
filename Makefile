all:
	@echo "install:  download all required packages and statics"
	@echo "clean:    clean up folder"
	@echo "verclean: bring folder back to original state"
	@echo "serve:    start a server"
	@echo "test:     run test cases"

install: venv pip_packages bower_packages app.db

venv:
	# virtual environment
	wget https://raw.github.com/pypa/virtualenv/master/virtualenv.py
	python virtualenv.py --no-site-packages flask

pip_packages:
	# python packages
	flask/bin/pip install sqlalchemy==0.7.9
	flask/bin/pip install MarkupSafe flask iso8601 pytz flask-sqlalchemy sqlalchemy-migrate flask-mail
	
bower_packages:
	# bower packages
	npm install bower
	node_modules/bower/bin/bower install bootstrap font-awesome jquery.tablesorter
	cd components/bootstrap ; npm install ; make build bootstrap
	cp -fr components/bootstrap/bootstrap app/static/bootstrap
	cp -fr components/jquery app/static
	cp -fr components/font-awesome app/static
	cp -fr components/jquery.tablesorter app/static

app.db:
	./db_create.py

clean:
	rm -fr virtualenv.py virtualenv.pyc node_modules components
	rm -fr *.pyc app/*.pyc

veryclean: clean
	rm -fr flask
	rm -fr app/static/bootstrap app/static/jquery app/static/font-awesome app/static/jquery.tablesorter

dbclean:
	rm -fr db_repository app.db

serve:
	./run.py

check:
	./test.py
