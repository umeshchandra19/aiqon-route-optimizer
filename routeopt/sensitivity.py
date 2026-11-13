"""Sensitivity of decisions to weights and to uncertain inputs."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .scoring import CRITERIA, compute_metrics, decide, resolve_settings


def reweight(base: dict, criterion: str, w: float) -> dict:
    """Set ``criterion`` to weight ``w``; rescale the others proportionally to sum to 1-w."""
    others = {k: v for k, v in base.items() if k != criterion}
    tot = sum(others.values())
    out = {k: (1 - w) * v / tot for k, v in others.items()} if tot > 0 else {k: (1 - w) / 3 for k in others}
    out[criterion] = w
    return out


def weight_sweep_one(table, ship, criterion: str, steps: int = 21, **settings) -> pd.DataFrame:
    """Chosen route for one shipment as the weight on ``criterion`` goes 0 -> 1."""
    _, base_w, cons = resolve_settings(ship, **settings)
    rows = []
    for w in np.linspace(0, 1, steps):
        d = decide(table, reweight(base_w, criterion, w), cons, float(ship["value_usd"]),
                   float(ship["deadline_days"]), str(ship["shipment_id"]), robustness_draws=0)
        rows.append(dict(weight=round(float(w), 3), chosen=d.chosen,
                         family=d.table.loc[d.chosen, "family"]))
    return pd.DataFrame(rows)


def switch_points(sweep: pd.DataFrame) -> list:
    """Weights at which the recommendation changes."""
    out, prev = [], None
    for r in sweep.itertuples():
        if prev is not None and r.chosen != prev.chosen:
            out.append((prev.weight, r.weight, prev.chosen, r.chosen))
        prev = r
    return out


def dataset_weight_sweep(ships, tables: dict, criterion: str = "cost", steps: int = 11) -> pd.DataFrame:
    """For each weight on ``criterion``: how many decisions flip vs the profile default,
    and what the portfolio of picks looks like."""
    base_choice = {}
    for sid, t in tables.items():
        ship = ships.loc[sid]
        _, w, cons = resolve_settings(ship)
        base_choice[sid] = decide(t, w, cons, float(ship["value_usd"]), float(ship["deadline_days"]),
                                  sid, robustness_draws=0).chosen
    rows = []
    for wt in np.linspace(0, 1, steps):
        flips, cost, days, dprob, air = 0, [], [], [], 0
        for sid, t in tables.items():
            ship = ships.loc[sid]
            _, w, cons = resolve_settings(ship)
            d = decide(t, reweight(w, criterion, wt), cons, float(ship["value_usd"]),
                       float(ship["deadline_days"]), sid, robustness_draws=0)
            r = d.table.loc[d.chosen]
            flips += d.chosen != base_choice[sid]
            cost.append(r.cost_usd); days.append(r.exp_days); dprob.append(r.delay_prob); air += bool(r.has_air)
        n = len(tables)
        rows.append(dict(criterion=criterion, weight=round(float(wt), 2), flip_rate_pct=100 * flips / n,
                         mean_freight_usd=np.mean(cost), mean_exp_days=np.mean(days),
                         mean_delay_prob_pct=100 * np.mean(dprob), air_share_pct=100 * air / n))
    return pd.DataFrame(rows)


def delay_estimate_sensitivity(ships, routes: dict, scales=(0.5, 0.75, 1.0, 1.5, 2.0, 3.0),
                               n_sims: int = 2000) -> pd.DataFrame:
    """What if every delay probability is mis-estimated by a common factor?

    Reports how many recommendations change relative to the factor-1.0 decision
    and how the portfolio of picks shifts (more air = paying for certainty).
    """
    picks, stats = {}, {}
    for sc in scales:
        picks[sc], air, cost, ontime = {}, 0, [], []
        for sid, rs in routes.items():
            ship = ships.loc[sid]
            t = compute_metrics(rs, ship, n_sims=n_sims, delay_scale=sc)
            _, w, cons = resolve_settings(ship)
            d = decide(t, w, cons, float(ship["value_usd"]), float(ship["deadline_days"]), sid,
                       robustness_draws=0)
            r = d.table.loc[d.chosen]
            picks[sc][sid] = d.chosen
            air += bool(r.has_air); cost.append(r.cost_usd); ontime.append(r.p_ontime)
        stats[sc] = (100 * air / len(routes), float(np.mean(cost)), 100 * float(np.mean(ontime)))
    rows = []
    for sc in scales:
        change = 100 * np.mean([picks[sc][s] != picks[1.0][s] for s in routes])
        rows.append(dict(delay_prob_scale=sc, decision_change_pct=change, air_share_pct=stats[sc][0],
                         mean_freight_usd=stats[sc][1], mean_p_ontime_pct=stats[sc][2]))
    return pd.DataFrame(rows)
