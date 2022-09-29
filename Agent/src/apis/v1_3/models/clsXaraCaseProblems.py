from modDatabase import db
tableName = "xARA_CaseProblems"


class clsXaraCaseProblems(db.Model):

    __tablename__ = tableName
    __table_args__ = (
        db.Index(
            f'uk_{tableName}_CASE_ID',
            'CASE_ID',
            unique=True
        ),
    )

    CASE_ID = db.Column(db.String(255), primary_key=True, autoincrement=False, nullable=False)
    NO_OF_EDGES = db.Column(db.String(255), nullable=True)
    NO_OF_NODES = db.Column(db.String(255), nullable=True)

    N00_NODE_CATEGORY = db.Column(db.String(255), nullable=True)
    N01_NODE_CATEGORY = db.Column(db.String(255), nullable=True)
    N02_NODE_CATEGORY = db.Column(db.String(255), nullable=True)
    N03_NODE_CATEGORY = db.Column(db.String(255), nullable=True)

    E00_EDGE_PREDICATE = db.Column(db.String(255), nullable=True)
    E00_EDGE_ENDS = db.Column(db.String(255), nullable=True)

    E01_EDGE_PREDICATE = db.Column(db.String(255), nullable=True)
    E01_EDGE_ENDS = db.Column(db.String(255), nullable=True)

    E02_EDGE_PREDICATE = db.Column(db.String(255), nullable=True)
    E02_EDGE_ENDS = db.Column(db.String(255), nullable=True)
    
    ORIGIN = db.Column(db.String(255), nullable=True)

