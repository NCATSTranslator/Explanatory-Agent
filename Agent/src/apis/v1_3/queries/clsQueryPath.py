"""
Builds query analysis information to then execute a solution plan.
Voc P 3 Step 5
"""
import networkx
from .clsQueryGraph import clsNode, clsPredicate, clsTriplet, clsQualifier, clsQualifierConstraint


class clsQueryPath:
    ids_property = "ids"

    def __init__(self, query_graph: dict):
        self.query_graph = query_graph
        self.query_nx_graph = None
        self.edge_id_to_edge_mapping = None
        self.triplets = None
        self.unassigned_nodes = None

        self.convert_query_graph_to_digraph()

    def convert_query_graph_to_digraph(self):
        """
        Converts a TRAPI query graph into a networkx DiGraph
        :param query_graph:
        :return:
        """
        self.edge_id_to_edge_mapping = {}

        graph = networkx.DiGraph()

        for node_id, node_data in self.query_graph["nodes"].items():
            graph.add_node(node_id, **node_data)

        for edge_id, edge_data in self.query_graph["edges"].items():
            edge_data["__id"] = edge_id
            graph.add_edge(edge_data["subject"], edge_data["object"], **edge_data)
            self.edge_id_to_edge_mapping[edge_id] = (edge_data["subject"], edge_data["object"])

        self.query_nx_graph = graph

    @staticmethod
    def generate_qualifier_constraints(qualifier_constraint_objects):
        """
        Creates a list of QualifierConstraint objects from a JSON object from a QueryGraph
        :param qualifier_constraint_objects: List of Dictionaries following the '#/components/schemas/QualifierConstraint' JSON schema definition.
        :return: List of clsQualifierConstraint objects.
        """
        qualifier_constraints = []
        for qualifier_constraints_object in qualifier_constraint_objects:
            qualifiers = []
            for qualifier_set in qualifier_constraints_object.get('qualifier_set', []):
                qualifier = clsQualifier(qualifier_set.get('qualifier_type_id', 'NO_QUALIFIER_TYPE_ID'),
                                         qualifier_set.get('qualifier_value', 'NO_QUALIFIER_VALUE'))
                qualifiers.append(qualifier)
            qualifier_constraints.append(clsQualifierConstraint(qualifiers))

        return qualifier_constraints

    def create_plan(self):
        """
        Repeat steps (a) to (f) for each r' agent qg: 
        a) N_G = No. of nodes with ID or name (No. of given nodes) 
        b) If N_G == 0:
            No given node provided, invalid qg.
         c) If N_G == 1: 
             given_node[1] = Node with ID or name provided 
             opposite_node[1] = Other node that is pointed by the same edge 
             connected to given_node[1]
         d) If N_G > 1:
             For each edge (traverse ascending order of edge index): 
               i) Get nodes that are associated with the edge. 
               ii) Check if any node in selected edge have name or id. 
                 If yes: 
                   given_node[idx] = Node with name or id 
                   opposite_node[idx] = Other node that is pointed by same edge 
                 idx += 1 
                 (idx is index variable starting from 1 and increments by 1) 
                 Example: If there are more than one nodes with given name or id, priorities will be set on the ascending order of node's index.
                            If nodes: n0 and n2 have name/id, given_node[1] would be n0 and given_node[2] would be n2. opposite_node[1] would be other node
                            belonging in same edge as given_node[1] and same goes for opposite_node[2].
         e) For each node (noden) not assigned given_node or opposite_node: 
            node[idx] = noden 
            idx += 1 
            (idx is index variable starting from 1 and increments by 1) 
        f) For each edge predicate (predicaten) in agent qg: 
             pred[idx] = predicaten 
             idx += 1 
           (idx is index variable starting from 1 and increments by 1) 
        :return:
        """

        self.triplets = []
        assigned_node_ids = set()
        self.unassigned_nodes = []

        # identify nodes with ID
        nodes_with_ids = 0
        for node_id, node_data in self.query_nx_graph.nodes(data=True):
            if clsQueryPath.ids_property in node_data and len(node_data[clsQueryPath.ids_property]) > 0:
                nodes_with_ids += 1

        if nodes_with_ids <= 0:
            raise ValueError("Invalid Query Graph, no nodes present")
        elif nodes_with_ids == 1:
            edge_ids = sorted(list(self.query_graph["edges"]))
            for edge_id in edge_ids:
                source, target = self.edge_id_to_edge_mapping[edge_id]
                edge_data = self.query_nx_graph.get_edge_data(source, target)
                source_data = self.query_nx_graph.nodes[source]
                target_data = self.query_nx_graph.nodes[target]
                source_has_id = clsQueryPath.ids_property in source_data
                target_has_id = clsQueryPath.ids_property in target_data
                # if source_has_id == True and target_has_id == True:
                #     raise ValueError(f"Both nodes have ids: '{source}', '{target}'!")

                source_node = clsNode(source, source_data)
                predicate = clsPredicate(edge_data["__id"], edge_data)
                target_node = clsNode(target, target_data)
                if "qualifier_constraints" in edge_data:
                    qualifier_constraints = clsQueryPath.generate_qualifier_constraints(edge_data["qualifier_constraints"])
                else:
                    qualifier_constraints = None

                triplet = clsTriplet(
                    source_node,
                    predicate,
                    target_node
                )
                self.triplets.append(triplet)
                assigned_node_ids.add(source)
                assigned_node_ids.add(target)
        elif nodes_with_ids > 1:
            """
            For each edge (traverse ascending order of edge index): 
               i) Get nodes that are associated with the edge. 
               ii) Check if any node in selected edge have name or id. 
                 If yes: 
                   given_node[idx] = Node with name or id 
                   opposite_node[idx] = Other node that is pointed by same edge 
                 idx += 1 
            """
            edge_ids = sorted(list(self.query_graph["edges"]))
            for edge_id in edge_ids:
                source, target = self.edge_id_to_edge_mapping[edge_id]
                edge_data = self.query_nx_graph.get_edge_data(source, target)
                source_data = self.query_nx_graph.nodes[source]
                target_data = self.query_nx_graph.nodes[target]
                source_has_id = clsQueryPath.ids_property in source_data
                target_has_id = clsQueryPath.ids_property in target_data
                # if source_has_id == True and target_has_id == True:
                #     raise ValueError(f"Both nodes have ids: '{source}', '{target}'!")

                source_node = clsNode(source, source_data)
                predicate = clsPredicate(edge_data["__id"], edge_data)
                target_node = clsNode(target, target_data)
                if "qualifier_constraints" in edge_data:
                    qualifier_constraints = clsQueryPath.generate_qualifier_constraints(edge_data["qualifier_constraints"])
                else:
                    qualifier_constraints = None

                triplet = clsTriplet(
                    source_node,
                    predicate,
                    target_node
                )
                self.triplets.append(triplet)
                assigned_node_ids.add(source)
                assigned_node_ids.add(target)

    def ingest_case_solutions(self, triplets_case_solutions):
        assert len(triplets_case_solutions) == len(self.triplets)
        self.triplets_case_solutions = triplets_case_solutions

    def execute(self):
        """
        Run all case solutions sequentially across the triplets, so full paths may be returned once the system times out.
        :return:
        """
        for solution_index in range(len(self.triplets_case_solutions[0])):
            for triplet_index, triplet in enumerate(self.triplets):
                triplet_case_solution = self.triplets_case_solutions[triplet_index][solution_index]
                triplet_case_solution.execute()

    def __eq__(self, other):
        if len(self.triplets) != len(other.triplets):
            return False

        for i, triplet in enumerate(self.triplets):
            other_triplet = other.triplets[i]
            if triplet != other_triplet:
                return False

        return True


