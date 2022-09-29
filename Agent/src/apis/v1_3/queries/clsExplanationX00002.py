"""
(FOR every edge:)
    Assign "The score was obtained based on the relationship between biomedical entities found in published literature." to the value of "attribute_type_id": "biolink:description"

(FOR every edge:)
    Call function Voc P 8: find_node_synonyms () with 1 parameter:
        a) NodeID - (Subject Node the first time)
    RETURN Subject Node Synonyms List
    Call function Voc P 8: find_node_synonyms () with 1 parameter:
        a) NodeID - (Object Node the first time)
    RETURN Object Node Synonyms List
    Call function Sol P 4: relationship_finder() with 4 parameters:
        a) Subject Node Category
        b) Subject Node Synonyms List
        c) Object Node Category
        d) Object Node Synonyms List
"""

from collections import OrderedDict
import copy
from modDatabase import db
import time
from .clsNodeNormalizerProvider import clsNodeNormalizerProvider
from .clsNameResolutionProvider import clsNameResolutionProvider
from utils.biobert.relationship_classification import relationship_classification
from utils.clsLog import clsLogEvent
from modConfig import ZERO_RESULT_SCORE
import re
import logging

from .clsExplanationBase import clsExplanationBase

class ExplanationX00002(clsExplanationBase):
    def __init__(self, app):
        self.case_id = "X00002"
        self.app = app
        self.valid_categories = {"biolink:drug", "biolink:smallmolecule", "biolink:gene", "biolink:protein", "biolink:geneproduct", "biolink:geneorgeneproduct"}
        self.logs = []

    def identify_edge(self, edge_id):
        """
        Match the edge names present in the edge id
        :param edge_id:
        :return:
        """
        found_edge_values = set()

        for edge_value in self.edge_values:
            if edge_value in edge_id.upper():
                found_edge_values.add(edge_value)

        explanation, score = self.value_combinations[frozenset(found_edge_values)]

        return explanation, score

    def edgeAttributeValidate(self, edge):
        """
        No attribute criteria, so this explanation should not be used.
        :param edge:
        :return:
        """
        return False

    def find_references(self, synonyms, categories):
        """
        FOR every Subject Node Synonym in Subject Node Synonyms List:
            IF Subject Node Category=="biolink:Drug" or Subject Node Category=="biolink:SmallMolecule":
                Search the synonym in the "CHEM_TOKS" field from the CHEM_TOKS_TEXT table in the Biomedical Publications Database and extract the Sentence
                  Record (ID, Article_Number, Article_ID, SENT_ID, SENT_TEXT, CHEM_TOKS)
            ELSE IF Subject Node Category=="biolink:Gene" or Subject Node Category=="biolink:Protein" or Subject Node Category=="biolink:GeneProduct"
                    or Subject Node Category=="biolink:GeneOrGeneProduct":
                  Search the synonym in the "GENE_TOKS" column from the GENE_TOKS_TEXT table in the Biomedical Publications Database Records and extract the
                    Sentence Record (ID, Article_Number, Article_ID, SENT_ID, SENT_TEXT, GENE_TOKS).

            ELSE IF Subject Node Category=="biolink:Disease" or
                Subject Node Category=="biolink:PhenotypicFeature" or
                Subject Node Category=="biolink:DiseaseOrPhenotypicFeature":
                Search the synonym in the "DIS_TOKS" column from the DIS_TOKS_TEXT table in the Biomedical Publications Database Records and extract
                  the Sentence Record (ID, Article_Number, Article_ID, SENT_ID, 	SENT_TEXT, DIS_TOKS).

            FOR every Object Node Synonym in Object Node Synonyms
            List:
                IF Object Node Category=="biolink:Drug" or Object Node Category=="SmallMolecule":
                    Search the synonym in the "CHEM_TOKS" column from the CHEM_TOKS_TEXT table in the Biomedical Publications Database and extract the
                      Sentence Record (ID, Article_Number, Article_ID, SENT_ID, SENT_TEXT, CHEM_TOKS).
                ELSE IF Object Node Category=="biolink:Gene" or Object Node Category=="biolink:Protein"
                        or Object Subject Node Category=="biolink:GeneProduct" or Object Node Category=="biolink:GeneOrGeneProduct":
                      Search the synonym in the "GENE_TOKS" column from the GENE_TOKS_TEXT table in the Biomedical Publications Database and extract the
                        Sentence Record (ID, Article_Number, Article_ID, SENT_ID, SENT_TEXT, GENE_TOKS).
                ELSE IF Object Node Category=="biolink:Disease" or Object Node Category=="biolink:PhenotypicFeature"
                        or Object Node Category=="biolink:DiseaseOrPhenotypicFeature":
                       Search the synonym in the "DIS_TOKS" column from the DIS_TOKS_TEXT table in the Biomedical Publications Databas
                       Records and extract the Sentence Record (ID, Article_Number, Article_ID, SENT_ID, SENT_TEXT, DIS_TOKS).


        :param synonyms:
        :param categories:
        :return:
        """
        synonyms = [s.lower() for s in synonyms]
        categories = [c.lower() for c in categories]

        if "biolink:drug" in categories or "biolink:smallmolecule" in categories:
            query = """SELECT "ID", "Article_Number", "Article_ID", "SENT_ID", "SENT_TEXT", "CHEM_TOKS" as "TOKS" FROM public."CHEM_TOKENS_TEXT" WHERE "CHEM_TOKS" = ANY(array[:synonyms]);"""
        elif "biolink:gene" in categories or "biolink:protein" in categories or "biolink:geneproduct" in categories or "biolink:geneorgeneproduct" in categories:
            query = """SELECT "ID", "Article_Number", "Article_ID", "SENT_ID", "SENT_TEXT", "GENE_TOKS" as "TOKS" FROM public."GENE_TOKENS_TEXT" WHERE "GENE_TOKS" = ANY(array[:synonyms]);"""
        # elif "biolink:disease" in categories or "biolink:phenotypicfeature" in categories or "biolink:diseaseorphenotypicfeature" in categories:
        #     query = ""
        else:
            return []

        with self.app.app_context():
            results = db.session.execute(query, {"synonyms": synonyms}).mappings().all()


        matches = []
        for result in results:
            matches.append(dict(result))

        return matches

    no_found_references_attributes = [
        {
            "original_attribute_name": "Explanation Rationale",
            "attribute_type_id": "biolink:description",
            "value": "The score was obtained based on the relationship between biomedical entities found in published literature.",
            "description": "Describes to user the Rationale for explaining the ranking"
        },
        {
            "original_attribute_name": "Explanation Text",
            "attribute_type_id": "biolink:has_evidence",
            "value": "No Records Found for any Subject Node or Object Node",
            "description": "Describes the reason this specific edge receives a score w.r.t Rationale"
        }
    ]

    no_matching_reference_pairs_attributes = [
        {
            "original_attribute_name": "Explanation Rationale",
            "attribute_type_id": "biolink:description",
            "value": "The score was obtained based on the relationship between biomedical entities found in published literature.",
            "description": "Describes to user the Rationale for explaining the ranking"
        },
        {
            "original_attribute_name": "Explanation Text",
            "attribute_type_id": "biolink:has_evidence",
            "value": "We found publications with both entities to attempt to identify an explicit relation; we recommend the user to look at the literature. Article IDs: ",
            "description": "Describes the reason this specific edge receives a score w.r.t Rationale"
        }
    ]

    reference_distance_too_large_attributes = [
        {
            "original_attribute_name": "Explanation Rationale",
            "attribute_type_id": "biolink:description",
            "value": "The score was obtained based on the relationship between biomedical entities found in published literature.",
            "description": "Describes to user the Rationale for explaining the ranking"
        },
        {
            "original_attribute_name": "Explanation Text",
            "attribute_type_id": "biolink:has_evidence",
            "value": "{} and {} in this edge are found in the same article ({}) but are not in close proximity to recognize whether the investigations support their relationship.",
            "description": "Describes the reason this specific edge receives a score w.r.t Rationale"
        }
    ]

    reference_model_fail_attributes = [
        {
            "original_attribute_name": "Explanation Rationale",
            "attribute_type_id": "biolink:description",
            "value": "The score was obtained based on the relationship between biomedical entities found in published literature.",
            "description": "Describes to user the Rationale for explaining the ranking"
        },
        {
            "original_attribute_name": "Explanation Text",
            "attribute_type_id": "biolink:has_evidence",
            "value": "{} and the {} in this edge are found in close proximity in article {} but our model was unable to clearly determine the relationship between the terms.",
            "description": "Describes the reason this specific edge receives a score w.r.t Rationale"
        }
    ]

    reference_model_pass_attributes = [
        {
            "original_attribute_name": "Explanation Rationale",
            "attribute_type_id": "biolink:description",
            "value": "The score was obtained based on the relationship between biomedical entities found in published literature.",
            "description": "Describes to user the Rationale for explaining the ranking"
        },
        {
            "original_attribute_name": "Explanation Text",
            "attribute_type_id": "biolink:has_evidence",
            "value": "'{subject_name}' and '{object_name}' in this edge are found in the same article. Based on the articles' text, the relationship between '{subject_name}' and '{object_name}' is of the type '{relation_label}'. See more details in paper '{article_title}' by {article_author}.",
            "description": "Describes the reason this specific edge receives a score w.r.t Rationale"
        }
    ]

    def create_results_and_explain(self, case_solution):
        query_graph = case_solution.query_graph
        knowledge_graph = case_solution.knowledge_graph

        e00_id, n00_id, n01_id = self.find_node_edge_ids(case_solution.query_graph)
        results = []

        start_time = time.time()

        # sorting edge IDs for deterministic results.
        edges = sorted(list(knowledge_graph['edges'].items()), key=lambda i: i[0])

        # bulk get all canonical identifiers for all node ids
        node_identifiers = set()
        for index, (edgeId, edge) in enumerate(edges):
            edge_subject = edge["subject"]
            edge_object = edge["object"]
            node_identifiers.add(edge_subject)
            node_identifiers.add(edge_object)
        logging.debug(f"Getting node identifiers")
        self.logs.append(clsLogEvent(
            identifier=self.case_id,
            level="DEBUG",
            code="",
            message=f"Getting all ({len(node_identifiers)}) node identifiers."
        ))
        node_normalizer_provider = clsNodeNormalizerProvider(sorted(list(node_identifiers)))
        node_normalizer_provider.get_identifiers()
        identifiers = node_normalizer_provider.identifiers

        # bulk get all synonyms
        logging.debug(f"Getting node synonyms")
        self.logs.append(clsLogEvent(
            identifier=self.case_id,
            level="DEBUG",
            code="",
            message=f"Getting all node synonyms."
        ))
        name_resolution_provider = clsNameResolutionProvider(sorted(list(identifiers.values())))
        name_resolution_provider.get_synonyms()

        # collect all edges that have acceptable sentences to bulk predict later
        predictable_edges = []

        for index, (edgeId, edge) in enumerate(edges):
            # # TODO: Remove! Debugging only!
            # if index > 10:
            #     break
            if index == 0:
                self.logs.append(clsLogEvent(
                    identifier=self.case_id,
                    level="DEBUG",
                    code="",
                    message=f"Starting explanations for {len(knowledge_graph['edges'])} edges."
                ))
            if index % 50 == 0 and index > 0:
                logging.debug(f"{self.case_id} edge {index} of {len(knowledge_graph['edges'])}")
                self.logs.append(clsLogEvent(
                    identifier=self.case_id,
                    level="DEBUG",
                    code="",
                    message=f"Explained {index} of {len(knowledge_graph['edges'])} edges."
                ))
            if time.time() > start_time + 3.0 * 60:
                self.logs.append(clsLogEvent(
                    identifier=self.case_id,
                    level="ERROR",
                    code="",
                    message=f"Explanation timeout."
                ))
                # break
                raise TimeoutError("Explanation execution ran too long")

            result = OrderedDict()
            result['edge_bindings'] = {
                e00_id: [{
                    "id": edgeId,
                }]
            }

            # TODO: Some KGs may have reversed edge subjects and objects compared to the result node bindings! Should use result node bindings instead.
            result['node_bindings'] = {
                n00_id: [{"id": edge['subject']}],
                n01_id: [{"id": edge['object']}],
            }

            edge_subject = edge["subject"]
            subject_categories = knowledge_graph['nodes'][edge_subject]['categories']
            subject_categories_lower = [s.lower() for s in subject_categories]
            edge_object = edge["object"]
            object_categories = knowledge_graph['nodes'][edge_object]['categories']
            object_categories_lower = [o.lower() for o in object_categories]

            self.logs.append(clsLogEvent(
                identifier=self.case_id,
                level="DEBUG",
                code="",
                message=f"Explaining edge {index+1}: {edgeId} Predicate {edge['predicate']}, Subject: {edge_subject} {subject_categories}, Object: {edge_object} {object_categories}."
            ))

            # if either the subject's or object's categories don't have tables representing them, stop.
            if len(set(subject_categories_lower) & self.valid_categories) == 0 or len(set(object_categories_lower) & self.valid_categories) == 0:
                result['score'] = ZERO_RESULT_SCORE
                result['attributes'] = ExplanationX00002.no_found_references_attributes
                results.append(result)
                continue

            subject_synonyms = name_resolution_provider.synonyms[identifiers[edge_subject]]

            logging.debug(f"{self.case_id} edge {index+1} of {len(knowledge_graph['edges'])} getting subject article references")
            self.logs.append(clsLogEvent(
                identifier=self.case_id,
                level="DEBUG",
                code="",
                message=f"Edge {edgeId} getting subject article references."
            ))
            subject_references = self.find_references(subject_synonyms, subject_categories)
            self.logs.append(clsLogEvent(
                identifier=self.case_id,
                level="DEBUG",
                code="",
                message=f"Edge {edgeId} Subject Synonyms: {subject_synonyms}, References: {len(subject_references)}."
            ))

            if len(subject_references) <= 0:
                result['score'] = ZERO_RESULT_SCORE
                result['attributes'] = ExplanationX00002.no_found_references_attributes
                results.append(result)
                continue

            object_synonyms = name_resolution_provider.synonyms[identifiers[edge_object]]
            logging.debug(f"{self.case_id} edge {index + 1} of {len(knowledge_graph['edges'])} getting object article references")
            self.logs.append(clsLogEvent(
                identifier=self.case_id,
                level="DEBUG",
                code="",
                message=f"Edge {edgeId} getting object article references."
            ))
            object_references = self.find_references(object_synonyms, object_categories)

            self.logs.append(clsLogEvent(
                identifier=self.case_id,
                level="DEBUG",
                code="",
                message=f"Edge {edgeId} Object Synonyms: {object_synonyms}, References: {len(object_references)}."
            ))

            # object_references = [
            #     {'ID': 261595, 'Article_Number': '1336', 'Article_ID': '288e7bf5d16ac18731d2f1ee7db6d6ed2a720cc2', 'SENT_ID': 85,
            #      'SENT_TEXT': 'On the other hand, AP2 and SP1 are known to activate epidermal growth factor receptor some chemical.',
            #      'TOKS': 'some chemical'}
            # ]

            if len(object_references) <= 0:
                self.logs.append(clsLogEvent(
                    identifier=self.case_id,
                    level="DEBUG",
                    code="",
                    message=f"Edge {edgeId} No object references found, stopping."
                ))
                result['score'] = ZERO_RESULT_SCORE
                result['attributes'] = ExplanationX00002.no_found_references_attributes
                results.append(result)
                continue

            # find matching article ids between the two lists of subject and object results
            matching_reference_pairs_by_article = {}
            for subject_reference in subject_references:
                for object_reference in object_references:
                    if subject_reference["Article_ID"] == object_reference["Article_ID"]:
                        if subject_reference["Article_ID"] not in matching_reference_pairs_by_article:
                            matching_reference_pairs_by_article[subject_reference["Article_ID"]] = []
                        matching_reference_pairs_by_article[subject_reference["Article_ID"]].append((subject_reference, object_reference))

            self.logs.append(clsLogEvent(
                identifier=self.case_id,
                level="DEBUG",
                code="",
                message=f"Edge {edgeId} Matched subject/object articles: {len(matching_reference_pairs_by_article)}."
            ))

            if len(matching_reference_pairs_by_article) <= 0:
                result['score'] = ZERO_RESULT_SCORE
                attributes = copy.deepcopy(ExplanationX00002.no_matching_reference_pairs_attributes)
                # get all unique PMIDs to return to the user
                pmids = set()
                for subject_reference in subject_references:
                    pmids.add(subject_reference['Article_ID'])
                for object_reference in object_references:
                    pmids.add(object_reference['Article_ID'])

                attributes[1]["value"] += ", ".join(pmids)
                result['attributes'] = attributes
                results.append(result)
                self.logs.append(clsLogEvent(
                    identifier=self.case_id,
                    level="DEBUG",
                    code="",
                    message=f"Edge {edgeId} No matched articles found, stopping."
                ))
                continue

            article_information = self.get_article_information(list(matching_reference_pairs_by_article.keys()))

            result['attributes'] = []
            score = 0.5

            pairs_to_predict = []
            for article_id, reference_pairs in matching_reference_pairs_by_article.items():
                if time.time() > start_time + 4.5 * 60:
                    self.logs.append(clsLogEvent(
                        identifier=self.case_id,
                        level="ERROR",
                        code="",
                        message=f"Explanation timeout."
                    ))
                    raise TimeoutError("Explanation execution ran too long")

                pair_distances = []
                for reference_pair in reference_pairs:
                    distance = abs(reference_pair[0]["SENT_ID"] - reference_pair[1]["SENT_ID"])
                    pair_distances.append((reference_pair, distance, reference_pair[0]["Article_Number"]))

                pair_distances.sort(key=lambda x: (x[1], x[2]))
                closest_reference_pair_data = pair_distances[0]
                closest_reference_pair = closest_reference_pair_data[0]

                self.logs.append(clsLogEvent(
                    identifier=self.case_id,
                    level="DEBUG",
                    code="",
                    message=f"Edge {edgeId} Article {article_id} closest pair distance {closest_reference_pair_data[1]}."
                ))

                if closest_reference_pair_data[1] > 9:
                    self.logs.append(clsLogEvent(
                        identifier=self.case_id,
                        level="DEBUG",
                        code="",
                        message=f"Edge {edgeId} Sentence distance too great: {closest_reference_pair_data[1]}, stopping."
                    ))
                # if False:
                    attributes = copy.deepcopy(ExplanationX00002.reference_distance_too_large_attributes)
                    attributes[1]["value"] = attributes[1]["value"].format(closest_reference_pair[0]["TOKS"], closest_reference_pair[1]["TOKS"], article_id)
                    result['attributes'] += attributes
                    result['score'] = score
                    # result['attributes'] = attributes
                    # results.append(result)
                    continue

                pairs_to_predict.append((article_id, closest_reference_pair))

                # # combine two sentences and wrap the matched text in special characters
                # subject_special_sentence = closest_reference_pair[0]['SENT_TEXT'].replace(closest_reference_pair[0]['TOKS'], f"<<{closest_reference_pair[0]['TOKS']}>>")
                # object_special_sentence = closest_reference_pair[1]['SENT_TEXT'].replace(closest_reference_pair[1]['TOKS'], f"[[{closest_reference_pair[1]['TOKS']}]]")
                # instance = f"{subject_special_sentence} {object_special_sentence}"
                # # data_try = 'Agonistic activity of << ICI 182 780 >> on activation of GSK 3β/[[ AKT ]] pathway in the rat uterus during the estrous cycle.'
                # self.logs.append(clsLogEvent(
                #     identifier=self.case_id,
                #     level="DEBUG",
                #     code="",
                #     message=f"Edge {edgeId} Beginning relationship classification..."
                # ))
                #
                # relation_label = relationship_classification(instance)
                # self.logs.append(clsLogEvent(
                #     identifier=self.case_id,
                #     level="DEBUG",
                #     code="",
                #     message=f"Edge {edgeId} Relationship classification finished {relation_label}"
                # ))
                # # import random
                # # random.seed(1234)
                # # relation_label = random.choice(["UPREGULATOR|ACTIVATOR|INDIRECT_UPREGULATOR", "DOWNREGULATOR|INHIBITOR|INDIRECT_DOWNREGULATOR", "AGONIST|AGONIST‐ACTIVATOR|AGONIST‐INHIBITOR", "ANTAGONIST", "SUBSTRATE|PRODUCT_OF|SUBSTRATE_PRODUCT_OF" "No RELATION"])
                #
                # if relation_label == "No RELATION":
                #     attributes = copy.deepcopy(ExplanationX00002.reference_model_fail_attributes)
                #     attributes[1]["value"] = attributes[1]["value"].format(closest_reference_pair[0]["TOKS"], closest_reference_pair[1]["TOKS"], article_id)
                #     result['attributes'] += attributes
                # else:
                #     article = article_information.get(article_id, {"Title": "Article Not Found", "Author": "Article Not Found"})
                #     attributes = copy.deepcopy(ExplanationX00002.reference_model_pass_attributes)
                #     attributes[1]["value"] = attributes[1]["value"].format(subject_name=closest_reference_pair[0]["TOKS"],
                #                                                            object_name=closest_reference_pair[1]["TOKS"],
                #                                                            relation_label=relation_label, article_title=article["Title"], article_author=article["Author"])
                #     result['attributes'] += attributes
                #     score = 1.0
                #
                # result['score'] = score

            if len(pairs_to_predict) > 0:
                self.logs.append(clsLogEvent(
                    identifier=self.case_id,
                    level="DEBUG",
                    code="",
                    message=f"Edge {edgeId} explanation queued."
                ))

                predictable_edges.append((edge, result, article_information, pairs_to_predict))
            else:
                results.append(result)

        if len(predictable_edges) > 0:
            prediction_sentences = []
            for edge, result, article_information, pairs_to_predict in predictable_edges:
                for article_id, closest_reference_pair in pairs_to_predict:
                    # combine two sentences and wrap the matched text in special characters
                    subject_pattern = re.compile(re.escape(str(closest_reference_pair[0]['TOKS'])), re.IGNORECASE)
                    subject_special_sentence = subject_pattern.sub(f"<<{closest_reference_pair[0]['TOKS']}>>", closest_reference_pair[0]['SENT_TEXT'])
                    # subject_special_sentence = closest_reference_pair[0]['SENT_TEXT'].replace(closest_reference_pair[0]['TOKS'], f"<<{closest_reference_pair[0]['TOKS']}>>")

                    object_pattern = re.compile(re.escape(str(closest_reference_pair[1]['TOKS'])), re.IGNORECASE)
                    object_special_sentence = object_pattern.sub(f"<<{closest_reference_pair[1]['TOKS']}>>", closest_reference_pair[1]['SENT_TEXT'])
                    # object_special_sentence = closest_reference_pair[1]['SENT_TEXT'].replace(closest_reference_pair[1]['TOKS'], f"[[{closest_reference_pair[1]['TOKS']}]]")
                    instance = f"{subject_special_sentence} {object_special_sentence}"
                    prediction_sentences.append(instance)

            t0 = time.time()
            relation_labels = relationship_classification(prediction_sentences)
            t1 = time.time()
            logging.debug(f"Predicting {len(prediction_sentences)} sentences took {t1-t0} seconds.")
            self.logs.append(clsLogEvent(
                identifier=self.case_id,
                level="DEBUG",
                code="",
                message=f"Predicting {len(prediction_sentences)} sentences took {t1-t0} seconds."
            ))

            # for i, (edge, article_id, closest_reference_pair, result) in enumerate(predictable_edges):
            prediction_index = 0
            for i, (edge, result, article_information, pairs_to_predict) in enumerate(predictable_edges):
                for j, (article_id, closest_reference_pair) in enumerate(pairs_to_predict):
                    relation_label = relation_labels[prediction_index]
                    self.logs.append(clsLogEvent(
                        identifier=self.case_id,
                        level="DEBUG",
                        code="",
                        message=f"Edge {edgeId} Beginning relationship classification..."
                    ))

                    # relation_label = relationship_classification(instance)
                    self.logs.append(clsLogEvent(
                        identifier=self.case_id,
                        level="DEBUG",
                        code="",
                        message=f"Edge {edgeId} Relationship classification finished {relation_label}"
                    ))
                    # import random
                    # random.seed(1234)
                    # relation_label = random.choice(["UPREGULATOR|ACTIVATOR|INDIRECT_UPREGULATOR", "DOWNREGULATOR|INHIBITOR|INDIRECT_DOWNREGULATOR", "AGONIST|AGONIST‐ACTIVATOR|AGONIST‐INHIBITOR", "ANTAGONIST", "SUBSTRATE|PRODUCT_OF|SUBSTRATE_PRODUCT_OF" "No RELATION"])

                    if relation_label == "No RELATION":
                        attributes = copy.deepcopy(ExplanationX00002.reference_model_fail_attributes)
                        attributes[1]["value"] = attributes[1]["value"].format(closest_reference_pair[0]["TOKS"], closest_reference_pair[1]["TOKS"], article_id)
                        result['attributes'] += attributes
                    else:
                        article = article_information.get(article_id, {"Title": "Article Not Found", "Author": "Article Not Found"})
                        attributes = copy.deepcopy(ExplanationX00002.reference_model_pass_attributes)
                        attributes[1]["value"] = attributes[1]["value"].format(subject_name=closest_reference_pair[0]["TOKS"],
                                                                               object_name=closest_reference_pair[1]["TOKS"],
                                                                               relation_label=relation_label, article_title=article["Title"], article_author=article["Author"])
                        result['attributes'] += attributes
                        score = 1.0

                    result['score'] = score

                    prediction_index += 1

                results.append(result)

        self.logs.append(clsLogEvent(
            identifier=self.case_id,
            level="DEBUG",
            code="",
            message=f"Explained all {len(knowledge_graph['edges'])} edges."
        ))

        return results

    def get_article_information(self, article_ids):
        """

        :param article_ids:
        :return:
        """
        article_information = {}
        with self.app.app_context():
            results = db.session.execute(
                """SELECT "Article_ID", "Article_Title", "Article_Author" FROM public."RAW_TEXT" WHERE "Article_ID" = ANY(array[:article_ids]);""",
                {"article_ids": article_ids}).mappings().all()
        for result in results:
            article_information[result["Article_ID"]] = {"Title": result["Article_Title"], "Author": result["Article_Author"]}

        return article_information
