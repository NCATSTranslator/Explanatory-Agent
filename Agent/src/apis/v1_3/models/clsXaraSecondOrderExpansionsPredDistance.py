from modDatabase import db
tableName = "xARA_SecondOrderExpansions_PredDistance"


class clsXaraSecondOrderExpansionsPredDistance(db.Model):

    __tablename__ = tableName
    # __table_args__ = (
    #     db.Index(
    #         f'uk_{tableName}_CASE_ID',
    #         'CASE_ID',
    #         unique=True
    #     ),
    # )

    N00_category = db.Column(db.String(255), nullable=True)
    N00_type = db.Column(db.String(255), nullable=True)
    
    N01_category = db.Column(db.String(255), nullable=True)
    N01_type = db.Column(db.String(255), nullable=True)
    
    E00_predicate = db.Column(db.String(255), nullable=True)
    
    Expanded_first_node_category = db.Column(db.String(255), nullable=True)
    Expanded_second_node_category = db.Column(db.String(255), nullable=True)
    Expanded_third_node_category = db.Column(db.String(255), nullable=True)
    
    Expanded_first_edge_predicate = db.Column(db.String(255), nullable=True)
    Expanded_second_edge_predicate = db.Column(db.String(255), nullable=True)
   
    Predicate_Distance = db.Column(db.Integer, nullable=True)
