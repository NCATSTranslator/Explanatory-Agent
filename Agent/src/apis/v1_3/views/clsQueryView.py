"""
WHAT: A class which represents a view for all query related operations
WHY: Need an api view
ASSUMES: 'Agent' is short for 'Explanatory Autonomous Relay Agent'
FUTURE IMPROVEMENTS: N/A
WHO: SL 2021-05-11
"""

from flask_restx import Resource, Namespace, fields
from ..queries.clsQueryManager import clsQueryManager
from ..queries.modQuerySync import querySync, querySyncPreSteps
import json


namespace = Namespace("query", description="Query Endpoints")

sampleBodyOnePathCaseIdQ000019 = \
    {
        "message": {
            "query_graph": {
                "edges": {
                    "e00": {
                        "subject": "n00",
                        "predicates": [
                            "biolink:correlated_with"
                        ],
                        "object": "n01",
                        "constraints": [
                            {
                                "id": "CHP:PredicateProxy",
                                "name": "Predicate Proxy",
                                "operator": "==",
                                "value": [
                                    "EFO:0000714"
                                ],
                                "unit_id": None,
                                "unit_name": None
                            }
                        ]
                    }
                },
                "nodes": {
                    "n00": {
                        "names": [
                            "Aspirin"
                        ],
                        "constraints": [
                            {
                                "id": "CHP:PredicateProxy",
                                "name": "Predicate Proxy",
                                "operator": "==",
                                "value": [
                                    "EFO:0000714"
                                ],
                                "unit_id": None,
                                "unit_name": None
                            }
                        ]
                    },
                    "n01": {
                        "categories": [
                            "biolink:Gene"
                        ]
                    }
                }
            }
        },
        "log_level": "ERROR"
    }

sampleBodyTwoPathsCaseIdQ000094 = \
    {
        "message": {
            "query_graph": {
                "nodes": {
                    "n00": {
                        "ids": [
                            "PUBCHEM.COMPOUND:2244"
                        ],
                        "categories": [
                            "biolink:ChemicalSubstance"
                        ]
                    },
                    "n01": {
                        "categories": [
                            "biolink:Disease"
                        ]
                    }
                },
                "edges": {
                    "e00": {
                        "subject": "n00",
                        "object": "n01",
                        "predicates": [
                            "biolink:affected_by"
                        ]
                    }
                }
            }
        }
    }

sampleBodyThread0OnePathCaseIdQ000019Thread1TwoPathCaseIdQ000127 = \
    {
        "message": {
            "query_graph": {
                "edges": {
                    "e00": {
                        "subject": "n00",
                        "predicates": [
                            "biolink:correlated_with",
                            "biolink:affected_by"
                        ],
                        "object": "n01",
                        "constraints": [
                            {
                                "id": "CHP:PredicateProxy",
                                "name": "Predicate Proxy",
                                "operator": "==",
                                "value": [
                                    "EFO:0000714"
                                ],
                                "unit_id": None,
                                "unit_name": None
                            }
                        ]
                    }
                },
                "nodes": {
                    "n00": {
                        "names": [
                            "Aspirin"
                        ],
                        "constraints": [
                            {
                                "id": "CHP:PredicateProxy",
                                "name": "Predicate Proxy",
                                "operator": "==",
                                "value": [
                                    "EFO:0000714"
                                ],
                                "unit_id": None,
                                "unit_name": None
                            }
                        ]
                    },
                    "n01": {
                        "categories": [
                            "biolink:Gene"
                        ]
                    }
                }
            }
        },
        "log_level": "ERROR"
    }
sampleBodyVerySimple = \
    {
      "message": {
        "query_graph": {
          "edges": {
            "e00": {
              "subject": "n00",
              "predicates": ["biolink:condition_associated_with_gene"],
              "object": "n01"
            }
          },
          "nodes": {
            "n00": {
              "ids": ["DOID:1612"],
              "categories": ["biolink:Disease"]
            },
            "n01": {
              "categories": ["biolink:Gene"]
            }
          }
        }
      }
    }

