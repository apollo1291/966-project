"""
Fit the computational concept-editing model to human data.

This script performs:
- Human data loading
- Model simulation with adjustable parameters
- Distribution comparison
- Parameter search (grid or randomized)
- Saves grid results to CSV for visualization
"""

import json
import os
import numpy as np
import pandas as pd
from collections import Counter
from itertools import product

from run_model import (
    load_stimuli,
    run_experiment_parametric
)

def load_human_data(folder="behavioral_responses"):
    rows = []
    for fname in os.listdir(folder):
        if not fname.endswith(".json"):
            continue
        pid = fname.replace(".json", "")
        with open(os.path.join(folder, fname), "r") as f:
            data = json.load(f)

        for r in data["responses"]:
            rows.append({
                "participant": pid,
                "trial_id": r["trial_id"],
                "response_type": r["response_type"],
                "condition": r.get("condition", "unknown")
            })

    return pd.DataFrame(rows)


def compute_distribution(df):
    counts = Counter(df["response_type"])
    total = sum(counts.values())
    return {
        "additive": counts.get("additive", 0) / total,
        "subtractive": counts.get("subtractive", 0) / total,
        "mixed": counts.get("mixed", 0) / total,
        "nochange": counts.get("nochange", 0) / total,
    }

def dist_to_vec(d):
    return np.array([d["additive"], d["subtractive"], d["mixed"], d["nochange"]])


def kl_divergence(p, q):
    eps = 1e-9
    p = np.array(p) + eps
    q = np.array(q) + eps
    return np.sum(p * np.log(p / q))

def l2_distance(p, q):
    return np.sum((np.array(p) - np.array(q))**2)

def cross_entropy(p, q):
    eps = 1e-9
    p = np.array(p) + eps
    q = np.array(q) + eps
    return -np.sum(p * np.log(q))


def evaluate_model(params, trials, obj_by_id, human_dist):
    """
    params: dict with p_add, steps, temperature
    human_dist: distribution dict

    Returns: scalar loss
    """
    p_add = params["p_add"]
    steps = params["steps"]
    temp  = params["temperature"]

    # run model
    model_results = run_experiment_parametric(
        trials=trials,
        obj_by_id=obj_by_id,
        p_add=p_add,
        steps=steps,
        temperature=temp,
        num_chains=50
    )

    df = pd.DataFrame(model_results)
    model_dist = compute_distribution(df)

    # Compute chosen metric
    p = dist_to_vec(human_dist)
    q = dist_to_vec(model_dist)

    return kl_divergence(p, q)


def grid_search_fit(human_df, trials, obj_by_id):
    """
    Simple grid search across p_add, steps, temperature.
    Saves all results into model_fit_grid.csv.
    """

    human_dist = compute_distribution(human_df[human_df["condition"] == "normal"])

    p_add_vals = [0.1, 0.3, 0.5, 0.7, 0.9]
    steps_vals = [100, 200, 500, 800]
    temp_vals  = [0.5, 1.0, 1.5, 2.0]

    results = []

    print("Beginning grid search...")

    for p_add, steps, temp in product(p_add_vals, steps_vals, temp_vals):
        params = {"p_add": p_add, "steps": steps, "temperature": temp}
        loss = evaluate_model(params, trials, obj_by_id, human_dist)

        results.append({
            "p_add": p_add,
            "steps": steps,
            "temperature": temp,
            "loss": loss
        })

        print(f"Tested {params}, Loss={loss:.4f}")

    # Convert to DataFrame and save to CSV
    results_df = pd.DataFrame(results)
    results_df.to_csv("results/model_fit_grid.csv", index=False)

    # Identify best-fit parameters
    best_row = results_df.loc[results_df["loss"].idxmin()]
    best_params = {
        "p_add": float(best_row["p_add"]),
        "steps": int(best_row["steps"]),
        "temperature": float(best_row["temperature"]),
    }
    best_loss = float(best_row["loss"])

    print("\nBest parameters:", best_params)
    print("Best loss:", best_loss)

    return best_params, results_df

def main():
    print("Loading human data...")
    human_df = load_human_data()

    print("Loading stimuli...")
    objects, obj_by_id, trials = load_stimuli("../src/stimuli.json")

    print("Running parameter fitting...")
    best_params, results_df = grid_search_fit(
        human_df=human_df,
        trials=trials,
        obj_by_id=obj_by_id
    )

    # Save the best params
    with open("results/best_model_params.json", "w") as f:
        json.dump(best_params, f, indent=2)

    print("Done.")
    print("Saved: best_model_params.json and model_fit_grid.csv")


if __name__ == "__main__":
    main()
