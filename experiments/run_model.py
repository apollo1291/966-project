import math
import random
import json
import csv
from dataclasses import dataclass
from typing import List, Dict, Any


RANDOM_SEED = 0
random.seed(RANDOM_SEED)

@dataclass
class Obj:
    id: int
    shape: str
    color: str
    fill: str
    size: str


@dataclass
class Example:
    object_id: int
    label: int


@dataclass
class Trial:
    id: str
    type: str
    hypothesis: List[str]
    examples: List[Example]


def load_stimuli(filename: str):
    with open(filename, "r") as f:
        data = json.load(f)

    objects = [Obj(**obj) for obj in data["objects"]]

    trials = []
    for t in data["trials"]:
        examples = [Example(**e) for e in t["examples"]]
        trials.append(
            Trial(
                id=t["id"],
                type=t["type"],
                hypothesis=t["hypothesis"],
                examples=examples,
            )
        )

    objects_by_id = {o.id: o for o in objects}
    return objects, objects_by_id, trials



ALL_FEATURES = [
    "circle", "square",
    "red", "blue",
    "solid", "striped",
    "big", "small"
]

def feature_dim(feature: str) -> str:
    if feature in ("circle", "square"):
        return "shape"
    if feature in ("red", "blue"):
        return "color"
    if feature in ("solid", "striped"):
        return "fill"
    if feature in ("big", "small"):
        return "size"
    raise ValueError(f"Unknown feature: {feature}")

def feature_satisfied(feature: str, obj: Obj) -> bool:
    if feature == "circle":  return obj.shape == "circle"
    if feature == "square":  return obj.shape == "square"
    if feature == "red":     return obj.color == "red"
    if feature == "blue":    return obj.color == "blue"
    if feature == "solid":   return obj.fill == "solid"
    if feature == "striped": return obj.fill == "striped"
    if feature == "big":     return obj.size == "big"
    if feature == "small":   return obj.size == "small"
    raise ValueError(f"Unknown feature: {feature}")

def predicts(h: List[str], obj: Obj) -> bool:
    return all(feature_satisfied(f, obj) for f in h)


LAMBDA = 0.7
NOISE = 0.05

def log_prior(h: List[str]) -> float:
    return -LAMBDA * len(h)

def log_likelihood(h: List[str], examples: List[Example], obj_by_id):
    ll = 0.0
    for ex in examples:
        obj = obj_by_id[ex.object_id]
        pred = 1 if predicts(h, obj) else 0
        ll += math.log(1 - NOISE) if pred == ex.label else math.log(NOISE)
    return ll

def log_posterior(h: List[str], examples: List[Example], obj_by_id):
    return log_prior(h) + log_likelihood(h, examples, obj_by_id)


def used_dims(h):
    return {feature_dim(f) for f in h}

def available_add_features(h):
    dims = used_dims(h)
    return [
        f for f in ALL_FEATURES
        if f not in h and feature_dim(f) not in dims
    ]

def available_remove_features(h):
    return list(h)

def propose(h, p_add):
    adds = available_add_features(h)
    removes = available_remove_features(h)

    if not adds and not removes:
        return h.copy(), "none"

    if not adds:
        do_add = False
    elif not removes:
        do_add = True
    else:
        do_add = random.random() < p_add

    new_h = h.copy()

    if do_add:
        f = random.choice(adds)
        new_h.append(f)
        move = "additive"
    else:
        f = random.choice(removes)
        new_h.remove(f)
        move = "subtractive"

    return new_h, move


