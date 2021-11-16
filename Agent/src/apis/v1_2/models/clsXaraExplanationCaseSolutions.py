from modDatabase import db
tableName = "xARA_ExplanationCaseSolutions"


class clsXaraExplanationCaseSolutions(db.Model):

    __tablename__ = tableName
    __table_args__ = (
        db.Index(
            f'uk_{tableName}_SOLUTION_ID',
            'SOLUTION_ID',
            unique=True
        ),
    )

    SOLUTION_ID = db.Column(db.Integer(255), primary_key=True, autoincrement=False, nullable=False)
    CASE_ID = db.Column(db.String(255), nullable=False)
    SOLUTION_PROCESSES = db.Column(db.String(255), nullable=True)