# Harvard Capstone Reference Visualization

### Collaborators: Arthur, Mohammad, David, Pipat

#### Requirements:
- Linux or MacOS
- Python 3.7.2

#### How to setup local development environment
- Install a sample MySQL database as described in https://github.com/pipatth/pubmed_update
- Or, use the database hosted on AWS by the author (preferred)
- Install VirtualEnv if you don't have it:
```
$ pip install virtualenv
```
- Create virtual environment and install dependencies
```
$ virtualenv env
$ source env/bin/activate 
$ pip install -r requirements.txt
```
- Set environment variables and start a Redis Queue server
```
$ export FLASK_CONFIG=development 
$ export DB_ENDPOINTS=<your_mysql_ip_host>
$ export DB_DBNAME=<your_database_name>
$ export DB_USERNAME=<your_mysql_username>
$ export DB_PASS=<your_mysql_password>
$ python worker.py
```
- In another console, activate virtual environment, set environment variables, and start the server
```
$ source env/bin/activate 
$ export FLASK_CONFIG=development 
$ export DB_ENDPOINTS=<your_mysql_ip_host>
$ export DB_DBNAME=<your_database_name>
$ export DB_USERNAME=<your_mysql_username>
$ export DB_PASS=<your_mysql_password>
$ python main.py
```

To run test with code coverage:
- Use the database hosted on AWS by the author
- Set environment variable to 'test' and start a Redis Queue server
```
$ source env/bin/activate 
$ export FLASK_CONFIG=test
$ export DB_ENDPOINTS=<your_mysql_ip_host>
$ export DB_DBNAME=<your_database_name>
$ export DB_USERNAME=<your_mysql_username>
$ export DB_PASS=<your_mysql_password>
$ python worker.py
```
- In another console, activate virtual environment, set environment variables, and run the following command
```
$ source env/bin/activate 
$ export FLASK_CONFIG=test
$ export DB_ENDPOINTS=<your_mysql_ip_host>
$ export DB_DBNAME=<your_database_name>
$ export DB_USERNAME=<your_mysql_username>
$ export DB_PASS=<your_mysql_password>
$ pytest --cov=app -p no:warnings test.py --cov-report html
```
Test coverage report will be created in './htmlcov/index.html'

To test APIs, use the Postman collection provided in `RefViz.postman_collection.json`
