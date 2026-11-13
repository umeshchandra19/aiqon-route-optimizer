"""Core data structures: Route, disruption scenarios, dataset loading."""
from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = REPO_ROOT / "data"
DEFAULT_RESULTS_DIR = REPO_ROOT / "results"


@dataclass
class Route:
    """One end-to-end route option for a shipment; arrays are per leg."""

    route_id: str
    shipment_id: str
    nodes: list          # length L+1, node codes
    modes: list          # length L
    corridors: list      # length L
    cost: np.ndarray     # USD per leg (freight + handling at arrival node)
    days: np.ndarray     # nominal days per leg (incl. dwell at arrival node)
    p: np.ndarray        # delay probability per leg
    m: np.ndarray        # mean extra days if delayed
    cong: np.ndarray     # congestion 0..1
    geo: np.ndarray      # geopolitical risk 0..1

    @property
    def n_legs(self) -> int:
        return len(self.modes)

    @property
    def has_air(self) -> bool:
        return "air" in self.modes

    def path_str(self) -> str:
        return " > ".join(self.nodes)

    def modes_str(self) -> str:
        return ">".join(self.modes)

    def family(self) -> str:
        """Coarse route family, used for reporting."""
        if self.has_air:
            return "Air"
        if "eurasia_rail" in self.corridors:
            return "Eurasia rail"
        if "red_sea" in self.corridors:
            return "Suez / Red Sea"
        if "CPT" in self.nodes:
            return "Cape of Good Hope"
        if "PAN" in self.nodes:
            return "Panama"
        if "lax" in self.corridors:
            return "Transpacific / US land-bridge"
        return "Other surface"


# --------------------------------------------------------------------------
# Disruption scenarios: multipliers applied to legs tagged with a corridor.
# --------------------------------------------------------------------------
SCENARIOS = {
    "red_sea": {
        "corridor": "red_sea",
        "delay_p_mult": 2.0, "delay_mean_mult": 1.6, "geo_floor": 0.95, "cong_add": 0.0,
        "description": "Red Sea / Suez crisis: delay odds x2, delay length x1.6, geopolitical risk -> 0.95",
    },
    "lax_congestion": {
        "corridor": "lax",
        "delay_p_mult": 1.8, "delay_mean_mult": 1.5, "geo_floor": 0.0, "cong_add": 0.25,
        "description": "US west-coast port congestion: delay odds x1.8, delay length x1.5, congestion +0.25",
    },
}


def apply_scenario(route: Route, scenario: str | None) -> Route:
    if not scenario:
        return route
    if scenario not in SCENARIOS:
        raise ValueError(f"Unknown scenario '{scenario}'. Options: {list(SCENARIOS)}")
    sc = SCENARIOS[scenario]
    mask = np.array([c == sc["corridor"] for c in route.corridors])
    if not mask.any():
        return route
    p = route.p.copy()
    m = route.m.copy()
    geo = route.geo.copy()
    cong = route.cong.copy()
    p[mask] = np.clip(p[mask] * sc["delay_p_mult"], 0, 0.95)
    m[mask] = m[mask] * sc["delay_mean_mult"]
    geo[mask] = np.maximum(geo[mask], sc["geo_floor"])
    cong[mask] = np.clip(cong[mask] + sc["cong_add"], 0, 1)
    return replace(route, p=p, m=m, geo=geo, cong=cong)


def scale_delay(route: Route, factor: float) -> Route:
    """Scale every leg's delay probability (used for sensitivity analysis)."""
    return replace(route, p=np.clip(route.p * factor, 0, 0.95))


# --------------------------------------------------------------------------
# Dataset IO
# --------------------------------------------------------------------------
LEG_COLUMNS = ["shipment_id", "route_id", "leg_idx", "from_node", "to_node", "mode", "corridor",
               "cost_usd", "days", "delay_p", "delay_mean", "congestion", "geo"]


def route_to_rows(route: Route):
    rows = []
    for i in range(route.n_legs):
        rows.append(dict(
            shipment_id=route.shipment_id, route_id=route.route_id, leg_idx=i,
            from_node=route.nodes[i], to_node=route.nodes[i + 1], mode=route.modes[i],
            corridor=route.corridors[i], cost_usd=round(float(route.cost[i]), 2),
            days=round(float(route.days[i]), 3), delay_p=round(float(route.p[i]), 4),
            delay_mean=round(float(route.m[i]), 3), congestion=round(float(route.cong[i]), 3),
            geo=round(float(route.geo[i]), 3)))
    return rows


def routes_from_legs(legs: pd.DataFrame) -> dict:
    """Group a legs table into ``{shipment_id: [Route, ...]}``."""
    out: dict[str, list[Route]] = {}
    for (sid, rid), g in legs.sort_values(["shipment_id", "route_id", "leg_idx"]).groupby(
            ["shipment_id", "route_id"], sort=True):
        g = g.reset_index(drop=True)
        nodes = [g.loc[0, "from_node"]] + list(g["to_node"])
        corridors = [c if isinstance(c, str) else "" for c in g["corridor"].fillna("")]
        out.setdefault(sid, []).append(Route(
            route_id=rid, shipment_id=sid, nodes=nodes, modes=list(g["mode"]),
            corridors=corridors, cost=g["cost_usd"].to_numpy(float), days=g["days"].to_numpy(float),
            p=g["delay_p"].to_numpy(float), m=g["delay_mean"].to_numpy(float),
            cong=g["congestion"].to_numpy(float), geo=g["geo"].to_numpy(float)))
    return out


def load_dataset(data_dir: str | Path = DEFAULT_DATA_DIR, truth: bool = False):
    """Return ``(shipments_df indexed by shipment_id, routes dict)``.

    With ``truth=True`` the hidden ground-truth leg parameters are loaded
    instead of the estimates the decision system sees (evaluation only).
    """
    data_dir = Path(data_dir)
    ships = pd.read_csv(data_dir / "shipments.csv").set_index("shipment_id", drop=False)
    legs = pd.read_csv(data_dir / ("route_legs_truth.csv" if truth else "route_legs.csv"))
    return ships, routes_from_legs(legs)
