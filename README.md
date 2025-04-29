# Clinical Trials KP

**Description**: The Clinical Trials KP, created by the [Multiomics Provider](https://github.com/NCATSTranslator/Translator-All/wiki/Multiomics-Provider), provides information on Clinical Trials, ultimately derived from researcher submissions to clinicaltrials.gov, via the Aggregate Analysis of Clinical Trials (AACT) database). Information on select trials includes the NCT Identifier of the trial, interventions used, diseases/conditions relevant to the trial, adverse events, etc.

**Example**: The Multiomics Clinical Trials KG reports that warfarin was used as an intervention for end-stage renal failure in a (completed) phase 3 clinical trial with 170 participants (NCT Identifier NCT00157651), and in a (currently recruiting) phase 4 clinical trial anticipating recruitment of 718 participants (NCT03862859).

The graph currently uses biolink:in_clinical_trials_for, biolink:mentioned_in_trials_for, and biolink:treats as predicates. Node categories include biolink:SmallMolecule, biolink:ChemicalEntity, and biolink:MolecularMixture for the interventions, and biolink:Disease and biolink:PhenotypicFeature for the conditions.

**Modes of access**:
- SmartAPI: https://smart-api.info/registry?q=e51073371d7049b9643e1edbdd61bcbd

**Knowledge Sources Accessed**:
- clinicaltrials.gov, via AACT

**Additional Links**: https://github.com/NCATSTranslator/Translator-All/wiki/Clinical-Trials-KP
