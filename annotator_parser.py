import pandas as pd
import os
import json

attribute_source = "infores:clinicaltrials"
aact = "infores:aact"
ctgov = "infores:clinicaltrials"
kgInfoUrl = "https://db.systemsbiology.net/gestalt/cgi-pub/KGinfo.pl?id="
treats = "biolink:treats"
phaseNames = {"0.0": "not_provided", "0.5": "pre_clinical_research_phase", "1.0": "clinical_trial_phase_1", "2.0": "clinical_trial_phase_2", "3.0": "clinical_trial_phase_3", "4.0": "clinical_trial_phase_4", "1.5": "clinical_trial_phase_1_to_2", "2.5": "clinical_trial_phase_2_to_3"}

def load_content(data_folder):
    edges_file_path = os.path.join(data_folder, "clinical_trials_kg_edges_v2.7.13.tsv")
    nodes_file_path = os.path.join(data_folder, "clinical_trials_kg_nodes_v2.7.13.tsv")

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
        if pred == treats: continue
        obj  = line['object']
        if subj and pred and subj.split(':')[0] and obj.split(':')[0]:
            source_record_url = kgInfoUrl + line['id']
            prefix = obj.split(':')[0].replace(".","_")
            disease = {
                prefix.lower(): obj,
                "name": id_name_mapping[obj],
            }
            
            # properties for predicate/association
            edge_attributes = [
                {
                    "attribute_type_id": "biolink:knowledge_level",
                    "value": line['knowledge_level'],
                },
                {
                    "attribute_type_id": "biolink:agent_type",
                     "value": line['agent_type'],
                }
            ]
            
            # sources
            edge_sources = [
                {
                    "resource_id": attribute_source,
                    "resource_role": "aggregator_knowledge_source",
                    "source_record_urls": [ source_record_url ]
                },
                {
                    "resource_id": ctgov,
                    "resource_role": "primary_knowledge_source"
                },
                {
                   "resource_id": aact,
                    "resource_role": "aggregator_knowledge_source"
                }
            ]
            
            nctids = str(line['nctid']).split('|')
            phases = str(line['phase']).split('|')
            status = str(line['overall_status']).split('|')
            enroll = str(line['enrollment']).split('|')
            en_typ = str(line['enrollment_type']).split('|')
            tested = str(line['tested']).split('|')
            trials = []

            for nctid,phase,stat,N,Nt,test in zip(nctids,phases,status,enroll,en_typ,tested):
                try: N = int(N)
                except: N = -1
                trials.append(
                    {
                        "id": nctid,
                        "label": pred,
                        "tested_intervention": test,
                        "phase": phaseNames[str(float(phase))],
                        "status": stat,
                        "study_size": N,
                        "source_record_urls": [ source_record_url ],
                        "disease": disease
                    }
                )
                
            
            yield subj, trials, line['intervention_boxed_warning']

        else:
            print(f"Cannot find prefix for {line} !")

def load_data(data_folder):
    output = {}
    final = []
    warning = {}
    edges = load_content(data_folder)
    while 1:
        try: subj, trials, boxed_warning = next(edges)
        except: break
        if subj in output:
            for trial in trials:
                output[subj].append(trial)
        else:
            output.update({subj: trials})
        warning[subj] = boxed_warning
    for key in output:
        final.append({"_id": key, "clinical_trials": output[key], "boxed_warning": warning[key] != "0"})
    for entry in final:
        yield entry



def main():
    gen = load_data('test')
    while 1:
        try: entry = next(gen)
        except: break
        print(json.dumps(entry, sort_keys=True, indent=2))

if __name__ == '__main__':
    main()
