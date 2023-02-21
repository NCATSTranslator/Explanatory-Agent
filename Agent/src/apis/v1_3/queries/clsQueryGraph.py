from typing import *


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


class clsQualifier:
    def __init__(self, qualifier_type_id, qualifier_value):
        self.qualifier_type_id = qualifier_type_id
        self.qualifier_value = qualifier_value

    def json(self):
        return {
            "qualifier_type_id": self.qualifier_type_id,
            "qualifier_value": self.qualifier_value
        }

    def __repr__(self):
        return f"'{self.qualifier_type_id}': '{self.qualifier_value}'"

    def __eq__(self, other):
        return self.qualifier_type_id == other.qualifier_type_id and self.qualifier_value == other.qualifier_value


class clsQualifierConstraint:
    def __init__(self, qualifier_set: List[clsQualifier]):
        self.qualifier_set: List[clsQualifier] = qualifier_set

    def json(self):
        qualifiers = []
        for qualifier_set in self.qualifier_set:
            qualifiers.append(qualifier_set.json())

        return {
            "qualifier_set": qualifiers
        }

    def __repr__(self):
        return f"QualifierConstraint: {self.qualifier_set}"

    def __eq__(self, other):
        return self.qualifier_set == other.qualifier_set


class clsTriplet:
    def __init__(self, source_node: clsNode, predicate: clsPredicate, target_node: clsNode):
        self.source_node = source_node
        self.predicate = predicate
        self.target_node = target_node

    def __repr__(self):
        return f"Source: {self.source_node}, Predicate: {self.predicate}, Opposite: {self.target_node}"

    def __eq__(self, other):
        return self.source_node == other.source_node and self.predicate == other.predicate and self.target_node == other.target_node
