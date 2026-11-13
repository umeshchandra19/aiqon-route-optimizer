"""Monte Carlo model of route transit time.

Per leg:   transit = nominal_days * (1 + 5% jitter)  +  Bernoulli(p) * Exponential(mean)

A *systemic factor* z ~ LogNormal(mean 1, sigma 0.25) is drawn once per
simulated trip and multiplies every leg's delay probability.  This makes legs
of the same trip positively correlated (bad weather season, strike wave...),
which fattens the tail of the transit-time distribution compared with fully
independent legs - exactly the part that matters for deadlines.
"""
from __future__ import annotations

import zlib

import numpy as np

from .model import Route

SYSTEMIC_SIGMA = 0.25
JITTER = 0.05


def route_seed(route_id: str, salt: int = 0) -> int:
    """Deterministic seed per route so results are reproducible and comparable."""
    return (zlib.crc32(route_id.encode()) + 7919 * salt) % (2 ** 32)


def simulate_transit(route: Route, n: int, rng: np.random.Generator):
    """Simulate ``n`` trips. Returns total transit days, shape (n,)."""
    L = route.n_legs
    z = rng.lognormal(-SYSTEMIC_SIGMA ** 2 / 2, SYSTEMIC_SIGMA, size=(n, 1))
    p_eff = np.clip(route.p[None, :] * z, 0, 0.95)
    delayed = rng.random((n, L)) < p_eff
    extra = rng.exponential(route.m[None, :], size=(n, L)) * delayed
    base = route.days[None, :] * (1 + JITTER * rng.standard_normal((n, L)))
    return np.maximum(base, 0).sum(axis=1) + extra.sum(axis=1)


def analytic_summary(route: Route) -> dict:
    """Closed-form route aggregates (no simulation)."""
    base_days = float(route.days.sum())
    exp_days = base_days + float((route.p * route.m).sum())
    delay_prob = float(1 - np.prod(1 - route.p))
    cong = float((route.cong * route.days).sum() / max(route.days.sum(), 1e-9))
    geo = float(route.geo.max())
    risk_index = 0.4 * cong + 0.6 * geo
    return dict(cost_usd=float(route.cost.sum()), base_days=base_days, exp_days_analytic=exp_days,
                delay_prob=delay_prob, congestion=cong, geo=geo, risk_index=risk_index)