sampleCOHD = {
  "message": {
    "query_graph": {
      "nodes": {
        "n00": {
          "ids": [
            "DOID:9053"
          ],
          "categories": [
            "biolink:Disease"
          ]
        },
        "n01": {
          "categories": [
            "biolink:Procedure"
          ]
        }
      },
      "edges": {
        "e00": {
          "predicates": [
            "biolink:correlated_with"
          ],
          "subject": "n00",
          "object": "n01"
        }
      }
    }
  }
}

use_case_1 = {
  "message": {
    "query_graph": {
      "nodes": {
        "n00": {
          "ids": [
            "HP:0002013"
          ],
          "categories": [
            "biolink:DiseaseOrPhenotypicFeature"
          ]
        },
        "n01": {
          "categories": [
            "biolink:ChemicalEntity"
          ]
        }
      },
      "edges": {
        "e00": {
          "predicates": [
            "biolink:related_to"
          ],
          "subject": "n00",
          "object": "n01"
        }
      }
    }
  }
}

use_case_2 = {
  "message": {
    "query_graph": {
      "nodes": {
        "n00": {
          "categories": [
            "biolink:SmallMolecule"
          ]
        },
        "n01": {
          "ids": [
            "NCBIGene:1956"
          ],
        }
      },
      "edges": {
        "e00": {
          "predicates": [
              "biolink:decreases_abundance_of",
              # "biolink:decreases_activity_of",
              # "biolink:decreases_expression_of",
              # "biolink:decreases_synthesis_of",
              # "biolink:increases_degradation_of",
              # "biolink:disrupts",
              # "biolink:entity_negatively_regulates_entity"
          ],
          "subject": "n00",
          "object": "n01"
        }
      }
    }
  }
}

x00002_sample = {
  "message": {
    "query_graph": {
      "nodes": {
        "n00": {
          "ids": [
            "NCBIGene:1956"
          ],
          "categories": [
            "biolink:Gene"
          ]
        },
        "n01": {
          "categories": [
            "biolink:ChemicalSubstance"
          ]
        }
      },
      "edges": {
        "e00": {
          "predicates": [
            "biolink:related_to"
          ],
          "subject": "n00",
          "object": "n01"
        }
      }
    }
  }
}

similarity_score_test = {
  "message": {
    "query_graph": {
      "edges": {
        "e00": {
          "predicates": [
            "biolink:related_to"
          ],
          "subject": "n00",
          "object": "n01"
        }
      },
      "nodes": {
        "n00": {
          "ids": [
            "NCBIGene:26160"
          ],
          "categories": [
            "biolink:Gene"
          ]
        },
        "n01": {
          "categories": [
            "biolink:SmallMolecule"
          ]
        }
      }
    }
  }
}

reverse_one_hop_test = {
  "message": {
    "query_graph": {
      "edges": {
        "e00": {
          "predicates": [
            "biolink:related_to"
          ],
          "subject": "n00",
          "object": "n01"
        }
      },
      "nodes": {
        "n00": {
          "categories": [
            "biolink:SmallMolecule"
          ]
        },
        "n01": {
          "ids": [
            "NCBIGene:26160"
          ],
          "categories": [
            "biolink:Gene"
          ]
        }
      }
    }
  }
}

two_hop = \
{
    "message": {
        "query_graph": {
            "edges": {
                "e01": {
                    "object": "n0",
                    "subject": "n1",
                    "predicates": [
                        "biolink:entity_regulates_entity"
                    ]
                },
                "e02": {
                    "object": "n1",
                    "subject": "n2",
                    "predicates": [
                        "biolink:related_to"
                    ]
                }
            },
            "nodes": {
                "n0": {
                    "ids": [
                        "NCBIGene:23221"
                    ],
                    "categories": [
                        "biolink:Gene"
                    ]
                },
                "n1": {
                    "categories": [
                        "biolink:Gene"
                    ]
                },
                "n2": {
                    "categories": [
                        "biolink:SmallMolecule"
                    ]
                }
            }
        }
    }
}

