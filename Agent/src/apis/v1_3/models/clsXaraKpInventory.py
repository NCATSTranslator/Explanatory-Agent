from modDatabase import db
tableName = "xARA_KP_Inventory"


class clsXaraKpInventory(db.Model):

    __tablename__ = tableName
    # __table_args__ = (
    #     db.Index(
    #         f'uk_{tableName}_CASE_ID',
    #         'CASE_ID',
    #         unique=True
    #     ),
    # )

    No_of_nodes	= db.Column(db.Integer, nullable=True)
    No_of_edges	= db.Column(db.Integer, nullable=True)

    N00_category = db.Column(db.String(255), nullable=True)
    N01_category = db.Column(db.String(255), nullable=True)
    N02_category = db.Column(db.String(255), nullable=True)
    N03_category = db.Column(db.String(255), nullable=True)
    
    E00_predicate = db.Column(db.String(255), nullable=True)
    E00_ends = db.Column(db.String(255), DEFAULT = 'n00:n01', nullable=False),
    
    E01_predicate = db.Column(db.String(255), nullable=True)
    E01_ends = db.Column(db.String(255), nullable=True)
    
    E02_predicate = db.Column(db.String(255), nullable=True)
    E02_ends = db.Column(db.String(255), nullable=True)
   
    KP_to_query	= db.Column(db.String(255), nullable=True)
