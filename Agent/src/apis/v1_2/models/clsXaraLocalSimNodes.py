from modDatabase import db
tableName = "xARA_LocalSimNodes"


class clsXaraLocalSimNodes(db.Model):

    __tablename__ = tableName
    # __table_args__ = (
    #     db.Index(
    #         f'uk_{tableName}_CASE_ID',
    #         'CASE_ID',
    #         unique=True
    #     ),
    # )


    Node_1 = db.Column(db.String(255), nullable=True)
    Node_2 = db.Column(db.String(255), nullable=True)
    Similarity_score = db.Column(db.Integer, nullable=True)