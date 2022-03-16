class clsExplanationBase:

    def edgeAttributeValidate(self, edge):
        """
        Returns how many attributes in the edge meet the case criteria
        """
        raise NotImplementedError

    def attribute_has_value(self, attribute_value, test_value):
        """
        Checks if an attribute object has a key with the specified value. As there are no standards on value content (e.g. a string or a list of strings)
        we have to check thoroughly.
        NOTE: We only check the FIRST value when comparing a list!
        :param key:
        :param value:
        :return:
        """
        if isinstance(attribute_value, list):
            return attribute_value[0] == test_value
        else:
            return attribute_value == test_value

    def find_edge_similarity_scores(self, edge, score_attribute_lower, score_attribute_key='attribute_type_id'):
        result = []
        for attribute in edge["attributes"]:
            if score_attribute_key in attribute and attribute[score_attribute_key].lower() == score_attribute_lower:
                result.append(attribute['value'])
        return result

    def find_min_max_similarity_scores(self, knowledge_graph, score_attribute_lower, score_attribute_key='attribute_type_id'):
        similarity_scores = []
        for edge in knowledge_graph['edges'].values():
            similarity_scores.extend(self.find_edge_similarity_scores(edge, score_attribute_lower, score_attribute_key=score_attribute_key))

        if len(similarity_scores) == 0:
            return None, None

        return min(similarity_scores), max(similarity_scores)

    @staticmethod
    def value_not_empty(attribute):
        return attribute['value'] is not None and attribute['value'] != ''

    @staticmethod
    def find_node_edge_ids(query_graph):
        """
        Returns edge_id, node1_id, node2_id from the query graph.
        Returns: edge id, subject node id, object node id
        """
        edge_id = list(query_graph["edges"].keys())[0]
        node_ids = sorted(list(query_graph["nodes"].keys()))
        return edge_id, query_graph['edges'][edge_id]['subject'], query_graph['edges'][edge_id]['object']

    @staticmethod
    def enumerate_edges(knowledge_graph):
        # sorting for deterministic results. This can go away after index isn't used for rank.
        yield from enumerate(sorted(list(knowledge_graph['edges'].items()), key=lambda i: i[0]))
