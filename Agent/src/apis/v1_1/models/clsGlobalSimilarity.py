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

    Id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)
    Subject = db.Column(db.String(255))
    Object = db.Column(db.String(255))
    Predicate = db.Column(db.String(255))
    CaseId = db.Column(db.String(255))
    CaseValue = db.Column(db.Float)
