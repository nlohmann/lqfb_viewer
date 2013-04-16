# LiquidFeedback Viewer - Bootstrap version

## Technisches

Der Viewer läuft mit dem Python Framework [Flask](http://flask.pocoo.org). Für die Templates wird [Jinja](http://jinja.pocoo.org) genutzt.

### Vorbereitung

Um den Viewer zu starten, werden folgende Werkzeuge benötigt:

- [Python](http://www.python.org)
- [SQLite](http://www.sqlite.org)
- [npm](https://npmjs.org)
- [make](http://www.gnu.org/software/make)

Alle weiteren benötigten Pakete werden dann mit

    make install

eingerichtet.

### Konfiguration

Standardmäßig ist die Instanz der [SMV Mecklenburg-Vorpommern](http://smv.piratenpartei-mv.de) als Datenquelle angegeben. Andere Quellen können durch setzen der Felder `api_url` und `lqfb_url` in der Datei `settings.json` festgelegt werden.

### Server starten

Der Server kann mit

    make serve

gestartet werden. Er sollte dann unter <http://127.0.0.1:5000> erreichbar sein.

### Aufräumen

Alle nicht für den Server benötigten Daten können mit

    make clean

gelöscht werden. Mit

    make veryclean

Werden alle Daten gelöscht, die von `make install` erstellt wurden.

Die Datenbank kann mit

    make db_clean

gelöscht werden.

## Rechtliches

Das Projekt ist unter der [MIT License](http://opensource.org/licenses/mit-license.php) lizensiert.

> Copyright (c) 2013 Niels Lohmann
> 
> Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: 
> 
> The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
> 
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
