# Advanced Explanation System (AES)
*Compound Screening: Protein interacts with Chemical workflow*

## 1. Background
The AES is one means by which the Explanatory Agent provides the ability to evaluate, order, and organize Translator Knowledge Provider (KP) assertions i.e., subject-predicate-object triples returned by one or more KPs. Specifically, AES involves an independent querying system, congruent to Translator KP queries, which provides corroborating assertions for comparison. Furthermore, AES provides vectorized encodings of biochemical and biomedical entity properties (e.g., proteins, chemicals, and phenotypes), are used to score Translator results by virtue of their similarity to AES-derived results. This strategy evaluates the extent to which translator responses are consistent with independently obtained answers to a query, and to which the properties of those answers align with known associations.

# 2. AES query workflow description
When the Explanatory Agent receives a query related to the identification of chemicals which interact with a protein, it triggers a process housed at Tufts Analytics Platform (TAP) which performs the following steps*:
1)	For the input query protein, it performs a query against the [Target Central Resource Database (TCRD)](http://juniper.health.unm.edu/tcrd/) to identify known active ligands with activity values (IC50 and EC50). 
2)	For each set of agonists (those with EC50 activity values) and antagonists (those with IC50 values) a three-dimensional representation of the compound is constructed from the SMILES string obtained from TCRD and a pharmacophore representing the common, prevalent chemical features shared by most of the active compounds is constructed. 
3)	For each agonist and antagonist pharmacophore, a pharmacophore search is performed against the Chembl database to obtain a set of chemicals with three-dimensional structures matching the pharmacophore. These results serve as the AES-derived chemical answers to the query.
4)	Additionally, for each result, in-silico docking is attempted against the known or predicted input protein target structure and a binding affinity value is estimated.

*Due to runtime limitations, only the first step is currently in place on the live Explanatory Agent ITRB instance. All known active ligands are passed on to AES feature engineering described in the following section.

## 3. AES feature engineering process
For each set of chemicals returned from AES and from Translator, an engineered feature matrix is computed where each row is a single chemical and the columns are a set of 5217 chemical features computed across six fingerprinting libraries: [maccskeys](https://resources.wolframcloud.com/FunctionRepository/resources/MACCSKeys/) , [circular](https://pubmed.ncbi.nlm.nih.gov/16523386/) , [mol2vec](https://mol2vec.readthedocs.io/en/latest/) , [Mordred](https://jcheminf.biomedcentral.com/articles/10.1186/s13321-018-0258-y) , [rdkit](http://rdkit.org/docs/source/rdkit.Chem.Fingerprints.html) , and [pubchem](https://ftp.ncbi.nlm.nih.gov/pubchem/specifications/pubchem_fingerprints.txt) . 
## 4. Answer scoring
Each resultant Translator chemical feature vector is compared against the AES matrix using cosine similarity to produce a list of cosine scores which are then averaged to produce an encoded similarity score indicating chemical similarity to AES-derived answers. 
