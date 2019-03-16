### How to setup development environment
- Copy rvcapsrv1.db to flask_mysql directory
- Create virtual environment and install dependencies
```
virtualenv env
source env/bin/activate
pip install -r requirements.txt
```
- Set environment variable to 'development'
```
export FLASK_CONFIG=development
```
- Start the server
```
python main.py
```
To test APIs, use the Postman collection in 'Development Resources/API' section in Google Drive