"""
Builds query analysis information to then execute a solution plan.
Voc P 3 Step 5
"""
import networkx
from .clsQueryGraph import clsNode, clsPredicate, clsTriplet


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
                target_node = clsNode(target, target_data)

                triplet = clsTriplet(
                    source_node,
                    clsPredicate(edge_data["__id"], edge_data),
                    target_node
                )
                self.triplets.append(triplet)
                assigned_node_ids.add(source)
                assigned_node_ids.add(target)
            # for node_id, node_data in self.query_nx_graph.nodes(data=True):
            #     if clsQueryPath.ids_property in node_data and len(node_data[clsQueryPath.ids_property]) > 0:
            #         in_edges = list(self.query_nx_graph.in_edges(node_id, data=True))
            #         out_edges = list(self.query_nx_graph.out_edges(node_id, data=True))
            #         if len(in_edges) > 0:
            #             edge_source = in_edges[0][0]
            #             edge_target = in_edges[0][1]
            #             edge_data = in_edges[0][2]
            #         elif len(out_edges) > 0:
            #             edge_source = out_edges[0][0]
            #             edge_target = out_edges[0][1]
            #             edge_data = out_edges[0][2]
            #         else:
            #             raise ValueError(f"Node ID '{node_id}' has no edges!")
            #
            #         opposite_node_id = list({edge_source, edge_target} - {node_id})[0]
            #         opposite_node_data = self.query_nx_graph.nodes[opposite_node_id]
            #
            #         triplet = clsTriplet(
            #             clsNode(node_id, node_data),
            #             clsPredicate(edge_data["__id"], edge_data),
            #             clsNode(opposite_node_id, opposite_node_data)
            #         )
            #         self.triplets.append(triplet)
            #         assigned_node_ids.add(node_id)
            #         assigned_node_ids.add(opposite_node_id)
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
                target_node = clsNode(target, target_data)

                triplet = clsTriplet(
                    source_node,
                    clsPredicate(edge_data["__id"], edge_data),
                    target_node
                )
                self.triplets.append(triplet)
                assigned_node_ids.add(source)
                assigned_node_ids.add(target)

        pass

        # def walk_graph(given_node_id, given_edges, steps_left):
        #     if steps_left <= 0:
        #         return
        #
        #     for source_node_id, target_node_id in given_edges:
        #         source_data = self.query_nx_graph.nodes[source_node_id]
        #         target_data = self.query_nx_graph.nodes[target_node_id]
        #         edge_data = self.query_nx_graph.get_edge_data(source_node_id, target_node_id)
        #
        #         if given_node_id == target_node_id and source_node_id not in assigned_node_ids:
        #             triplet = clsTriplet(
        #                 clsNode(target_node_id, target_data),
        #                 clsPredicate(edge_data["__id"], edge_data),
        #                 clsNode(source_node_id, source_data),
        #             )
        #             self.triplets.append(triplet)
        #             assigned_node_ids.add(source_node_id)
        #             new_edges = list(self.query_nx_graph.in_edges(source_node_id)) + list(self.query_nx_graph.out_edges(source_node_id))
        #             walk_graph(source_node_id, new_edges, steps_left - 1)
        #
        #         elif given_node_id == source_node_id and target_node_id not in assigned_node_ids:
        #             triplet = clsTriplet(
        #                 clsNode(source_node_id, source_data),
        #                 clsPredicate(edge_data["__id"], edge_data),
        #                 clsNode(target_node_id, target_data),
        #             )
        #             self.triplets.append(triplet)
        #             assigned_node_ids.add(target_node_id)
        #             new_edges = list(self.query_nx_graph.in_edges(target_node_id)) + list(self.query_nx_graph.out_edges(target_node_id))
        #             walk_graph(target_node_id, new_edges, steps_left - 1)
        #
        # final_opposite_id = self.triplets[-1].opposite_node.id
        # opposite_edges = list(self.query_nx_graph.in_edges(final_opposite_id)) + list(self.query_nx_graph.out_edges(final_opposite_id))
        # walk_graph(final_opposite_id, opposite_edges, len(self.query_nx_graph.edges))
        #
        # unassigned_nodes = []
        # node_ids_ordered = sorted(self.query_nx_graph.nodes)
        # for node_id in node_ids_ordered:
        #     if node_id not in assigned_node_ids:
        #         node_data = self.query_nx_graph.nodes[node_id]
        #         unassigned_nodes.append(clsNode(node_id, node_data))

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


