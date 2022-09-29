from modDatabase import db
tableName = "xARA_KP_Info"


class clsXaraKpInfo(db.Model):

    __tablename__ = tableName
    # __table_args__ = (
    #     db.Index(
    #         f'uk_{tableName}_CASE_ID',
    #         'CASE_ID',
    #         unique=True
    #     ),
    # )

    KP_Name	= db.Column(db.String(255), nullable=True)
    Contact_Person = db.Column(db.String(255), nullable=True)
    Contact_Email = db.Column(db.String(255), nullable=True)
    URL	= db.Column(db.String(255), nullable=True)
    Priority = db.Column(db.Integer, nullable=True)
