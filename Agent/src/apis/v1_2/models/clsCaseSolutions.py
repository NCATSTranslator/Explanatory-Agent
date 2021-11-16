from modDatabase import db
tableName = "v1_1_CaseSolutions"


class clsCaseSolutions(db.Model):

    __tablename__ = tableName
    __table_args__ = (
        db.CheckConstraint(
            """
            (
                "KnowledgeProviderPathCount" = 1 and
                "KnowledgeProviderPath2Name" is null and
                "Node1Path2Category" is null and
                "Node1Path2Type" is null and
                "Node1Path2Reference" is null and
                "Node2Path2Category" is null and
                "Node2Path2Type" is null and
                "Node2Path2Reference" is null and
                "Edge1Path2Predicate" is null and
                "Edge1Path2Ends" is null and
                "Edge1Path2Reference" is null
            ) OR (
                "KnowledgeProviderPathCount" = 2 and
                "KnowledgeProviderPath2Name" is not null and
                "Node1Path2Category" is not null and
                "Node1Path2Type" is not null and
                "Node1Path2Reference" is not null and
                "Node2Path2Category" is not null and
                "Node2Path2Type" is not null and
                "Node2Path2Reference" is not null and
                "Edge1Path2Predicate" is not null and
                "Edge1Path2Ends" is not null and
                "Edge1Path2Reference" is not null and
                "Node2Path1Category" = "Node1Path2Category"
            )
            """,
            f"chk_{tableName}_KnowledgeProviderPathCount"
        ),
    )

    Id = db.Column(db.BigInteger, primary_key=True, autoincrement=False, nullable=False)
    CaseId = db.Column(db.String(255), nullable=False)
    Origin = db.Column(db.String(255), nullable=False)

    KnowledgeProviderPathCount = db.Column(db.SmallInteger, nullable=False)
    KnowledgeProviderPath1Name = db.Column(db.String(255), nullable=False)
    KnowledgeProviderPath2Name = db.Column(db.String(255), nullable=True)

    Node1Path1Category = db.Column(db.String(255), nullable=False)
    Node1Path1Type = db.Column(db.String(255), nullable=False)
    Node1Path1Reference = db.Column(db.String(255), nullable=False)

    Node2Path1Category = db.Column(db.String(255), nullable=False)
    Node2Path1Type = db.Column(db.String(255), nullable=False)
    Node2Path1Reference = db.Column(db.String(255), nullable=False)

    Edge1Path1Predicate = db.Column(db.String(255), nullable=False)
    Edge1Path1Ends = db.Column(db.String(255), nullable=False)
    Edge1Path1Reference = db.Column(db.String(255), nullable=False)

    Node1Path2Category = db.Column(db.String(255), nullable=True)
    Node1Path2Type = db.Column(db.String(255), nullable=True)
    Node1Path2Reference = db.Column(db.String(255), nullable=True)

    Node2Path2Category = db.Column(db.String(255), nullable=True)
    Node2Path2Type = db.Column(db.String(255), nullable=True)
    Node2Path2Reference = db.Column(db.String(255), nullable=True)

    Edge1Path2Predicate = db.Column(db.String(255), nullable=True)
    Edge1Path2Ends = db.Column(db.String(255), nullable=True)
    Edge1Path2Reference = db.Column(db.String(255), nullable=True)
