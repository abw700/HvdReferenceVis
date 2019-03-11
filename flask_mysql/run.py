#!/usr/bin/python
 
import os
from app import create_app

## Run application
config_name = os.getenv('FLASK_CONFIG')
app = create_app(config_name)

if __name__ == '__main__':
    print(config_name)
    app.run()
