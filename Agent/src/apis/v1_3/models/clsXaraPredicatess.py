from modDatabase import db
tableName = "xARA_Predicates"


class clsXaraPredicatess(db.Model):

    __tablename__ = tableName
    __table_args__ = (
        db.Index(
            f'uk_{tableName}_Predicate_key',
            'Predicate_key',
            unique=True
        ),
    )

   
    Predicate_key = db.Column(db.Integer, primary_key=True, autoincrement=False, nullable=False)
    Predicate_name = db.Column(db.String(255), nullable=True)