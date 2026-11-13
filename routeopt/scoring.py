"""Decision framework.

Pipeline for one shipment
-------------------------
1. ``compute_metrics``  - turn each route's leg data into decision metrics
                          (cost, expected days, P90 buffer, delay prob,
                          P(on-time), risk index) via Monte Carlo.
2. Hard constraints     - mode exclusions, minimum P(on-time), maximum
                          geopolitical exposure.  Routes that violate them are
                          *not allowed to compete*, no matter how cheap.
3. Pareto screen        - flags routes dominated on all four criteria.
4. Weighted scoring     - cargo-profile weights over four criteria mapped to
                          [0,1] penalties on absolute scales: cost (share of
                          cargo value), time (deadline buffer), reliability
                          (delay probability), risk (congestion / geopolitics).
5. Robustness check     - re-run the decision under perturbed metrics and
                          weights to quantify how stable the pick is.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .model import Route, apply_scenario, scale_delay
from .simulate import analytic_summary, route_seed, simulate_transit

CRITERIA = ["cost", "time", "reliability", "risk"]
CRITERIA_LABEL = {
    "cost": "freight cost",
    "time": "deadline buffer",
    "reliability": "delay probability",
    "risk": "congestion / geopolitical risk",
}

# ---------------------------------------------------------------------------
# Criterion scales.  Each criterion is mapped to a penalty in [0, 1] using an
# ABSOLUTE, decision-relevant scale instead of min-max scaling inside the
# option set.  (Min-max was tried first: a single air option 20x more expensive
# than sea stretches the scale so far that every surface route looks "equally
# cheap", and air then wins on the remaining criteria.  Absolute scales do not
# depend on which outliers happen to be in the option set.)
#
#   cost        freight / cargo value; 0% -> 0, >= COST_ANCHOR (20%) -> 1
#   time        deadline utilisation = expected days / deadline.  Speed only
#               has value for protecting the deadline: arriving with a
#               >= 30% buffer is "free" (0); the penalty rises linearly to 1
#               at 100% utilisation (expected arrival == deadline).
#   reliability probability that at least one leg is delayed; >= 50% -> 1
#   risk        0.4 * congestion + 0.6 * max leg geopolitical risk (already 0..1)
# ---------------------------------------------------------------------------
COST_ANCHOR = 0.20
REVIEW_PREMIUM_SHARE = 0.25   # flag for human review if hard rules add > 25% of cargo value
TIME_COMFORT = 0.70
DELAY_ANCHOR = 0.50


@dataclass(frozen=True)
class Profile:
    weights: dict
    min_ontime: float   # hard constraint: P(arrive by deadline) >= this
    max_geo: float      # hard constraint: max leg geopolitical risk allowed
    rationale: str = ""


# Profile weights.  The *shape* (relative priority of time / reliability / risk)
# encodes the cargo's nature; the overall weight on cost was calibrated on a
# separate synthetic dataset (seed 7, 200 shipments) with
# scripts/calibrate_profiles.py -> results/calibration_profiles.json.
# The hard on-time / geopolitical thresholds are policy (service-level) choices.
PROFILES = {
    "standard": Profile(
        {"cost": 0.45, "time": 0.22, "reliability": 0.22, "risk": 0.11}, 0.70, 0.90,
        "Cost-driven; deadline is soft-ish, tolerate moderate risk."),
    "perishable": Profile(
        {"cost": 0.40, "time": 0.26, "reliability": 0.22, "risk": 0.12}, 0.85, 0.90,
        "Shelf-life makes deadline buffer and schedule reliability important."),
    "high_value": Profile(
        {"cost": 0.60, "time": 0.07, "reliability": 0.12, "risk": 0.21}, 0.80, 0.50,
        "Theft / seizure / diversion exposure dominates the non-cost criteria; hard cap on geopolitical risk."),
    "urgent": Profile(
        {"cost": 0.10, "time": 0.50, "reliability": 0.30, "risk": 0.10}, 0.90, 0.90,
        "Time-critical (spares, launches); pay to protect the deadline."),
}


@dataclass
class Constraints:
    min_ontime: float = 0.0
    max_geo: float = 1.0
    exclude_modes: tuple = ()


@dataclass
class Decision:
    shipment_id: str
    table: pd.DataFrame            # one row per route, with scores / flags
    chosen: str
    runner_up: str | None
    weights: dict
    constraints: Constraints
    relaxed: bool = False
    relax_note: str = ""
    stability: float | None = None  # share of perturbation draws won by `chosen`
    margin: float | None = None     # suitability-score gap to runner-up (0-100 pts)
    confidence: str = "n/a"
    profile: str = ""
    unconstrained_best: str | None = None   # winner if the hard rules were ignored
    constraint_premium: float = 0.0         # extra freight (USD) the hard rules cost
    needs_review: bool = False              # hard rules force a very expensive pick


# ---------------------------------------------------------------------------
# 1. Metrics
# ---------------------------------------------------------------------------
def compute_metrics(routes: list, ship, scenario: str | None = None, n_sims: int = 4000,
                    delay_scale: float = 1.0) -> pd.DataFrame:
    rows = []
    deadline = float(ship["deadline_days"])
    for r in routes:
        r2 = apply_scenario(r, scenario)
        if delay_scale != 1.0:
            r2 = scale_delay(r2, delay_scale)
        a = analytic_summary(r2)
        T = simulate_transit(r2, n_sims, np.random.default_rng(route_seed(r.route_id)))
        p90 = float(np.quantile(T, 0.90))
        rows.append(dict(
            route_id=r.route_id, path=r2.path_str(), modes=r2.modes_str(), n_legs=r2.n_legs,
            family=r2.family(), has_air=r2.has_air,
            cost_usd=a["cost_usd"], base_days=a["base_days"], exp_days=float(T.mean()),
            p90_days=p90, tail_days=max(p90 - a["base_days"], 0.0),
            delay_prob=a["delay_prob"], p_ontime=float((T <= deadline).mean()),
            congestion=a["congestion"], geo=a["geo"], risk_index=a["risk_index"]))
    return pd.DataFrame(rows).set_index("route_id", drop=False)


def criteria_matrix(df: pd.DataFrame) -> np.ndarray:
    """Raw criterion values (lower = better), used for the Pareto screen."""
    return np.column_stack([df["cost_usd"], df["exp_days"], df["delay_prob"], df["risk_index"]])


def penalty_matrix(cost, exp_days, delay_prob, risk, value, deadline) -> np.ndarray:
    """Map raw metrics to per-criterion penalties in [0,1]; shape (..., 4)."""
    cost_pen = np.clip(np.asarray(cost) / value / COST_ANCHOR, 0, 1)
    util = np.asarray(exp_days) / deadline
    time_pen = np.clip((util - TIME_COMFORT) / (1 - TIME_COMFORT), 0, 1)
    rel_pen = np.clip(np.asarray(delay_prob) / DELAY_ANCHOR, 0, 1)
    risk_pen = np.clip(np.asarray(risk), 0, 1)
    return np.stack([cost_pen, time_pen, rel_pen, risk_pen], axis=-1)


def table_penalties(df: pd.DataFrame, value: float, deadline: float) -> np.ndarray:
    return penalty_matrix(df["cost_usd"].to_numpy(), df["exp_days"].to_numpy(),
                          df["delay_prob"].to_numpy(), df["risk_index"].to_numpy(), value, deadline)


def normalise_weights(weights: dict) -> dict:
    w = {k: float(weights.get(k, 0.0)) for k in CRITERIA}
    if any(v < 0 for v in w.values()):
        raise ValueError("weights must be non-negative")
    s = sum(w.values())
    if s <= 0:
        raise ValueError("weights must sum to a positive number")
    return {k: v / s for k, v in w.items()}


def _dominated(X: np.ndarray) -> np.ndarray:
    K = X.shape[0]
    dom = np.zeros(K, bool)
    for i in range(K):
        for j in range(K):
            if i != j and np.all(X[j] <= X[i]) and np.any(X[j] < X[i]):
                dom[i] = True
                break
    return dom


# ---------------------------------------------------------------------------
# 2-5. Decision
# ---------------------------------------------------------------------------
def decide(table: pd.DataFrame, weights: dict, constraints: Constraints, value: float,
           deadline: float, shipment_id: str = "", robustness_draws: int = 300, seed: int = 0,
           profile: str = "") -> Decision:
    df = table.copy()
    w = normalise_weights(weights)
    wv = np.array([w[c] for c in CRITERIA])

    # --- hard constraints -------------------------------------------------
    excluded = set(constraints.exclude_modes)
    reasons = []
    mode_ok = np.zeros(len(df), bool)
    geo_ok = np.zeros(len(df), bool)
    ontime_ok = np.zeros(len(df), bool)
    for i, row in enumerate(df.itertuples()):
        rs = []
        bad_modes = sorted(excluded.intersection(row.modes.split(">")))
        if bad_modes:
            rs.append(f"uses excluded mode ({', '.join(bad_modes)})")
        else:
            mode_ok[i] = True
        if row.geo > constraints.max_geo + 1e-9:
            rs.append(f"geopolitical exposure {row.geo:.2f} exceeds cap {constraints.max_geo:.2f}")
        else:
            geo_ok[i] = True
        if row.p_ontime < constraints.min_ontime - 1e-9:
            shown = "<1%" if row.p_ontime < 0.005 else f"{row.p_ontime:.0%}"
            rs.append(f"only a {shown} chance of on-time arrival (need {constraints.min_ontime:.0%})")
        else:
            ontime_ok[i] = True
        reasons.append("; ".join(rs))
    df["violations"] = reasons
    feasible = mode_ok & geo_ok & ontime_ok
    df["feasible"] = feasible

    if not mode_ok.any():
        raise ValueError("No route remains after applying the mode exclusions.")

    relaxed, note = False, ""
    if feasible.any():
        pool = feasible
    else:
        relaxed = True
        hard = mode_ok & geo_ok
        if hard.any():
            best = df.loc[hard, "p_ontime"].max()
            pool = hard & (df["p_ontime"].to_numpy() >= best - 0.05)
            note = (f"No route meets the {constraints.min_ontime:.0%} on-time requirement. "
                    f"Best achievable is {'<1%' if best < 0.005 else f'{best:.0%}'}; recommending among the most punctual options. "
                    f"Consider relaxing the deadline or approving a faster mode.")
        else:
            lowest = df.loc[mode_ok, "geo"].min()
            pool = mode_ok & (df["geo"].to_numpy() <= lowest + 0.05)
            note = (f"No route satisfies the geopolitical-risk cap of {constraints.max_geo:.2f}. "
                    f"Recommending among the lowest-exposure options (min {lowest:.2f}); "
                    f"manual review advised.")
    df["in_pool"] = pool

    # --- Pareto screen (over all options, for information) --------------------
    X_all = criteria_matrix(df)
    df["dominated"] = _dominated(X_all)
    df["dominated_by"] = ""
    for i in np.where(df["dominated"].to_numpy())[0]:
        for j in range(len(df)):
            if j != i and np.all(X_all[j] <= X_all[i]) and np.any(X_all[j] < X_all[i]):
                df.iloc[i, df.columns.get_loc("dominated_by")] = df.index[j]
                break

    # --- weighted scoring within the pool ----------------------------------
    P_all = table_penalties(df, value, deadline)
    for k, c in enumerate(CRITERIA):
        df[f"pen_{c}"] = P_all[:, k]
    pen = np.full(len(df), np.nan)
    pen[pool] = P_all[pool] @ wv
    df["penalty"] = pen
    df["score"] = 100 * (1 - df["penalty"])
    df["rank"] = df["penalty"].rank(method="first")
    ids_pool = list(df.index[pool])
    order = df.loc[ids_pool].sort_values("penalty").index.tolist()
    chosen = order[0]
    runner_up = order[1] if len(order) > 1 else None
    margin = None
    if runner_up is not None:
        margin = float(df.loc[chosen, "score"] - df.loc[runner_up, "score"])

    # --- price of the hard rules ---------------------------------------------
    unc_ids = list(df.index[mode_ok])
    pen_unc = P_all[mode_ok] @ wv
    unc_best = unc_ids[int(np.argmin(pen_unc))]
    premium = float(df.loc[chosen, "cost_usd"] - df.loc[unc_best, "cost_usd"]) if unc_best != chosen else 0.0
    needs_review = bool(unc_best != chosen and premium > REVIEW_PREMIUM_SHARE * value)

    # --- robustness: perturb metrics (estimate error) and weights ---------------
    stability = None
    confidence = "n/a"
    if len(ids_pool) == 1:
        stability, confidence = 1.0, "High (only feasible option)"
    elif robustness_draws > 0:
        rng = np.random.default_rng(seed + zlib_hash(shipment_id))
        B, K = robustness_draws, len(ids_pool)
        sub = df.loc[ids_pool]
        cost_b = sub["cost_usd"].to_numpy()[None, :] * rng.lognormal(0, 0.10, (B, K))
        time_b = sub["exp_days"].to_numpy()[None, :] * rng.lognormal(0, 0.08, (B, K))
        dp_b = np.clip(sub["delay_prob"].to_numpy()[None, :] * rng.lognormal(0, 0.30, (B, K)), 0, 1)
        risk_b = np.clip(sub["risk_index"].to_numpy()[None, :] + rng.normal(0, 0.10, (B, K)), 0, 1)
        Pb = penalty_matrix(cost_b, time_b, dp_b, risk_b, value, deadline)   # (B,K,4)
        pos = wv > 0
        g = rng.gamma(np.where(pos, wv * 60, 1.0), size=(B, 4)) * pos
        wb = g / g.sum(axis=1, keepdims=True)
        scores_b = (Pb * wb[:, None, :]).sum(axis=-1)
        winners = scores_b.argmin(axis=1)
        stability = float((np.array(ids_pool)[winners] == chosen).mean())
        confidence = "High" if stability >= 0.80 else "Medium" if stability >= 0.55 else "Low"

    return Decision(shipment_id=shipment_id, table=df, chosen=chosen, runner_up=runner_up,
                    weights=w, constraints=constraints, relaxed=relaxed, relax_note=note,
                    stability=stability, margin=margin, confidence=confidence, profile=profile,
                    unconstrained_best=unc_best, constraint_premium=premium, needs_review=needs_review)


def zlib_hash(s: str) -> int:
    import zlib
    return zlib.crc32(s.encode()) % 100003


def resolve_settings(ship, profile: str | None = None, weights: dict | None = None,
                     min_ontime: float | None = None, max_geo: float | None = None,
                     exclude_modes: tuple = ()):
    """Combine cargo profile defaults with operator overrides."""
    pname = profile or ship["cargo_type"]
    if pname not in PROFILES:
        raise ValueError(f"Unknown profile '{pname}'. Options: {list(PROFILES)}")
    prof = PROFILES[pname]
    w = dict(prof.weights)
    if weights:
        w = normalise_weights({**{k: 0.0 for k in CRITERIA}, **weights})
    cons = Constraints(
        min_ontime=prof.min_ontime if min_ontime is None else min_ontime,
        max_geo=prof.max_geo if max_geo is None else max_geo,
        exclude_modes=tuple(exclude_modes))
    return pname, w, cons


def recommend(ship, routes: list, profile: str | None = None, weights: dict | None = None,
              min_ontime: float | None = None, max_geo: float | None = None,
              exclude_modes: tuple = (), scenario: str | None = None, n_sims: int = 4000,
              robustness_draws: int = 300, seed: int = 0, table: pd.DataFrame | None = None) -> Decision:
    pname, w, cons = resolve_settings(ship, profile, weights, min_ontime, max_geo, exclude_modes)
    if table is None:
        table = compute_metrics(routes, ship, scenario=scenario, n_sims=n_sims)
    return decide(table, w, cons, float(ship["value_usd"]), float(ship["deadline_days"]),
                  shipment_id=str(ship["shipment_id"]), robustness_draws=robustness_draws,
                  seed=seed, profile=pname)
