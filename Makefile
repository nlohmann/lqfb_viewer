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
	venv/bin/pip install iso8601 pytz python-dateutil icalendar
	# flask
	venv/bin/pip install sqlalchemy==0.7.9 MarkupSafe flask flask-sqlalchemy sqlalchemy-migrate flask-mail
	# celery
	venv/bin/pip install celery
	
bower_packages:
	# bower packages
	npm install bower
	node_modules/bower/bin/bower install bootstrap font-awesome jquery.tablesorter Chart.js
	node_modules/bower/bin/bower install https://github.com/arnab/jQuery.PrettyTextDiff.git
	# bootstrap needs to be built
	cd components/bootstrap ; npm install ; make build bootstrap
	# copy components
	cp -fr components/bootstrap/bootstrap app/static/bootstrap
	cp -fr components/jquery app/static
	cp -fr components/Chart.js app/static
	cp -fr components/font-awesome/build/assets/font-awesome app/static
	cp -fr components/tablesorter app/static
	cp -fr components/jQuery.PrettyTextDiff app/static

config.py:
	test -f config.py || echo "WARNING: USING DEFAULT CONFIGURATION. PLEASE EDIT config.py!"
	test -f config.py || cp config.py.default config.py

clean:
	rm -fr virtualenv.py virtualenv.pyc node_modules components
	rm -fr *.pyc app/*.pyc

veryclean: clean
	rm -fr venv
	rm -fr app/static/bootstrap app/static/jquery app/static/font-awesome app/static/tablesorter app/static/jQuery.PrettyTextDiff

app.db:
	./db_create.py

dbclean:
	rm -fr db_repository app.db

serve:
	./run.py

celery:
	venv/bin/celery worker -A app.tasks -B --loglevel=info

celery_clean:
	rm -fr celerybeat-schedule celery_broker.db celery_result.db

check:
	./test.py
