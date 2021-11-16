from modDatabase import db
tableName = "xARA_Nodes"


class clsXaraNodes(db.Model):

    __tablename__ = tableName
    __table_args__ = (
        db.Index(
            f'uk_{tableName}_Node_key',
            'Node_key',
            unique=True
        ),
    )

  
    Node_key = db.Column(db.Integer, primary_key=True, autoincrement=False, nullable=False)
    Node_Category = db.Column(db.String(255), nullable=True)
   
