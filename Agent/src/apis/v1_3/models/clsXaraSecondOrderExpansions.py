from modDatabase import db
tableName = "xARA_SecondOrderExpansions"


class clsXaraSecondOrderExpansions(db.Model):

    __tablename__ = tableName
    # __table_args__ = (
    #     db.Index(
    #         f'uk_{tableName}_CASE_ID',
    #         'CASE_ID',
    #         unique=True
    #     ),
    # )


    N00_category = db.Column(db.String(255), nullable=True)
    N01_category = db.Column(db.String(255), nullable=True)
   
    E00_predicate = db.Column(db.String(255), nullable=True)
  
    Expanded_N00_category = db.Column(db.String(255), nullable=True)
    Expanded_N01_category = db.Column(db.String(255), nullable=True)
    Expanded_N02_category = db.Column(db.String(255), nullable=True)
   
    Expanded_E00_predicate = db.Column(db.String(255), nullable=True)
    Expanded_E01_predicate = db.Column(db.String(255), nullable=True)
