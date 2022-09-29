from modDatabase import db
tableName = "xARA_CaseSolutions"


class clsXaraCaseSolutions(db.Model):

    __tablename__ = tableName
    __table_args__ = (
        db.Index(
            f'uk_{tableName}_CASE_ID',
            'CASE_ID',
            unique=True
        ),
    )

    SOLUTION_ID = db.Column(db.Integer, primary_key=True, autoincrement=False, nullable=False)
    CASE_ID = db.Column(db.String(255), nullable=True)
    ORIGIN = db.Column(db.String(255), nullable=True)
    
    SOLUTION_STEPS = db.Column(db.Integer, nullable=True)
    SOLUTION_FIRST_KP_NAME = db.Column(db.String(255), nullable=True)
    SOLUTION_SECOND_KP_NAME = db.Column(db.String(255), nullable=True)

    NODE1_PATH1_CATEGORY = db.Column(db.String(255), nullable=True)
    NODE2_PATH1_CATEGORY = db.Column(db.Float, nullable=True)

    NODE1_PATH2_CATEGORY = db.Column(db.String(255), nullable=True)
    NODE2_PATH2_CATEGORY = db.Column(db.String(255), nullable=True)

    EDGE1_PATH1_PREDICATE = db.Column(db.String(255), nullable=True)
    EDGE1_PATH1_ENDS = db.Column(db.String(255), nullable=True)

    EDGE1_PATH2_PREDICATE = db.Column(db.String(255), nullable=True)
    EDGE1_PATH2_ENDS = db.Column(db.String(255), nullable=True)

