from modDatabase import db
tableName = "v1_1_GlobalSimilarity"


class clsGlobalSimilarity(db.Model):

    __tablename__ = tableName
    __table_args__ = (
        db.Index(
            f'uk_{tableName}_Subject_Object_Predicate_CaseId',
            'Subject', 'Object', 'Predicate', 'CaseId',
            unique=True
        ),
    )

    Id = db.Column(db.BigInteger, primary_key=True, autoincrement=False, nullable=False)
    Subject = db.Column(db.String(255), nullable=False)
    Object = db.Column(db.String(255), nullable=False)
    Predicate = db.Column(db.String(255), nullable=False)
    CaseId = db.Column(db.String(255), nullable=False)
    CaseValue = db.Column(db.Float, nullable=False)
