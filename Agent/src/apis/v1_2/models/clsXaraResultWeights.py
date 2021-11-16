from modDatabase import db
tableName = "xARA_ResultWeights"


class clsXaraResultWeights(db.Model):

    __tablename__ = tableName
    # __table_args__ = (
    #     db.Index(
    #         f'uk_{tableName}_CASE_ID',
    #         'CASE_ID',
    #         unique=True
    #     ),
    # )


    XCASE_ID = db.Column(db.String(255), nullable=True)
    SUBJECT_NODE_WEIGHT	= db.Column(db.Integer, nullable=True)
    OBJECT_NODE_WEIGHT = db.Column(db.Integer, nullable=True)
    PREDICATE_WEIGHT = db.Column(db.Integer, nullable=True)
    KP_WEIGHT = db.Column(db.Integer, nullable=True)
