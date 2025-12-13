import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import json
import os
from collections import Counter

sns.set(style="whitegrid", context="talk")



def compute_distribution(df):
    counts = Counter(df["response_type"])
    total = sum(counts.values())
    return {
        "additive": counts.get("additive", 0) / total,
        "subtractive": counts.get("subtractive", 0) / total,
        "mixed": counts.get("mixed", 0) / total,
        "nochange": counts.get("nochange", 0) / total,
    }



def load_human_data(folder="behavioral_responses"):
    rows = []
    for fname in os.listdir(folder):
        if not fname.endswith(".json"):
            continue

        participant_id = fname.replace(".json", "")
        with open(os.path.join(folder, fname), "r") as f:
            data = json.load(f)

        # each trial inside "responses"
        for r in data["responses"]:
            rows.append({
                "participant": participant_id,
                "trial_id": r["trial_id"],
                "initial_hypothesis": ";".join(r["initial_hypothesis"]),
                "response_hypothesis": ";".join(r["response_hypothesis"]),
                "response_type": r["response_type"],
                "condition": r.get("condition", "unknown"),
                "rt_ms": r.get("rt_ms", None)
            })

    return pd.DataFrame(rows)




def plot_distribution(dist, title):
    labels = list(dist.keys())
    values = [dist[k] for k in labels]

    plt.figure(figsize=(8, 5))
    plt.bar(labels, values, color=["#4C72B0", "#C44E52", "#55A868", "#8172B2"])
    plt.ylabel("Proportion")
    plt.title(title)
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.show()



def plot_sweep(results_dict, x_label, title):
    xs = list(results_dict.keys())
    additives = [results_dict[x]["additive"] for x in xs]
    subtractives = [results_dict[x]["subtractive"] for x in xs]
    mixed = [results_dict[x]["mixed"] for x in xs]
    nochange = [results_dict[x]["nochange"] for x in xs]

    plt.figure(figsize=(10, 6))
    plt.plot(xs, additives, '-o', label="Additive")
    plt.plot(xs, subtractives, '-o', label="Subtractive")
    plt.plot(xs, mixed, '-o', label="Mixed")
    plt.plot(xs, nochange, '-o', label="Nochange")

    plt.xlabel(x_label)
    plt.ylabel("Proportion")
    plt.title(title)
    plt.legend()
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.show()




def visualize_baseline(path="results/results_baseline.csv"):
    df = pd.read_csv(path)
    dist = compute_distribution(df)
    plot_distribution(dist, "Model: Baseline Response Distribution")
    return dist




def visualize_cognitive_load(path="results/results_cognitive_load.csv"):
    df = pd.read_csv(path)

    df["steps"] = df["condition"].str.extract(r"steps=(\d+)").astype(int)
    df["temp"]  = df["condition"].str.extract(r"temp=([0-9.]+)").astype(float)

    step_values = sorted(df["steps"].unique())
    temp_values = sorted(df["temp"].unique())

    dist_steps = {s: compute_distribution(df[df["steps"] == s]) for s in step_values}
    dist_temp  = {t: compute_distribution(df[df["temp"] == t])  for t in temp_values}

    plot_sweep(dist_steps, "MCMC Steps", "Model: Effect of Cognitive Load (Steps)")
    plot_sweep(dist_temp,  "Temperature", "Model: Effect of Cognitive Load (Temperature)")

    return dist_steps, dist_temp



def visualize_cueing(path="results/results_cueing.csv"):
    df = pd.read_csv(path)
    df["p_add"] = df["condition"].str.extract(r"p_add=([0-9.]+)").astype(float)

    padd_values = sorted(df["p_add"].unique())
    dist_cue = {p: compute_distribution(df[df["p_add"] == p]) for p in padd_values}

    plot_sweep(dist_cue, "Probability of Additive Proposal (p_add)", "Model: Effect of Cueing")
    return dist_cue

def plot_model_vs_human(model_dist, human_dist, title):
    labels = ["additive", "subtractive", "mixed", "nochange"]
    x = np.arange(len(labels))
    width = 0.35

    plt.figure(figsize=(10, 6))
    plt.bar(x - width/2, [model_dist[l] for l in labels], width, label="Model")
    plt.bar(x + width/2, [human_dist[l] for l in labels], width, label="Human")

    plt.xticks(x, labels)
    plt.ylim(0, 1)
    plt.title(title)
    plt.ylabel("Proportion")
    plt.legend()
    plt.tight_layout()
    plt.show()



def visualize_human_data(folder="behavioral_responses"):
    df = load_human_data(folder)
    print(f"Loaded {len(df)} human trials from {df['participant'].nunique()} participants.")

    overall_dist = compute_distribution(df)
    plot_distribution(overall_dist, "Human Overall Response Distribution")

    # By condition (normal, time_pressure, add_subtract_reminder)
    for cond in df["condition"].unique():
        subdf = df[df["condition"] == cond]
        dist = compute_distribution(subdf)
        plot_distribution(dist, f"Human Response Distribution: {cond}")

    return df




def compare_human_model_baseline(human_df, model_dist):
    # Human baseline is the "normal" condition
    base_df = human_df[human_df["condition"] == "normal"]
    human_dist = compute_distribution(base_df)
    plot_model_vs_human(model_dist, human_dist, "Model vs Human (Baseline / Normal)")


def visualize_human_conditions_together(human_df):
    """
    Produces a single grouped bar chart:
    x-axis = conditions
    bars = additive, subtractive, mixed, nochange proportions
    """

    conditions = sorted(human_df["condition"].unique())

    # compute distribution per condition
    dist_by_cond = {
        cond: compute_distribution(human_df[human_df["condition"] == cond])
        for cond in conditions
    }

    labels = ["additive", "subtractive", "mixed", "nochange"]
    x = np.arange(len(conditions))
    width = 0.2

    plt.figure(figsize=(12, 7))

    # One bar series per response type
    for i, rtype in enumerate(labels):
        values = [dist_by_cond[c][rtype] for c in conditions]
        plt.bar(x + i * width - width * 1.5,
                values,
                width,
                label=rtype.capitalize())

    plt.xticks(x, conditions, rotation=15)
    plt.ylabel("Proportion")
    plt.title("Human Response Type Distributions Across All Conditions")
    plt.ylim(0, 1)
    plt.legend(title="Response Type")
    plt.tight_layout()
    plt.show()

    return dist_by_cond


if __name__ == "__main__":
    print("Loading human data...")
    human_df = visualize_human_data()

    print("Visualizing Model Baseline...")
    model_base = visualize_baseline()

    print("Comparing Human vs Model Baseline...")
    compare_human_model_baseline(human_df, model_base)

    print("Visualizing Model Cognitive Load...")
    visualize_cognitive_load()

    print("Visualizing Model Cueing...")
    visualize_cueing()

    print("Plotting all human conditions together...")
    visualize_human_conditions_together(human_df)

    print("Done.")
