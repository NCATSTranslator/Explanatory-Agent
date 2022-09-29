from modDatabase import db
from modConfig import dbAppName
from sqlalchemy.dialects.postgresql import JSONB

tableName = "xARA_QueryResults"


class clsXaraQueryResults(db.Model):
    __tablename__ = tableName
    __bind_key__ = dbAppName

    UUID = db.Column(db.String, primary_key=True, autoincrement=False, nullable=False)
    CREATED_ON = db.Column(db.DateTime, default=db.func.utcnow(), nullable=False)
    IP_ADDRESS = db.Column(db.String, nullable=True)
    PAYLOAD = db.Column(JSONB, nullable=True)
