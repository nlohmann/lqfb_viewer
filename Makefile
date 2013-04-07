all:
	@echo "install:  download all required packages and statics"
	@echo "clean:    clean up folder"
	@echo "verclean: bring folder back to original state"
	@echo "serve:    start a server"

install: packages statics

packages:
	pip install Flask iso8601 pytz

statics:
	npm install bower
	mkdir -p static
	node_modules/bower/bin/bower install bootstrap font-awesome jquery.tablesorter
	cd components/bootstrap ; npm install ; make build bootstrap
	cp -fr components/bootstrap/bootstrap static/bootstrap
	cp -fr components/jquery static
	cp -fr components/font-awesome static
	cp -fr components/jquery.tablesorter static

clean:
	rm -fr components
	rm -fr node_modules
	rm -fr *.pyc

veryclean: clean
	rm -fr static/bootstrap static/jquery static/font-awesome static/jquery.tablesorter

serve:
	python server.py
