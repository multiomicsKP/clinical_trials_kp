import pandas as pd
import os
import json

attribute_source = "infores:multiomics-clinicaltrials"
aact = "infores:aact"
ctgov = "infores:clinicaltrials"
kgInfoUrl = "https://db.systemsbiology.net/gestalt/cgi-pub/KGinfo.pl?id="
treats = "biolink:treats"
phaseNames = {"0.0": "not_provided", "0.5": "pre_clinical_research_phase", "1.0": "clinical_trial_phase_1", "2.0": "clinical_trial_phase_2", "3.0": "clinical_trial_phase_3", "4.0": "clinical_trial_phase_4", "1.5": "clinical_trial_phase_1_to_2", "2.5": "clinical_trial_phase_2_to_3"}

def load_data(data_folder):
    edges_file_path = os.path.join(data_folder, "clinical_trials_kg_edges_v3.1.14.tsv")
    nodes_file_path = os.path.join(data_folder, "clinical_trials_kg_nodes_v3.1.14.tsv")

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
            tested = str(line['tested']).split(',')
            max_phase = 0
            elevate_to_prediction = False

            for nctid,phase,stat,N,Nt,test in zip(nctids,phases,status,enroll,en_typ,tested):
                #print(phase,stat,N,Nt)
                if float(phase) > max_phase:
                    max_phase = float(phase)
                
                try: N = int(N)
                except: N = -1
                
                supporting_studies.append(
                    {
                        "id": nctid,
                        "tested_intervention": test,
                        "phase": phaseNames[str(float(phase))],
                        "status": stat,
                        "study_size": N,
                    }
                )
                
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
            
            # max research phase
            edge_attributes.append(
                {
                    "attribute_type_id": "biolink:max_research_phase",
                     "value": phaseNames[str(float(max_phase))],
                }
            )
            
            # elevate to prediction
            edge_attributes.append(
                {
                    "attribute_type_id": "elevate_to_prediction",
                     "value": str(line['elevate_to_prediction']),
                }
            )
            
            # approval status
            if pred == treats:
                edge_attributes.append(
                    {
                        "attribute_type_id": "clinical_approval_status",
                        "value": "biolink:approved_for_condition"
                    }
                )
            
            # boxed warning status
            if line['intervention_boxed_warning'] != '0':
                edge_attributes.append(
                    {
                        "attribute_type_id": "intervention_boxed_warning",
                        "value": line['intervention_boxed_warning']
                    }
                )
            
            # sources
            edge_sources = []
            if pred == treats:
                edge_sources = [
                    {
                        "resource_id": ctgov,
                        "resource_role": "supporting_data_source"
                    },
                    {
                        "resource_id": aact,
                        "resource_role": "supporting_data_source"
                    },
                    {
                        "resource_id": attribute_source,
                        "resource_role": "primary_knowledge_source",
                        "source_record_urls": [ kgInfoUrl + line['id'] ]
                    }
                ]
            else:
                edge_sources = [
                    {
                        "resource_id": attribute_source,
                        "resource_role": "primary_knowledge_source",
                        "source_record_urls": [ kgInfoUrl + line['id'] ]
                    },
                    {
                        "resource_id": ctgov,
                        "resource_role": "supporting_data_source"
                    },
                    {
                       "resource_id": aact,
                        "resource_role": "supporting_data_source"
                    }
                ]
            
            association = {
                "label": pred,
                "attributes": edge_attributes,
                "sources": edge_sources,
                "supporting_studies": supporting_studies,
            }

            # Yield subject, predicate, and object properties
            data = {
                "_id": line['id'],
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
        #print(json.dumps(entry, sort_keys=True, indent=2))
        #continue
        try: entry = next(gen)
        except StopIteration:
            break
        else:
            print(json.dumps(entry, sort_keys=True, indent=2))
            done = done + 1
    #print(done)

if __name__ == '__main__':
    main()