def run_chain(
    trial: Trial,
    condition_name: str,
    p_add: float,
    steps: int,
    temperature: float,
    chain_idx: int,
    obj_by_id,
):
    current_h = trial.hypothesis.copy()
    current_lp = log_posterior(current_h, trial.examples, obj_by_id)

    add_moves = 0
    sub_moves = 0

    for _ in range(steps):
        proposal, move_type = propose(current_h, p_add)
        if move_type == "none":
            continue

        prop_lp = log_posterior(proposal, trial.examples, obj_by_id)
        delta = prop_lp - current_lp
        accept = min(1.0, math.exp(delta / temperature))

        if random.random() < accept:
            current_h = proposal
            current_lp = prop_lp
            if move_type == "additive": add_moves += 1
            else: sub_moves += 1

    final_h = current_h

    removed = [f for f in trial.hypothesis if f not in final_h]
    added   = [f for f in final_h if f not in trial.hypothesis]

    if removed and not added:
        resp_type = "subtractive"
    elif added and not removed:
        resp_type = "additive"
    elif removed and added:
        resp_type = "mixed"
    else:
        resp_type = "nochange"

    correct = 0
    for ex in trial.examples:
        obj = obj_by_id[ex.object_id]
        pred = 1 if predicts(final_h, obj) else 0
        correct += int(pred == ex.label)

    accuracy = correct / len(trial.examples)

    return {
        "trial_id": trial.id,
        "trial_type": trial.type,
        "condition": condition_name,
        "chain_index": chain_idx,
        "initial_hypothesis": trial.hypothesis,
        "final_hypothesis": final_h,
        "final_length": len(final_h),
        "response_type": resp_type,
        "additive_moves": add_moves,
        "subtractive_moves": sub_moves,
        "accuracy": accuracy,
    }




def run_experiment_parametric(trials, obj_by_id, p_add, steps, temperature, num_chains):
    results = []
    for trial in trials:
        for chain_idx in range(num_chains):
            out = run_chain(
                trial=trial,
                condition_name=f"p_add={p_add}_steps={steps}_temp={temperature}",
                p_add=p_add,
                steps=steps,
                temperature=temperature,
                chain_idx=chain_idx,
                obj_by_id=obj_by_id,
            )
            results.append(out)
    return results


def save_json(results, filename):
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)

def save_csv(results, filename):
    if not results:
        print("Warning: No results to save for", filename)
        return
    fieldnames = list(results[0].keys())
    with open(filename, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in results:
            row2 = row.copy()
            row2["initial_hypothesis"] = ";".join(row["initial_hypothesis"])
            row2["final_hypothesis"]   = ";".join(row["final_hypothesis"])
            w.writerow(row2)



def main():
    OUTPUT_DIR = "results"
    print("Loading stimuli ...")
    objects, obj_by_id, trials = load_stimuli("../src/stimuli.json")


    print("\nRunning BASELINE experiment ...")
    baseline = run_experiment_parametric(
        trials, obj_by_id,
        p_add=0.5, steps=500, temperature=1.0,
        num_chains=50
    )
    save_json(baseline, f"{OUTPUT_DIR}/results_baseline.json")
    save_csv(baseline, f"{OUTPUT_DIR}/results_baseline.csv")



    print("\nRunning COGNITIVE LOAD experiment ...")

    steps_list = [50, 150, 300, 500, 800]
    temps_list = [1.0, 1.5, 2.0, 3.0]

    cog_results = []

    for steps in steps_list:
        out = run_experiment_parametric(
            trials, obj_by_id,
            p_add=0.5, steps=steps, temperature=1.0,
            num_chains=30
        )
        cog_results.extend(out)

    for temp in temps_list:
        out = run_experiment_parametric(
            trials, obj_by_id,
            p_add=0.5, steps=500, temperature=temp,
            num_chains=30
        )
        cog_results.extend(out)

    save_json(cog_results, f"{OUTPUT_DIR}/results_cognitive_load.json")
    save_csv(cog_results, f"{OUTPUT_DIR}/results_cognitive_load.csv")



    print("\nRunning CUEING experiment ...")

    p_add_values = [0.1, 0.3, 0.5, 0.7, 0.9]
    cue_results = []

    for p in p_add_values:
        out = run_experiment_parametric(
            trials, obj_by_id,
            p_add=p, steps=500, temperature=1.0,
            num_chains=30
        )
        cue_results.extend(out)

    save_json(cue_results, f"{OUTPUT_DIR}/results_cueing.json")
    save_csv(cue_results, f"{OUTPUT_DIR}/results_cueing.csv")

    print("\nAll experiments completed and saved.")


if __name__ == "__main__":
    main()