force_derived_query = {
  "message": {
    "query_graph": {
      "edges": {
        "e00": {
          "predicates": [
            "biolink:has_completed"
          ],
          "subject": "n00",
          "object": "n01"
        }
      },
      "nodes": {
        "n01": {
          "categories": [
            "biolink:Gene"
          ]
        },
        "n00": {
          "ids": [
            "NCBIGene:26160"
          ],
          "categories": [
            "biolink:Gene"
          ]
        }
      }
    }
  }
}

ace_sample_query = {
  "message": {
    "query_graph": {
      "edges": {
        "e01": {
          "object": "n0",
          "subject": "n1",
          "predicates": [
            "biolink:related_to"
          ]
        }
      },
      "nodes": {
        "n0": {
          "ids": [
            "NCBIGene:1636"
          ],
          "categories": [
            "biolink:Gene"
          ]
        },
        "n1": {
          "categories": [
            "biolink:SmallMolecule"
          ]
        }
      }
    }
  }
}

x00003_sample = {
  "message": {
    "query_graph": {
      "edges": {
        "e01": {
          "object": "n0",
          "subject": "n1",
          "predicates": [
            "biolink:correlated_with"
          ]
        }
      },
      "nodes": {
        "n0": {
          "ids": [
            "NCBIGene:7157"
          ],
          "categories": [
            "biolink:Gene"
          ]
        },
        "n1": {
          "categories": [
            "biolink:Gene"
          ]
        }
      }
    }
  }
}

derived_sample = {
  "message": {
    "query_graph": {
      "nodes": {
        "n00": {
          "categories": [
            "biolink:ChemicalEntity"
          ],
          "ids": [
            "UNII:63CZ7GJN5I"
          ]
        },
        "n01": {
          "categories": [
            "biolink:SmallMolecule"
          ]
        }
      },
      "edges": {
        "e00": {
          "subject": "n00",
          "object": "n01",
          "predicates": [
            "biolink:abundance_affected_by"
          ]
        }
      }
    }
  }
}

workflow_lookup_sample = {
    "workflow": [
        {
            "id": "fill",
            "parameters": {
                "allowlist": ["icees"]
            }
        },
        {
            "id": "bind",
            "parameters": {}
        },
        {
            "id": "complete_results",
            "parameters": {}
        }
    ],
    "message": {
        "query_graph": {
            "edges": {
                "e01": {
                    "object": "n0",
                    "subject": "n1",
                    "predicates": [
                        "biolink:correlated_with"
                    ]
                }
            },
            "nodes": {
                "n0": {
                    "ids": [
                        "NCBIGene:7157"
                    ],
                    "categories": [
                        "biolink:Gene"
                    ]
                },
                "n1": {
                    "categories": [
                        "biolink:Gene"
                    ]
                }
            }
        }
    }
}

# sampleBody = similarity_score_test
# sampleBody = use_case_1
# sampleBody = use_case_2
# sampleBody = sampleCOHD
# sampleBody = x00002_sample
# sampleBody = reverse_one_hop_test
sampleBody = workflow_lookup_sample

query_graph = namespace.model(
    name="query_graph",
    model=
    {
        'edges': fields.Raw(example=sampleBody["message"]["query_graph"]["edges"], type=json, required=True),
        'nodes': fields.Raw(example=sampleBody["message"]["query_graph"]["nodes"], type=json, required=True)
    }
)

message = namespace.model(
    name="message",
    model={
        "query_graph": fields.Nested(query_graph, required=True)
    }
)

body = namespace.model(
    name="body",
    model=
    {
        'message': fields.Nested(message, required=True)
    }
)


@namespace.route("/")
class clsQueryView(Resource):
    """
    See header
    """

    @namespace.doc(body=body)
    def post(self):
        """
        HTTP POST request
        * Initializes query model
        * Checks user request body is valid
        * Checks user request body is supported
        * Forwards request body to knowledge provider POST
        * Checks knowledge provider response body is valid
        * Generates results
        * Returns entire query view model back to client
        :return: Query view model
        """

        queryManager = clsQueryManager()
        preStepResults = querySyncPreSteps(queryManager=queryManager)
        if not isinstance(preStepResults, clsQueryManager):
            return preStepResults
        queryManager = preStepResults

        return querySync(queryManager=queryManager)
