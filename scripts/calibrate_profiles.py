"""Calibrate cargo-profile weights / on-time constraints on a SEPARATE dataset.

For each cargo type, search over (criterion weights, min_ontime) and keep the
setting with the lowest regret (as % of cargo value) among those that meet the
cargo type's service-level target (mean true P(on-time)).  The calibration
dataset (seed 7, 200 shipments) is disjoint from the evaluation dataset
(seed 42, 40 shipments); the chosen values are then frozen in
``routeopt/scoring.py::PROFILES``.

Usage:  python scripts/calibrate_profiles.py
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from routeopt.evaluate import estimate_tables, true_outcomes          # noqa: E402
from routeopt.generate_data import generate                           # noqa: E402
from routeopt.model import load_dataset                               # noqa: E402
from routeopt.scoring import Constraints, decide                       # noqa: E402

SLA = {"standard": 0.90, "perishable": 0.93, "high_value": 0.95, "urgent": 0.95}
# Hard-rule thresholds are *policy* (service-level commitments), not tuned.
MIN_ONTIME = {"standard": 0.70, "perishable": 0.85, "high_value": 0.80, "urgent": 0.90}
MAX_GEO = {"standard": 0.90, "perishable": 0.90, "high_value": 0.50, "urgent": 0.90}
# Only the overall weight on cost is calibrated; the relative priority among
# time / reliability / risk keeps each profile's intended shape.
SHAPE = {"standard": (0.40, 0.40, 0.20), "perishable": (0.44, 0.37, 0.19),
         "high_value": (0.18, 0.29, 0.53), "urgent": (0.56, 0.33, 0.11)}
COST_GRID = [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.60, 0.70]
CAL_DIR = ROOT / "data" / "calibration"


def weights_for(cargo, c):
    t, r, k = SHAPE[cargo]
    return {"cost": c, "time": (1 - c) * t, "reliability": (1 - c) * r, "risk": (1 - c) * k}


def main():
    generate(200, seed=7, out_dir=CAL_DIR)
    ships, routes_est = load_dataset(CAL_DIR)
    _, routes_true = load_dataset(CAL_DIR, truth=True)
    truth = true_outcomes(ships, routes_true)
    tabs = estimate_tables(ships, routes_est)
    out = {}
    for cargo, sla in SLA.items():
        ids = list(ships.index[ships.cargo_type == cargo])
        grid = []
        for c in COST_GRID:
            wd = weights_for(cargo, c)
            reg, ont = [], []
            for sid in ids:
                ship = ships.loc[sid]
                d = decide(tabs[sid], wd, Constraints(MIN_ONTIME[cargo], MAX_GEO[cargo]), float(ship.value_usd),
                           float(ship.deadline_days), sid, robustness_draws=0)
                tr = truth[sid].astype(float)
                reg.append((tr.loc[d.chosen, "biz_cost"] - tr["biz_cost"].min()) / ship.value_usd)
                ont.append(tr.loc[d.chosen, "p_ontime"])
            grid.append(dict(cost_weight=c, regret_pct_of_value=100 * float(np.mean(reg)),
                             mean_p_ontime=float(np.mean(ont))))
        ok = [g for g in grid if g["mean_p_ontime"] >= sla] or grid
        floor = min(g["regret_pct_of_value"] for g in ok)
        # parsimony: smallest cost weight within 0.10 pts (of cargo value) of the best regret,
        # so the non-cost criteria keep as much influence as the data allows
        best = min((g for g in ok if g["regret_pct_of_value"] <= floor + 0.10), key=lambda g: g["cost_weight"])
        out[cargo] = dict(n_shipments=len(ids), sla_target=sla, chosen_cost_weight=best["cost_weight"],
                          weights=weights_for(cargo, best["cost_weight"]), min_ontime=MIN_ONTIME[cargo],
                          grid=grid)
        print(cargo, "n=", len(ids), "chosen c=", best["cost_weight"],
              "| regret %value", round(best["regret_pct_of_value"], 3), "| P(on-time)", round(best["mean_p_ontime"], 3))
        for g in grid:
            print("   c=%.2f regret=%.3f%% ontime=%.3f" % (g["cost_weight"], g["regret_pct_of_value"], g["mean_p_ontime"]))
    (ROOT / "results" / "calibration_profiles.json").write_text(json.dumps(out, indent=2, default=float))


if __name__ == "__main__":
    main()
