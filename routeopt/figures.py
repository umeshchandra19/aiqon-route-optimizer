"""Figures used in the report (matplotlib, Agg backend)."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.titlesize": 10, "axes.titleweight": "bold", "figure.dpi": 100})

COLORS = {
    "Oracle (hindsight)": "#222222", "Ours": "#1b7f4c", "EV-cost baseline": "#2f6db5",
    "Fixed weights, no constraints": "#8e6bbf", "Cheapest": "#d98a1c", "Fastest": "#c0392b",
    "Lowest risk": "#b8567a", "Random (expected)": "#888888",
}


def fig_method_comparison(summary, path):
    df = summary[summary.method != "Oracle (hindsight)"].copy()
    fig, ax = plt.subplots(1, 2, figsize=(10.2, 3.5), gridspec_kw={"width_ratios": [1.0, 1.15]})
    d = df.sort_values("mean_regret_pct_of_cargo_value", ascending=True)
    y = np.arange(len(d))
    vals = np.maximum(d["mean_regret_pct_of_cargo_value"].to_numpy(), 0.01)
    ax[0].barh(y, vals, color=[COLORS[m] for m in d.method])
    ax[0].set_yticks(y)
    ax[0].set_yticklabels(d.method)
    ax[0].invert_yaxis()
    ax[0].set_xscale("log")
    ax[0].set_xlim(0.01, 60)
    for yi, v in zip(y, d["mean_regret_pct_of_cargo_value"]):
        ax[0].text(max(v, 0.01) * 1.15, yi, f"{v:.2f}%", va="center", fontsize=8)
    ax[0].set_xlabel("Mean excess cost vs. hindsight-best route\n(% of cargo value, log scale)")
    ax[0].set_title("(a) Cost of the decision")

    for _, r in df.iterrows():
        ax[1].scatter(max(r.mean_regret_pct_of_cargo_value, 0.01), r.mean_p_ontime_pct, s=70,
                      color=COLORS[r.method], zorder=3)
        dx = 1.25
        ax[1].annotate(r.method.replace(", no constraints", ""), (max(r.mean_regret_pct_of_cargo_value, 0.01) * dx,
                                                                  r.mean_p_ontime_pct), fontsize=8, va="center")
    ax[1].set_xscale("log")
    ax[1].set_xlim(0.01, 90)
    ax[1].set_ylim(55, 103)
    ax[1].axhline(95, color="#bbbbbb", lw=0.8, ls="--")
    ax[1].set_xlabel("Mean excess cost (% of cargo value, log scale)")
    ax[1].set_ylabel("Mean true P(on-time) (%)")
    ax[1].set_title("(b) Cost vs. service level")
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def fig_sensitivity(weight_sweeps, delay_sens, path):
    fig, ax = plt.subplots(1, 2, figsize=(10.2, 3.2))
    cols = {"cost": "#d98a1c", "time": "#2f6db5", "reliability": "#1b7f4c", "risk": "#c0392b"}
    for crit, df in weight_sweeps.items():
        ax[0].plot(df["weight"], df["flip_rate_pct"], marker="o", ms=3.5, color=cols[crit], label=crit)
    ax[0].set_xlabel("Weight placed on the criterion (others rescaled)")
    ax[0].set_ylabel("Recommendations that change (%)")
    ax[0].set_title("(a) Sensitivity to criterion weights")
    ax[0].legend(frameon=False, ncol=2)
    ax[0].set_ylim(-2, 80)

    a = ax[1]
    a.plot(delay_sens["delay_prob_scale"], delay_sens["decision_change_pct"], marker="o", color="#222222",
           label="recommendations changed (%)")
    a.plot(delay_sens["delay_prob_scale"], delay_sens["air_share_pct"], marker="s", color="#2f6db5",
           label="shipments sent by air (%)")
    a.axvline(1.0, color="#bbbbbb", lw=0.8, ls="--")
    a.set_xlabel("All delay probabilities multiplied by")
    a.set_ylabel("%")
    a.set_title("(b) Sensitivity to delay-estimate error")
    a.legend(frameon=False, loc="center right")
    a.set_ylim(-2, 48)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def fig_example(decision, ship, path):
    df = decision.table
    fig, ax = plt.subplots(figsize=(5.4, 3.5))
    for rid, r in df.iterrows():
        feasible = bool(r["in_pool"])
        size = 60 + 900 * r["delay_prob"]
        face = plt.cm.RdYlGn_r(np.clip(r["risk_index"], 0, 1)) if feasible else "none"
        edge = "#1b7f4c" if rid == decision.chosen else ("#555555" if feasible else "#999999")
        ax.scatter(r["cost_usd"], r["exp_days"], s=size, facecolor=face, edgecolor=edge,
                   linewidth=2.5 if rid == decision.chosen else 1.0, alpha=0.9 if feasible else 0.8,
                   linestyle="-" if feasible else "--", zorder=3)
        tag = rid.split("-")[-1] + " " + r["family"].split(" /")[0]
        if rid == decision.chosen:
            tag += "  (chosen)"
        ax.annotate(tag, (r["cost_usd"], r["exp_days"]), xytext=(7, 7), textcoords="offset points", fontsize=7.5)
    ax.set_xscale("log")
    ax.axhline(float(ship["deadline_days"]), color="#c0392b", lw=1, ls=":")
    ax.text(ax.get_xlim()[0] * 1.05, float(ship["deadline_days"]) + 0.6, "deadline", color="#c0392b", fontsize=7.5)
    ax.set_xlabel("Freight cost (USD, log scale)")
    ax.set_ylabel("Expected transit (days)")
    ax.set_title(f"{ship['shipment_id']}: {ship['origin']}→{ship['destination']} ({ship['cargo_type']})")
    ax.text(0.99, 0.97, "bubble = delay probability, colour = risk (green low → red high),\n"
                        "dashed hollow = excluded by hard rules", transform=ax.transAxes, ha="right", va="top",
            fontsize=6.8, color="#444444")
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
