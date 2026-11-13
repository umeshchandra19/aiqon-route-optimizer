"""Evaluation harness.

Protocol
--------
The decision system only sees *estimated* lane parameters (``route_legs.csv``).
The evaluation scores each recommendation against a hidden *ground truth*
(``route_legs_truth.csv``: the same lanes with forecast error on delay odds,
delay length, congestion and risk) using the dollar-based business-cost model
in ``economics.py``.  For every shipment we compare:

  * Oracle           - best route in hindsight (lowest true expected cost)
  * Ours             - cargo-profile constraints + weighted score (this project)
  * EV-cost          - route with the lowest *estimated* expected business cost
                       (a strong "price everything in dollars" baseline)
  * Fixed weights    - same scorer, but one-size-fits-all weights and no hard rules
  * Cheapest / Fastest / Lowest-risk - single-metric heuristics
  * Random           - expected outcome of picking an option uniformly at random

Headline metric: relative regret = (true cost of pick - true cost of oracle) / oracle.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .economics import expected_outcome
from .model import apply_scenario, load_dataset
from .scoring import (PROFILES, Constraints, compute_metrics, decide, resolve_settings)

METHODS = ["Oracle (hindsight)", "Ours", "EV-cost baseline", "Fixed weights, no constraints",
           "Cheapest", "Fastest", "Lowest risk", "Random (expected)"]


def true_outcomes(ships, routes_true, scenario=None, n_sims=4000) -> dict:
    out = {}
    for sid, rs in routes_true.items():
        rows = {}
        for r in rs:
            o = expected_outcome(apply_scenario(r, scenario), ships.loc[sid], n=n_sims, salt=1)
            o["geo"] = float(apply_scenario(r, scenario).geo.max())
            rows[r.route_id] = o
        out[sid] = pd.DataFrame(rows).T
    return out


def estimate_tables(ships, routes_est, scenario=None, informed=True, n_sims=4000) -> dict:
    sc = scenario if informed else None
    tabs = {}
    for sid, rs in routes_est.items():
        t = compute_metrics(rs, ships.loc[sid], scenario=sc, n_sims=n_sims)
        t["est_biz"] = [expected_outcome(apply_scenario(r, sc), ships.loc[sid], n=n_sims)["biz_cost"]
                        for r in rs]
        tabs[sid] = t
    return tabs


def pick_methods(ships, tabs, truth, robustness_draws=200) -> tuple[dict, dict]:
    """Return ({method: {sid: route_id|None}}, {sid: Decision} for 'Ours')."""
    picks = {m: {} for m in METHODS}
    decisions = {}
    for sid, t in tabs.items():
        ship = ships.loc[sid]
        picks["Oracle (hindsight)"][sid] = truth[sid]["biz_cost"].astype(float).idxmin()
        picks["Cheapest"][sid] = t["cost_usd"].idxmin()
        picks["Fastest"][sid] = t["exp_days"].idxmin()
        picks["Lowest risk"][sid] = (t["risk_index"] + 1e-9 * t["cost_usd"]).idxmin()
        picks["EV-cost baseline"][sid] = t["est_biz"].idxmin()
        picks["Random (expected)"][sid] = None
        _, w, cons = resolve_settings(ship)
        d = decide(t, w, cons, float(ship["value_usd"]), float(ship["deadline_days"]), shipment_id=sid,
                   robustness_draws=robustness_draws, profile=ship["cargo_type"])
        decisions[sid] = d
        picks["Ours"][sid] = d.chosen
        fw = decide(t, PROFILES["standard"].weights, Constraints(), float(ship["value_usd"]),
                    float(ship["deadline_days"]), shipment_id=sid, robustness_draws=0)
        picks["Fixed weights, no constraints"][sid] = fw.chosen
    return picks, decisions


def outcome_frame(ships, tabs, truth, picks) -> pd.DataFrame:
    """Per (method, shipment) true outcomes of the picks."""
    rows = []
    for m in METHODS:
        for sid, rid in picks[m].items():
            tr = truth[sid]
            if rid is None:  # random: average over all options
                r = tr.astype(float).mean()
                fam = "mixed"
            else:
                r = tr.loc[rid].astype(float)
                fam = tabs[sid].loc[rid, "family"]
            rows.append(dict(method=m, shipment_id=sid, route_id=rid, family=fam,
                             true_cost=r["biz_cost"], freight=r["freight"], p_ontime=r["p_ontime"],
                             exp_days=r["exp_days"], geo=r["geo"], incident_prob=r["incident_prob"],
                             value=float(ships.loc[sid, "value_usd"]),
                             oracle_cost=truth[sid]["biz_cost"].astype(float).min(),
                             oracle_route=picks["Oracle (hindsight)"][sid]))
    df = pd.DataFrame(rows)
    df["regret"] = df["true_cost"] - df["oracle_cost"]
    df["rel_regret"] = df["regret"] / df["oracle_cost"]
    df["regret_pct_value"] = 100 * df["regret"] / df["value"]
    df["match"] = (df["route_id"] == df["oracle_route"]).astype(float)
    return df


def summarise(of: pd.DataFrame, n_boot=2000, seed=0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for m in METHODS:
        d = of[of.method == m].reset_index(drop=True)
        rr = d["rel_regret"].to_numpy()
        boots = [rr[rng.integers(0, len(rr), len(rr))].mean() for _ in range(n_boot)]
        rows.append({
            "method": m,
            "mean_regret_pct_of_cargo_value": d["regret_pct_value"].mean(),
            "mean_rel_regret_pct": 100 * rr.mean(),
            "regret_ci_lo": 100 * np.percentile(boots, 2.5),
            "regret_ci_hi": 100 * np.percentile(boots, 97.5),
            "median_rel_regret_pct": 100 * np.median(rr),
            "total_true_cost_usd": d["true_cost"].sum(),
            "oracle_match_pct": 100 * d["match"].mean() if m != "Random (expected)" else np.nan,
            "mean_p_ontime_pct": 100 * d["p_ontime"].mean(),
            "mean_freight_usd": d["freight"].mean(),
            "mean_exp_days": d["exp_days"].mean(),
            "mean_geo_exposure": d["geo"].mean(),
        })
    return pd.DataFrame(rows)


def calibration(of: pd.DataFrame, decisions: dict) -> pd.DataFrame:
    d = of[of.method == "Ours"].copy()
    d["confidence"] = d["shipment_id"].map(lambda s: decisions[s].confidence)
    d["tier"] = d["confidence"].map(lambda c: "Only one feasible route" if "only" in c else c)
    g = d.groupby("tier").agg(n=("shipment_id", "count"), mean_rel_regret_pct=("rel_regret", lambda x: 100 * x.mean()),
                              mean_regret_pct_of_value=("regret_pct_value", "mean"),
                              oracle_match_pct=("match", lambda x: 100 * x.mean())).reset_index()
    order = {"High": 0, "Medium": 1, "Low": 2, "Only one feasible route": 3}
    return g.sort_values("tier", key=lambda s: s.map(order)).reset_index(drop=True)


def by_cargo(of: pd.DataFrame, ships) -> pd.DataFrame:
    d = of[of.method.isin(["Ours", "EV-cost baseline", "Cheapest", "Fastest"])].copy()
    d["cargo_type"] = d["shipment_id"].map(ships["cargo_type"])
    return (d.groupby(["cargo_type", "method"]).agg(n=("shipment_id", "count"),
            mean_rel_regret_pct=("rel_regret", lambda x: 100 * x.mean()),
            mean_regret_pct_of_value=("regret_pct_value", "mean"),
            mean_p_ontime_pct=("p_ontime", lambda x: 100 * x.mean()),
            mean_freight_usd=("freight", "mean")).reset_index())


def scenario_stress(ships, routes_est, routes_true, scenario="red_sea", n_sims=4000) -> pd.DataFrame:
    """Does the system react when risk inputs are updated for a disruption?"""
    truth = true_outcomes(ships, routes_true, scenario, n_sims)
    rows = []
    for informed in (True, False):
        tabs = estimate_tables(ships, routes_est, scenario, informed=informed, n_sims=n_sims)
        picks, _ = pick_methods(ships, tabs, truth, robustness_draws=0)
        of = outcome_frame(ships, tabs, truth, picks)
        for m in ["Ours", "EV-cost baseline", "Cheapest"]:
            if m == "Cheapest" and informed is False:
                continue
            d = of[of.method == m]
            label = m if m == "Cheapest" else f"{m} ({'risk inputs updated' if informed else 'stale inputs'})"
            rows.append(dict(method=label,
                             total_true_cost_usd=d["true_cost"].sum(),
                             mean_rel_regret_pct=100 * d["rel_regret"].mean(),
                             mean_regret_pct_of_value=d["regret_pct_value"].mean(),
                             mean_p_ontime_pct=100 * d["p_ontime"].mean(),
                             share_via_red_sea_pct=100 * (d["family"] == "Suez / Red Sea").mean(),
                             mean_geo_exposure=d["geo"].mean()))
        if informed:
            d = of[of.method == "Oracle (hindsight)"]
            rows.append(dict(method="Oracle (hindsight)", total_true_cost_usd=d["true_cost"].sum(),
                             mean_rel_regret_pct=0.0, mean_regret_pct_of_value=0.0, mean_p_ontime_pct=100 * d["p_ontime"].mean(),
                             share_via_red_sea_pct=100 * (d["family"] == "Suez / Red Sea").mean(),
                             mean_geo_exposure=d["geo"].mean()))
    return pd.DataFrame(rows)


def run_evaluation(data_dir, results_dir, n_sims=4000):
    results_dir = Path(results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    ships, routes_est = load_dataset(data_dir)
    _, routes_true = load_dataset(data_dir, truth=True)

    truth = true_outcomes(ships, routes_true, None, n_sims)
    tabs = estimate_tables(ships, routes_est, None, True, n_sims)
    picks, decisions = pick_methods(ships, tabs, truth)
    of = outcome_frame(ships, tabs, truth, picks)
    summary = summarise(of)
    calib = calibration(of, decisions)
    cargo = by_cargo(of, ships)
    stress = scenario_stress(ships, routes_est, routes_true, "red_sea", n_sims)
    stress_lax = scenario_stress(ships, routes_est, routes_true, "lax_congestion", n_sims)

    of.to_csv(results_dir / "eval_per_shipment.csv", index=False)
    summary.to_csv(results_dir / "eval_summary.csv", index=False)
    calib.to_csv(results_dir / "eval_confidence_calibration.csv", index=False)
    cargo.to_csv(results_dir / "eval_by_cargo.csv", index=False)
    stress.to_csv(results_dir / "eval_scenario_red_sea.csv", index=False)
    stress_lax.to_csv(results_dir / "eval_scenario_lax_congestion.csv", index=False)

    ours = of[of.method == "Ours"]
    meta = {
        "n_shipments": int(len(ships)),
        "n_route_options": int(sum(len(v) for v in routes_est.values())),
        "ours_family_counts": ours["family"].value_counts().to_dict(),
        "ours_confidence_counts": pd.Series([d.confidence for d in decisions.values()]).value_counts().to_dict(),
        "relaxed_decisions": int(sum(d.relaxed for d in decisions.values())),
        "mean_stability": float(np.mean([d.stability for d in decisions.values() if d.stability is not None])),
    }
    # Red Sea stress test: how many decisions go to air / are flagged for review
    from .scoring import recommend
    air = rev = 0
    for sid, rs in routes_est.items():
        d = recommend(ships.loc[sid], rs, scenario="red_sea", robustness_draws=0)
        air += bool(d.table.loc[d.chosen, "has_air"])
        rev += bool(d.needs_review)
    meta["red_sea_air_picks"] = air
    meta["red_sea_needs_review"] = rev
    (results_dir / "eval_meta.json").write_text(json.dumps(meta, indent=2))
    return dict(summary=summary, calibration=calib, by_cargo=cargo, stress=stress, stress_lax=stress_lax,
                meta=meta, per_shipment=of, decisions=decisions, tables=tabs)
