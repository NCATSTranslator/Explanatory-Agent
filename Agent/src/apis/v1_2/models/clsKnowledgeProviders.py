from modDatabase import db
tableName = "v1_1_KnowledgeProviders"


class clsKnowledgeProviders(db.Model):

    __tablename__ = tableName
    __table_args__ = (
        db.Index(
            f'uk_{tableName}_Name',
            'Name',
            unique=True
        ),
    )

    Id = db.Column(db.BigInteger, primary_key=True, autoincrement=False, nullable=False)
    Name = db.Column(db.String(255), nullable=False)
    Url = db.Column(db.Text, nullable=False)
