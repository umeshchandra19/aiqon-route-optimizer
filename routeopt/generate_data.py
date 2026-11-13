"""Synthetic dataset generator.

How the data is constructed
---------------------------
1. Shipments: 40 shipments over 16 origin/destination pairs (4 Asian origins x
   4 destinations), four cargo types (standard / perishable / high_value /
   urgent) with different weights and values per tonne.
2. Route options: for each shipment ALL simple paths with <= 4 legs through the
   network are enumerated, then 3-5 *diverse* options are kept: cheapest,
   fastest, balanced, most reliable and lowest-risk (de-duplicated), topped up
   with random plausible alternatives.  So every shipment contains genuine
   cost / time / risk trade-offs by construction.
3. Lane parameters are shipment-specific draws around the network base values
   (spot-rate factor, seasonal delay variation, congestion noise).  These are
   the *estimates* the decision system sees.
4. A separate *ground truth* is drawn around the estimates (delay odds can be
   mis-estimated by ~35%, risk by +-0.08...).  It is used ONLY by the
   evaluation harness, to emulate forecast error in the real world.
5. Deadlines are set relative to each shipment's option set and cargo type
   (tight for urgent / perishable, loose for standard).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .model import LEG_COLUMNS, Route, route_to_rows
from .network import (DESTINATIONS, DWELL_DAYS, HANDLING_PER_T, NODES, ORIGINS,
                      enumerate_paths)
from .simulate import analytic_summary

CARGO_TYPES = ["standard", "perishable", "high_value", "urgent"]
CARGO_PROBS = [0.40, 0.20, 0.20, 0.20]
VALUE_PER_T = {  # USD per tonne (low, high)
    "standard": (4_000, 10_000),
    "perishable": (8_000, 20_000),
    "high_value": (40_000, 150_000),
    "urgent": (20_000, 60_000),
}


def _ln(rng, sigma):
    return rng.lognormal(-sigma ** 2 / 2, sigma)


def _lane_params(e, market, rng):
    est = dict(
        cost_pt=e.cost_per_t * market * _ln(rng, 0.05),
        days=e.days * _ln(rng, 0.04),
        p=float(np.clip(e.delay_p * _ln(rng, 0.20), 0.01, 0.60)),
        m=e.delay_mean * _ln(rng, 0.15),
        cong=float(np.clip(e.congestion + rng.normal(0, 0.07), 0, 1)),
        geo=float(np.clip(e.geo + rng.normal(0, 0.04), 0, 1)))
    tru = dict(
        cost_pt=est["cost_pt"] * _ln(rng, 0.03),
        days=est["days"] * _ln(rng, 0.03),
        p=float(np.clip(est["p"] * _ln(rng, 0.35), 0.005, 0.70)),
        m=est["m"] * _ln(rng, 0.25),
        cong=float(np.clip(est["cong"] + rng.normal(0, 0.10), 0, 1)),
        geo=float(np.clip(est["geo"] + rng.normal(0, 0.08), 0, 1)))
    return {"est": est, "true": tru}


def _build_route(path, weight, lanes, which, route_id, shipment_id) -> Route:
    L = len(path)
    nodes = [path[0][0]] + [t for _, t, _ in path]
    cost, days, p, m, cong, geo = [], [], [], [], [], []
    for i, (_, _, e) in enumerate(path):
        q = lanes[e.idx][which]
        last = i == L - 1
        c = q["cost_pt"] * weight
        d = q["days"]
        if not last:  # handling + dwell at the intermediate node we arrive at
            c += HANDLING_PER_T[e.mode] * weight
            d += DWELL_DAYS[e.mode] * (1 + q["cong"])
        cost.append(c); days.append(d); p.append(q["p"]); m.append(q["m"])
        cong.append(q["cong"]); geo.append(q["geo"])
    return Route(route_id=route_id, shipment_id=shipment_id, nodes=nodes,
                 modes=[e.mode for _, _, e in path], corridors=[e.corridor for _, _, e in path],
                 cost=np.array(cost), days=np.array(days), p=np.array(p), m=np.array(m),
                 cong=np.array(cong), geo=np.array(geo))


def _minmax(x):
    x = np.asarray(x, float)
    return (x - x.min()) / max(x.max() - x.min(), 1e-9)


def _select_options(cands, rng):
    """Pick 3-5 diverse routes from candidate Route objects."""
    S = [analytic_summary(r) for r in cands]
    cost = np.array([s["cost_usd"] for s in S])
    time = np.array([s["exp_days_analytic"] for s in S])
    dprob = np.array([s["delay_prob"] for s in S])
    risk = np.array([s["risk_index"] for s in S])
    surface = np.array([not r.has_air for r in cands])
    bal = _minmax(cost) + _minmax(time) + _minmax(dprob) + _minmax(risk)

    def argmin_masked(v, mask):
        v = np.where(mask, v, np.inf)
        return int(np.argmin(v))

    everything = np.ones(len(cands), bool)
    order = [argmin_masked(cost, everything), argmin_masked(time, everything),
             argmin_masked(bal, surface), argmin_masked(dprob + 1e-6 * cost, surface),
             argmin_masked(risk + 1e-6 * cost, surface)]
    n_target = int(rng.integers(3, 6))
    picks = []
    for i in order:
        if i not in picks:
            picks.append(i)
    # top up with random plausible surface alternatives (<= 2x cheapest surface cost)
    cheap_surface = cost[surface].min() if surface.any() else cost.min()
    pool = [i for i in range(len(cands)) if i not in picks and surface[i] and cost[i] <= 2.0 * cheap_surface]
    rng.shuffle(pool)
    while len(picks) < n_target and pool:
        picks.append(pool.pop())
    picks = picks[:n_target]
    # at most two air-containing routes
    air_seen, final = 0, []
    for i in picks:
        if cands[i].has_air:
            air_seen += 1
            if air_seen > 2:
                continue
        final.append(i)
    return final


def generate(n_shipments: int = 40, seed: int = 42, out_dir: str | Path = "data"):
    rng = np.random.default_rng(seed)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    combos = [(o, d) for o in ORIGINS for d in DESTINATIONS] * int(np.ceil(n_shipments / 16))
    rng.shuffle(combos)
    ships, legs_est, legs_true = [], [], []

    for i in range(n_shipments):
        sid = f"S{i + 1:03d}"
        origin, dest = combos[i]
        cargo = str(rng.choice(CARGO_TYPES, p=CARGO_PROBS))
        weight = round(float(rng.uniform(3, 35)), 1)
        lo, hi = VALUE_PER_T[cargo]
        value = round(weight * float(rng.uniform(lo, hi)), -2)
        market = float(rng.uniform(0.90, 1.25))  # freight-rate index at ship date

        lanes: dict = {}
        paths = enumerate_paths(origin, dest, max_legs=4)
        for path in paths:
            for _, _, e in path:
                if e.idx not in lanes:
                    lanes[e.idx] = _lane_params(e, market, rng)
        cands = [_build_route(p, weight, lanes, "est", "tmp", sid) for p in paths]
        idxs = _select_options(cands, rng)

        routes_est, routes_true = [], []
        for k, ci in enumerate(idxs, start=1):
            rid = f"{sid}-R{k}"
            routes_est.append(_build_route(paths[ci], weight, lanes, "est", rid, sid))
            routes_true.append(_build_route(paths[ci], weight, lanes, "true", rid, sid))

        t_exp = np.array([analytic_summary(r)["exp_days_analytic"] for r in routes_est])
        t_min = float(t_exp.min())
        surf = [t for t, r in zip(t_exp, routes_est) if not r.has_air]
        t_surf = float(min(surf)) if surf else t_min
        if cargo == "standard":
            deadline = t_surf * rng.uniform(1.25, 1.80)
        elif cargo == "perishable":
            deadline = t_surf * rng.uniform(1.05, 1.45)
        elif cargo == "high_value":
            deadline = t_surf * rng.uniform(1.20, 1.80)
        else:  # urgent
            deadline = max(t_min + 1.5, t_surf * rng.uniform(0.45, 1.05))
        deadline = float(max(round(deadline), 2))

        ships.append(dict(shipment_id=sid, origin=origin, destination=dest,
                          origin_name=NODES[origin], destination_name=NODES[dest],
                          cargo_type=cargo, weight_t=weight, value_usd=value,
                          deadline_days=deadline, market_rate_index=round(market, 3),
                          n_routes=len(routes_est)))
        for r in routes_est:
            legs_est += route_to_rows(r)
        for r in routes_true:
            legs_true += route_to_rows(r)

    pd.DataFrame(ships).to_csv(out_dir / "shipments.csv", index=False)
    pd.DataFrame(legs_est, columns=LEG_COLUMNS).to_csv(out_dir / "route_legs.csv", index=False)
    pd.DataFrame(legs_true, columns=LEG_COLUMNS).to_csv(out_dir / "route_legs_truth.csv", index=False)

    # human-friendly flat view of the route options (what a planner would see)
    from .model import load_dataset
    from .simulate import analytic_summary as asum
    sh, rts = load_dataset(out_dir)
    flat = []
    for sid, rs in rts.items():
        for r in rs:
            a = asum(r)
            flat.append(dict(shipment_id=sid, route_id=r.route_id, path=r.path_str(),
                             modes=r.modes_str(), n_legs=r.n_legs, family=r.family(),
                             cost_usd=round(a["cost_usd"]), transit_days_nominal=round(a["base_days"], 1),
                             transit_days_expected=round(a["exp_days_analytic"], 1),
                             delay_probability=round(a["delay_prob"], 3),
                             congestion=round(a["congestion"], 2), geopolitical_risk=round(a["geo"], 2)))
    pd.DataFrame(flat).to_csv(out_dir / "route_options.csv", index=False)
    return len(ships), len(flat)
