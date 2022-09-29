

class clsNode:
    def __init__(self, identifier, data):
        self.id = identifier
        self.data = data

    def __repr__(self):
        return f"{self.id}, {self.data}"

    def __eq__(self, other):
        return self.id == other.id and self.data == other.data


class clsPredicate:
    def __init__(self, identifier, data):
        self.id = identifier
        self.data = data

    def __repr__(self):
        return f"{self.id}, {self.data}"

    def __eq__(self, other):
        return self.id == other.id and self.data == other.data


class clsTriplet:
    def __init__(self, source_node: clsNode, predicate: clsPredicate, target_node: clsNode):
        self.source_node = source_node
        self.predicate = predicate
        self.target_node = target_node

    def __repr__(self):
        return f"Source: {self.source_node}, Predicate: {self.predicate}, Opposite: {self.target_node}"

    def __eq__(self, other):
        return self.source_node == other.source_node and self.predicate == other.predicate and self.target_node == other.target_node
