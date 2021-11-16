
from modDatabase import db
tableName = "xARA_QueryWeights"


class clsXaraQueryWeights(db.Model):

    __tablename__ = tableName
    # __table_args__ = (
    #     db.Index(
    #         f'uk_{tableName}_CASE_ID',
    #         'CASE_ID',
    #         unique=True
    #     ),
    # )

    SUBJECT_NODE_WEIGHT	= db.Column(db.Integer, nullable=True)
    OBJECT_NODE_WEIGHT = db.Column(db.Integer, nullable=True)
    PREDICATE_WEIGHT = db.Column(db.Integer, nullable=True)