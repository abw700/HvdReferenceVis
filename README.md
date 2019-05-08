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

#### To run test with code coverage:
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

#### To deploy on Heroku
- Install Heroku CLI if you don't have it. Follow the instruction on https://devcenter.heroku.com/articles/heroku-cli
- Login and create a Heroku application
```
$ heroku login
$ heroku apps:create <your_app_name>
```
- Push the application to Heroku
```
$ git push heroku master:master
```
- Configure Dynos:
    - Your application URL will show 'Application Error' because you have not assigned Dyno to the application
    - Go to Heroku setup dashboard https://dashboard.heroku.com/apps/
    - Click on your app name
    - Go to 'Resources' tab
    - Make sure both the 'web' and the 'worker' has Dyno assigned to them
    - In 'Add-ons' section add 'Redis To Go' add-on and assign a Dyno to it
- Set environment variables:
    - Go to Heroku setup dashboard https://dashboard.heroku.com/apps/
    - Click on your app name
    - Go to 'Settings' tab
    - Click on 'Reveal Config Vars'
    - Add the following environment variables
        ```
        FLASK_CONFIG    production
        DB_ENDPOINTS    <your_mysql_ip_host>
        DB_DBNAME       <your_database_name>
        DB_USERNAME     <your_mysql_username>
        DB_PASS         <your_mysql_password>
        ```
- Your application should be ready at the URL shown in Heroku Dashboard 'Settings' tab