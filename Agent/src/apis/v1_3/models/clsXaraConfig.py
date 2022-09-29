from modDatabase import db
tableName = "xARA_Config"


class clsXaraConfig(db.Model):

    __tablename__ = tableName
    # __table_args__ = (
    #     db.Index(
    #         f'uk_{tableName}_CASE_ID',
    #         'CASE_ID',
    #         unique=True
    #     ),
    # )

    MAX_ARS_HOPS = db.Column(db.Integer, nullable=True)
    GLOBAL_QUERY_THRESHOLD = db.Column(db.Integer, nullable=True)
    GLOBAL_RESULT_THRESHOLD = db.Column(db.Integer, nullable=True)
    
