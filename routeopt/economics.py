"""Business-cost model.

This is the *independent yardstick* used to evaluate recommendations.  It is
deliberately different from the operator-facing weighted score in
``scoring.py``: it prices the outcome of a shipment in dollars

    total = freight + inventory carrying cost + late-delivery penalty + incident loss

and is evaluated by Monte Carlo against the hidden ground-truth lane
parameters.  The scorer never sees these formulas or the ground truth.
"""
from __future__ import annotations

import numpy as np

from .model import Route
from .simulate import route_seed, simulate_transit

CARRY_RATE_PER_DAY = 0.20 / 365          # 20% annual inventory carrying cost
LATE_RATE_PER_DAY = {                    # share of cargo value lost per day late
    "standard": 0.002,
    "perishable": 0.030,
    "high_value": 0.004,
    "urgent": 0.015,
}
INCIDENT_COEF = 0.06                     # per-leg incident prob = coef * geo^2
INCIDENT_LOSS_FRACTION = 0.50            # share of cargo value lost in an incident


def expected_outcome(route: Route, ship, n: int = 4000, salt: int = 0) -> dict:
    """Expected business outcome of using ``route`` for ``ship`` (Monte Carlo)."""
    rng = np.random.default_rng(route_seed(route.route_id, salt))
    T = simulate_transit(route, n, rng)
    value = float(ship["value_usd"])
    deadline = float(ship["deadline_days"])
    late = np.maximum(T - deadline, 0.0)
    ip = INCIDENT_COEF * route.geo ** 2
    incident = (rng.random((n, route.n_legs)) < ip[None, :]).any(axis=1)

    freight = float(route.cost.sum())
    carrying = value * CARRY_RATE_PER_DAY * T
    late_pen = value * LATE_RATE_PER_DAY[ship["cargo_type"]] * late
    loss = value * INCIDENT_LOSS_FRACTION * incident
    total = freight + carrying + late_pen + loss
    return dict(
        biz_cost=float(total.mean()), freight=freight, carrying=float(carrying.mean()),
        late_penalty=float(late_pen.mean()), incident_loss=float(loss.mean()),
        p_ontime=float((T <= deadline).mean()), exp_days=float(T.mean()),
        incident_prob=float(incident.mean()))
