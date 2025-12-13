"""
Generate Figures:
1. Human vs Best-Fitting Model Distribution
2. Parameter Fit Heatmaps (p_add x temp, p_add x steps, steps x temp)

Assumes:
- best_model_params.json exists
- model_fit_grid.csv contains grid search results
- behavioral_responses/* contains human files
"""

import json
import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from collections import Counter
from run_model import run_experiment_parametric, load_stimuli

sns.set(style="whitegrid", context="talk")


def load_human_data(folder="behavioral_responses"):
    rows = []
    for fname in os.listdir(folder):
        if fname.endswith(".json"):
            pid = fname.replace(".json", "")
            with open(os.path.join(folder, fname), "r") as f:
                data = json.load(f)
            for r in data["responses"]:
                rows.append({
                    "participant": pid,
                    "condition": r.get("condition", "unknown"),
                    "response_type": r["response_type"]
                })
    return pd.DataFrame(rows)


def compute_distribution(df):
    c = Counter(df["response_type"])
    total = sum(c.values())
    return {
        "additive":     c.get("additive", 0) / total,
        "subtractive":  c.get("subtractive", 0) / total,
        "mixed":        c.get("mixed", 0) / total,
        "nochange":     c.get("nochange", 0) / total,
    }


def dist_to_vec(d):
    return [d["additive"], d["subtractive"], d["mixed"], d["nochange"]]



def plot_human_vs_model(human_dist, model_dist):
    labels = ["additive", "subtractive", "mixed", "nochange"]
    x = np.arange(len(labels))
    width = 0.35

    plt.figure(figsize=(10, 6))
    plt.bar(x - width/2, [human_dist[l] for l in labels],
            width, label="Human", color="#4C72B0")
    plt.bar(x + width/2, [model_dist[l] for l in labels],
            width, label="Model", color="#C44E52")

    plt.xticks(x, labels)
    plt.ylim(0, 1)
    plt.ylabel("Proportion")
    plt.title("Human vs Best-Fitting Model")
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_heatmaps(grid_df):
    """
    Expects columns:
        p_add, steps, temperature, loss
    """

    # ---- Heatmap 1: p_add × temp ----
    pivot = grid_df.pivot_table(index="p_add", columns="temperature", values="loss")
    plt.figure(figsize=(10, 6))
    sns.heatmap(pivot, annot=True, cmap="viridis_r")
    plt.title("Fit Landscape: p_add × temperature (loss)")
    plt.ylabel("p_add")
    plt.xlabel("temperature")
    plt.tight_layout()
    plt.show()

    # ---- Heatmap 2: p_add × steps ----
    pivot = grid_df.pivot_table(index="p_add", columns="steps", values="loss")
    plt.figure(figsize=(10, 6))
    sns.heatmap(pivot, annot=True, cmap="viridis_r")
    plt.title("Fit Landscape: p_add × steps (loss)")
    plt.ylabel("p_add")
    plt.xlabel("steps")
    plt.tight_layout()
    plt.show()

    # ---- Heatmap 3: steps × temperature ----
    pivot = grid_df.pivot_table(index="steps", columns="temperature", values="loss")
    plt.figure(figsize=(10, 6))
    sns.heatmap(pivot, annot=True, cmap="viridis_r")
    plt.title("Fit Landscape: steps × temperature (loss)")
    plt.ylabel("steps")
    plt.xlabel("temperature")
    plt.tight_layout()
    plt.show()



def main():

    # Load human data
    human_df = load_human_data()
    human_baseline = human_df[human_df["condition"] == "normal"]
    human_dist = compute_distribution(human_baseline)

    with open("results/best_model_params.json", "r") as f:
        best_params = json.load(f)

    p_add = best_params["p_add"]
    steps = best_params["steps"]
    temperature = best_params["temperature"]

    # Load stimuli to run model
    objects, obj_by_id, trials = load_stimuli("../src/stimuli.json")

    print("Running model with best-fit parameters:", best_params)

    # Run the model with best-fit parameters
    model_results = run_experiment_parametric(
        trials=trials,
        obj_by_id=obj_by_id,
        p_add=p_add,
        steps=steps,
        temperature=temperature,
        num_chains=50
    )

    model_df = pd.DataFrame(model_results)
    model_dist = compute_distribution(model_df)

    print("Generating Figure 1...")
    plot_human_vs_model(human_dist, model_dist)

    # Load grid search results
    print("Generating Figure 2...")
    grid_df = pd.read_csv("results/model_fit_grid.csv")
    plot_heatmaps(grid_df)

    print("All figures generated.")


if __name__ == "__main__":
    main()
