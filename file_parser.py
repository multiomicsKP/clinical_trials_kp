import pandas as pd
import os
import json

attribute_source = "infores:biothings-multiomics-clinicaltrials"
aact = "infores:aact"
ctgov = "infores:clinicaltrials"
kgInfoUrl = "https://db.systemsbiology.net/gestalt/cgi-pub/KGinfo.pl?id="

def load_data(data_folder):
    edges_file_path = os.path.join(data_folder, "clinical_trials_kg_edges_v2.0.tsv")
    nodes_file_path = os.path.join(data_folder, "clinical_trials_kg_nodes_v2.0.tsv")

    nodes_data = pd.read_csv(nodes_file_path, sep='\t')
    id_name_mapping = {}
    id_type_mapping = {}
    for index,row in nodes_data.iterrows():
        id_name_mapping[row["id"]] = row["name"]
        id_type_mapping[row["id"]] = row["category"]

    edges_data = pd.read_csv(edges_file_path, sep='\t')
    for index,line in edges_data.iterrows():
        subj = line['subject']
        pred = line['predicate']
        obj  = line['object']
        if subj and pred and subj.split(':')[0] and obj.split(':')[0]:

            prefix = subj.split(':')[0].replace(".","_")
            subject = {
                "id": subj,
                prefix.lower(): subj,
                "name": id_name_mapping[subj],
                "type": id_type_mapping[subj]
            }

            prefix = obj.split(':')[0].replace(".","_")
            object_ = {
                "id": obj,
                prefix.lower(): obj,
                "name": id_name_mapping[obj],
                "type": id_type_mapping[obj]
            }

            # properties for predicate/association
            edge_attributes = []
            supporting_studies = []

            nctids = str(line['nctid']).split(',')
            phases = str(line['phase']).split(',')
            status = str(line['overall_status']).split(',')
            enroll = str(line['enrollment']).split(',')
            en_typ = str(line['enrollment_type']).split(',')
            max_phase = 0
            elevate_to_prediction = False

            for nctid,phase,stat,N,Nt in zip(nctids,phases,status,enroll,en_typ):
                #print(phase,stat,N,Nt)
                if float(phase) > max_phase: max_phase = float(phase)
                supporting_studies.append(
                    {
                        "id": nctid,
                        "tested_intervention": "yes" if pred == "biolink:in_clinical_trials_for" else "unsure",
                        "phase": phase,
                        "status": stat,
                        "study_size": int(N),
                    }
                )
            if pred == "biolink:in_clinical_trials_for" and max_phase >= 4:
                    elevate_to_prediction = True

            # knowledge level
            edge_attributes.append(
                {
                    "attribute_type_id": "biolink:knowledge_level",
                    "value": line['knowledge_level'],
                }
            )

            # agent type
            edge_attributes.append(
                {
                    "attribute_type_id": "biolink:agent_type",
                     "value": line['agent_type'],
                }
            )

            # sources
            edge_sources = [
                {
                    "resource_id": attribute_source,
                    "resource_role": "aggregator_knowledge_source",
                    "source_record_urls": [ kgInfoUrl + line['rowId'] ]
                },
                {
                    "resource_id": aact,
                    "resource_role": "aggregator_knowledge_source"
                },
                {
                    "resource_id": ctgov,
                    "resource_role": "primary_knowledge_source"
                }
            ]

            association = {
                "label": pred,
                "attributes": edge_attributes,
                "sources": edge_sources,
                "max_research_phase": str(max_phase),
                "elevate_to_prediction": elevate_to_prediction,
                "supporting_studies": supporting_studies,
            }

            # Yield subject, predicate, and object properties
            data = {
                "_id": line['rowId'],
                "subject": subject,
                "association": association,
                "object": object_
            }

            yield data

        else:
            print(f"Cannot find prefix for {line} !")



def main():
    testing = False #True
    done = 0
    gen = load_data('test')
    while not testing or done < 10:
        #entry = next(gen)
        #continue
        try: entry = next(gen)
        except:
            break
        else:
            print(json.dumps(entry, sort_keys=True, indent=2))
            done = done + 1
    #print(done)

if __name__ == '__main__':
    main()
