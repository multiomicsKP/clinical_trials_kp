import gzip
import os
import json
import sys

kgInfoUrl = "https://db.systemsbiology.net/gestalt/cgi-pub/KGinfo.pl?id="
treats = "biolink:treats"
studyPrefix = "CLINICALTRIALS:"

def open_jsonl(data_folder, which):
    # the dumper may or may not keep the files compressed
    path = os.path.join(data_folder, f"clinical_trials_kg_{which}_current.jsonl")
    if os.path.exists(path + ".gz"): return gzip.open(path + ".gz", 'rt')
    return open(path)

def load_nodes(data_folder):
    # only the fields the annotator needs, to keep this out of swap
    id_name_mapping = {}
    studies = {}
    with open_jsonl(data_folder, "nodes") as nodes_file:
        for nodeline in nodes_file:
            node = json.loads(nodeline)
            id = node["id"]
            if id.startswith(studyPrefix):
                studies[id] = {
                    "tested_intervention": node["clinical_trial_tested_intervention"],
                    "phase": node.get("clinical_trial_phase", "not_provided"),
                    "status": node["clinical_trial_overall_status"],
                    "start_date": node.get("clinical_trial_start_date", ""),
                    "study_size": node.get("clinical_trial_enrollment", -1),
                }
            else:
                id_name_mapping[id] = node["name"]
    return id_name_mapping, studies

def load_content(data_folder):
    id_name_mapping, studies = load_nodes(data_folder)

    with open_jsonl(data_folder, "edges") as edges_file:
        for edgeline in edges_file:
            line = json.loads(edgeline)
            subj = line['subject']
            pred = line['predicate']
            if pred == treats: continue
            obj = line['object']
            if subj and pred and subj.split(':')[0] and obj.split(':')[0]:
                source_record_url = kgInfoUrl + line['id']
                prefix = obj.split(':')[0].replace(".","_")
                disease = {
                    prefix.lower(): obj,
                    "name": id_name_mapping[obj],
                }

                # the per-trial details live on the study nodes
                trials = []
                for study_id in line['has_supporting_studies']:
                    study = studies[study_id]
                    trials.append(
                        {
                            "id": study_id[len(studyPrefix):],
                            "label": pred,
                            "tested_intervention": study["tested_intervention"],
                            "phase": study["phase"],
                            "status": study["status"],
                            "start_date": study["start_date"],
                            "study_size": study["study_size"],
                            "source_record_urls": [ source_record_url ],
                            "disease": disease
                        }
                    )

                # NaN when no intervention on this edge carries a boxed warning,
                # otherwise "N/M" with N >= 1
                boxed_warning = line['intervention_boxed_warning']
                yield subj, trials, isinstance(boxed_warning, str) and boxed_warning != ""

            else:
                print(f"Cannot find prefix for {line} !", file=sys.stderr)

def load_data(data_folder):
    output = {}
    final = []
    warning = {}
    for subj, trials, boxed_warning in load_content(data_folder):
        if subj in output:
            for trial in trials:
                output[subj].append(trial)
        else:
            output.update({subj: trials})
        # a boxed warning on any edge for this subject marks the subject
        warning[subj] = warning.get(subj, False) or boxed_warning
    for key in output:
        final.append({"_id": key, "clinical_trials": output[key], "boxed_warning": warning[key]})
    for entry in final:
        yield entry



def main():
    data_folder = sys.argv[1] if len(sys.argv) > 1 else 'test'
    for entry in load_data(data_folder):
        print(json.dumps(entry, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
