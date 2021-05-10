"""
WHAT: A module for the database ddl management script
WHY: Need to separate concerns and avoid circular import references
ASSUMES:
    * Database config is set on the flask app object
    * All api versions import their models for ddl management here
FUTURE IMPROVEMENTS: N/A
WHO: SL 2021-05-01
"""

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from modApp import appFactory
from modDatabase import db

# import models here to track ddl changes
from apis.v1_1.models import *


app = appFactory()  # create flask app object
db.init_app(app)  # bind to database
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
