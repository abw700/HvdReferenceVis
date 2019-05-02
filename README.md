# Harvard Capstone Reference Visualization

### Collaborators: Arthur, Mohammad, David, Pipat

#### How to setup development environment
- Copy rvcapsrv1.db to flask_mysql directory
- Install VirtualEnv if you dont have it:
```
pip install virtualenv
```
- Create virtual environment and install dependencies
```
virtualenv env
source env/bin/activate (This doesn't work on windows - For windows use "env\Scripts\activate". Note: you'll need admin permissions to run this script -- Open powershell in Admin mode and enter "Set-ExecutionPolicy Unrestricted" and hit "Y")
pip install -r requirements.txt
```
- Set environment variable to 'development'
```
On MacOS / Linux:
export FLASK_CONFIG=development 

On windows:
set FLASK_CONFIG=development 
-- still has issues, will research how to set env variables easily)
```
- Start the server
```
python main.py
```
To test APIs, use the Postman collection in 'Development Resources/API' section in Google Drive

To run test with code coverage:
- Set environment variable to 'test'
- Run the following command
```
pytest --cov=app -p no:warnings test.py --cov-report html
```
Test coverage report will be created in './htmlcov/index.html'