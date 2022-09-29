import unittest
from apis.v1_3.queries.clsExplanationSolutionFinder import ExplanationSolutionFinder
from collections import namedtuple, OrderedDict
from flask import Flask, redirect, url_for
from flask_compress import Compress
import modConfig
from modDatabase import db
from apis.v1_3.queries.clsExplanationX00012 import ExplanationX00012


class TestExplanationSolutionFinder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # create flask app object with a name
        cls.app = Flask(__name__)

        # add compression
        Compress(cls.app)

        # store database config
        cls.app.config.update(modConfig.dbConfig)
        db.init_app(cls.app)  # bind to database

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_x00012(self):
        finder = ExplanationSolutionFinder(TestExplanationSolutionFinder.app)
        knowledge_graph = {
            "edges": {
                "knowledge_graph_edge1": {
                    "subject": "n1",
                    "object": "n2",
                    "attributes": [
                        {
                            "attribute_source": "infores:hmdb",
                            "attribute_type_id": "biolink:Publication",
                            "attributes": [],
                            "original_attribute_name": "reference",
                            "value": "PMID:21059682",
                            "value_type_id": "string"
                        },
                        {
                            "attribute_source": "infores:hmdb",
                            "attribute_type_id": "biolink:Publication",
                            "attributes": [],
                            "original_attribute_name": "reference",
                            "value": "PMID:1740537",
                            "value_type_id": "string"
                        },
                        {
                            "attribute_source": "infores:hmdb",
                            "attribute_type_id": "biolink:Publication",
                            "attributes": [],
                            "original_attribute_name": "reference",
                            "value": "PMID:17269711",
                            "value_type_id": "string"
                        },
                        {
                            "attribute_source": "infores:hmdb",
                            "attribute_type_id": "biolink:Publication",
                            "attributes": [],
                            "original_attribute_name": "reference",
                            "value": "PMID:17314143",
                            "value_type_id": "string"
                        },
                        {
                            "attribute_source": "infores:hmdb",
                            "attribute_type_id": "biolink:Publication",
                            "attributes": [],
                            "original_attribute_name": "reference",
                            "value": "PMID:21761941",
                            "value_type_id": "string"
                        },
                        {
                            "attribute_source": "infores:hmdb",
                            "attribute_type_id": "biolink:Publication",
                            "attributes": [],
                            "original_attribute_name": "reference",
                            "value": "PMID:23516449",
                            "value_type_id": "string"
                        },
                        {
                            "attribute_source": "infores:hmdb",
                            "attribute_type_id": "biolink:Publication",
                            "attributes": [],
                            "original_attribute_name": "reference",
                            "value": "PMID:23867873",
                            "value_type_id": "string"
                        },
                        {
                            "attribute_source": "infores:hmdb",
                            "attribute_type_id": "biolink:Publication",
                            "attributes": [],
                            "original_attribute_name": "reference",
                            "value": "PMID:24811995",
                            "value_type_id": "string"
                        },
                        {
                            "attribute_source": "infores:hmdb",
                            "attribute_type_id": "biolink:Publication",
                            "attributes": [],
                            "original_attribute_name": "reference",
                            "value": "PMID:25598765",
                            "value_type_id": "string"
                        },
                        {
                            "attribute_source": "infores:hmdb",
                            "attribute_type_id": "biolink:Publication",
                            "attributes": [],
                            "original_attribute_name": "reference",
                            "value": "PMID:26806034",
                            "value_type_id": "string"
                        },
                        {
                            "attribute_source": "infores:hmdb",
                            "attribute_type_id": "biolink:Publication",
                            "attributes": [],
                            "original_attribute_name": "reference",
                            "value": "PMID:26848182",
                            "value_type_id": "string"
                        },
                        {
                            "attribute_source": "infores:hmdb",
                            "attribute_type_id": "biolink:Publication",
                            "attributes": [],
                            "original_attribute_name": "reference",
                            "value": "PMID:27609529",
                            "value_type_id": "string"
                        },
                        {
                            "attribute_source": "infores:hmdb",
                            "attribute_type_id": "biolink:Publication",
                            "attributes": [],
                            "original_attribute_name": "reference",
                            "value": "PMID:28842642",
                            "value_type_id": "string"
                        },
                        {
                            "attribute_source": "infores:hmdb",
                            "attribute_type_id": "biolink:primary_knowledge_source",
                            "attributes": [],
                            "description": "MolePro's HMDB disorders transformer",
                            "original_attribute_name": "biolink:primary_knowledge_source",
                            "value": "infores:hmdb",
                            "value_type_id": "biolink:InformationResource"
                        },
                        {
                            "attribute_source": "infores:hmdb",
                            "attribute_type_id": "biolink:aggregator_knowledge_source",
                            "attributes": [],
                            "description": "Molecular Data Provider",
                            "original_attribute_name": "biolink:aggregator_knowledge_source",
                            "value": "infores:molepro",
                            "value_type_id": "biolink:InformationResource"
                        },
                        {
                            "attribute_source": "infores:molepro",
                            "attribute_type_id": "biolink:aggregator_knowledge_source",
                            "description": "Molecular Data Provider",
                            "original_attribute_name": "biolink:aggregator_knowledge_source",
                            "value": "infores:molepro",
                            "value_type_id": "biolink:InformationResource"
                        },
                        {
                            "attribute_type_id": "biolink:aggregator_knowledge_source",
                            "value": "infores:explanatory-agent",
                            "value_type_id": "biolink:InformationResource",
                            "value_url": "https://explanatory-agent.azurewebsites.net/v1.2",
                            "description": "The eXplanatory Autonomous Relay Agent (xARA) utilizes a case-based reasoning approach to execute ARS queries by obtaining results from multiple knowledge providers (KPs) and utilizes various methods such as natural language understanding models that traverse biomedical literature to score and explain its scores.",
                            "attribute_source": "infores:explanatory-agent"
                        }
                    ]
                }
            }
        }
        results = finder.search(["biolink:SmallMolecule"], ["biolink:Disease"], ["biolink:treated_by"], knowledge_graph, "Automat HMDB")
        expected = ExplanationX00012("test_kp")
        self.assertEqual(results.__class__, expected.__class__)
