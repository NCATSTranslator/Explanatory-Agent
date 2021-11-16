from modDatabase import db
tableName = "xARA_KP_ExplanationExclusions"


class clsXaraKpExplanationExclusions(db.Model):

    __tablename__ = tableName
    # __table_args__ = (
    #     db.Index(
    #         f'uk_{tableName}_CASE_ID',
    #         'CASE_ID',
    #         unique=True
    #     ),
    # )

    KP = db.Column(db.String(255), nullable=True)
