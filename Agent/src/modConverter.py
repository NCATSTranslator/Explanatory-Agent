from reasoner_converter.upgrading import upgrade_Node, upgrade_NodeBinding, upgrade_Edge, upgrade_EdgeBinding
import os
import json
import reasoner_validator

# pathToConvert = os.path.join(os.getcwd(), "apis", "v1_0", "models", "test")
# for root,subdirs,files in os.walk(pathToConvert):
#     for file in files:
#         if file.endswith(".txt"):


fullPath = os.path.join(os.getcwd(), "apis", "v1_0", "models", "test", "test_user_request_body_nominal.json")

with open(fullPath) as file:
    fileDataRaw = json.load(file)

with open(fullPath) as file:
    fileDataClean = json.load(file)


def updateValueBasedOnKey(key, value):
    if key == "nodes":
        return [upgrade_Node(value_) for value_ in value]
    if key == "edges":
        return [upgrade_Edge(value_) for value_ in value]
    if key == "node_bindings":
        return [upgrade_NodeBinding(value_) for value_ in value]
    if key == "edge_bindings":
        return [upgrade_EdgeBinding(value_) for value_ in value]
    return value


def iterateDictionary(dictionary):
    for key, value in dictionary.items():
        dictionary[key] = updateValueBasedOnKey(key=key, value=value)
        if isinstance(value, dict):
            iterateDictionary(value)

iterateDictionary(fileDataClean)

x = 5







nominal = {
    "query_graph": {
        "edges": {
            "e00": {
                "subject": "n00",
                "object": "n01",
                "type": "biolink:associated"
            }
        },
        "nodes": {
            "n00": {
                "curie": "EFO:0004465",
                "type": "biolink:Disease"
            },
            "n01": {
                "type": "biolink:Gene"
            }
        }
    }
}


reasoner_validator.validate(nominal)

x = 5