"""
WHAT: A module for the database access object
WHY: Need to separate concerns and avoid circular import references
ASSUMES: Database config is set on the flask app object
FUTURE IMPROVEMENTS: N/A
WHO: SL 2021-05-01
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
