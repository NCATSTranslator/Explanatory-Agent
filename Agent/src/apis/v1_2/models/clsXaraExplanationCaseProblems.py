from modDatabase import db
tableName = "xARA_ExplanationCaseProblems"


class clsXaraExplanationCaseProblems(db.Model):

    __tablename__ = tableName
    __table_args__ = (
        db.Index(
            f'uk_{tableName}_CASE_ID',
            'CASE_ID',
            unique=True
        ),
    )

    CASE_ID = db.Column(db.String(255), primary_key=True, autoincrement=False, nullable=False)
    CASE_NAME = db.Column(db.String(255), nullable=True)
    KP_NAME	= db.Column(db.String(255), nullable=True)
   
    SUBJECT_NODE = db.Column(db.String(255), nullable=True)
    OBJECT_NODE	= db.Column(db.String(255), nullable=True)
    PREDICATE = db.Column(db.String(255), nullable=True)
    
    SLOT_LABEL_0	= db.Column(db.String(255), nullable=True)
    SLOT_VALUE_0	= db.Column(db.String(255), nullable=True)
    
    SLOT_LABEL_1	= db.Column(db.String(255), nullable=True)
    SLOT_VALUE_1	= db.Column(db.String(255), nullable=True)
    
    SLOT_LABEL_2	= db.Column(db.String(255), nullable=True)
    SLOT_VALUE_2	= db.Column(db.String(255), nullable=True)
    
    SLOT_LABEL_3	= db.Column(db.String(255), nullable=True)
    SLOT_VALUE_3	= db.Column(db.String(255), nullable=True)
    
    SLOT_LABEL_4	= db.Column(db.String(255), nullable=True)
    SLOT_VALUE_4	= db.Column(db.String(255), nullable=True)
    
    SLOT_LABEL_5	= db.Column(db.String(255), nullable=True)
    SLOT_VALUE_5	= db.Column(db.String(255), nullable=True)
    
    SLOT_LABEL_6	= db.Column(db.String(255), nullable=True)
    SLOT_VALUE_6	= db.Column(db.String(255), nullable=True)
    
    SLOT_LABEL_7	= db.Column(db.String(255), nullable=True)
    SLOT_VALUE_7	= db.Column(db.String(255), nullable=True)