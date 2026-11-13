"""Command-line interface.

    python -m routeopt all                      # generate data, run everything, make figures
    python -m routeopt recommend S007           # recommend + explain one shipment
    python -m routeopt recommend S007 --profile urgent --exclude-modes air
    python -m routeopt recommend S007 --weights cost=0.2,time=0.5,reliability=0.2,risk=0.1
    python -m routeopt recommend S007 --scenario red_sea
    python -m routeopt recommend S007 --sweep cost      # how the pick changes with the cost weight
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from .explain import explain
from .model import DEFAULT_DATA_DIR, DEFAULT_RESULTS_DIR, SCENARIOS, load_dataset
from .scoring import CRITERIA, PROFILES, compute_metrics, recommend


def _parse_weights(text):
    if not text:
        return None
    out = {}
    for part in text.split(","):
        k, v = part.split("=")
        k = k.strip()
        if k not in CRITERIA:
            raise SystemExit(f"Unknown criterion '{k}'. Use: {', '.join(CRITERIA)}")
        out[k] = float(v)
    return out


def _need_data(data_dir):
    if not (Path(data_dir) / "shipments.csv").exists():
        from .generate_data import generate
        print(f"No dataset in {data_dir}; generating one (seed 42)...")
        generate(40, 42, data_dir)


def cmd_generate(a):
    from .generate_data import generate
    n_ship, n_routes = generate(a.n_shipments, a.seed, a.data_dir)
    print(f"Generated {n_ship} shipments / {n_routes} route options in {a.data_dir}")


def cmd_list(a):
    _need_data(a.data_dir)
    ships, routes = load_dataset(a.data_dir)
    cols = ["shipment_id", "origin", "destination", "cargo_type", "weight_t", "value_usd", "deadline_days", "n_routes"]
    print(ships[cols].to_string(index=False))


def cmd_recommend(a):
    _need_data(a.data_dir)
    ships, routes = load_dataset(a.data_dir)
    if a.shipment not in ships.index:
        raise SystemExit(f"Unknown shipment '{a.shipment}'. Try: python -m routeopt list")
    ship = ships.loc[a.shipment]
    excl = tuple(x for x in (a.exclude_modes or "").split(",") if x)
    table = compute_metrics(routes[a.shipment], ship, scenario=a.scenario)
    dec = recommend(ship, routes[a.shipment], profile=a.profile, weights=_parse_weights(a.weights),
                    min_ontime=a.min_ontime, max_geo=a.max_geo, exclude_modes=excl,
                    scenario=a.scenario, table=table)
    ex = explain(dec, ship)
    if a.json:
        t = dec.table
        payload = {
            "shipment_id": a.shipment, "recommended_route": dec.chosen, "confidence": dec.confidence,
            "stability": dec.stability, "needs_review": dec.needs_review, "weights": dec.weights,
            "headline": ex["headline"], "explanation": ex["text"],
            "routes": json.loads(t.drop(columns=["has_air"]).replace({np.nan: None}).to_json(orient="records"))}
        print(json.dumps(payload, indent=2))
        return
    if a.scenario:
        print(f"[scenario: {a.scenario} - {SCENARIOS[a.scenario]['description']}]\n")
    print(ex["text"])
    if a.sweep:
        from .sensitivity import switch_points, weight_sweep_one
        sw = weight_sweep_one(table, ship, a.sweep, profile=a.profile, min_ontime=a.min_ontime,
                              max_geo=a.max_geo, exclude_modes=excl)
        print(f"\nSensitivity: weight on '{a.sweep}' swept 0 -> 1 (other weights rescaled)")
        print(sw.to_string(index=False))
        sp = switch_points(sw)
        print("Recommendation changes at:" if sp else "Recommendation never changes over this range.")
        for lo, hi, f, t in sp:
            print(f"  between weight {lo:.2f} and {hi:.2f}: {f} -> {t}")


def cmd_batch(a):
    _need_data(a.data_dir)
    ships, routes = load_dataset(a.data_dir)
    out = Path(a.results_dir)
    out.mkdir(parents=True, exist_ok=True)
    rows, md = [], ["# Recommendations and explanations for all shipments\n"]
    for sid in ships.index:
        ship = ships.loc[sid]
        dec = recommend(ship, routes[sid])
        ex = explain(dec, ship)
        t = dec.table
        c = t.loc[dec.chosen]
        rows.append(dict(shipment_id=sid, cargo_type=ship.cargo_type, origin=ship.origin,
                         destination=ship.destination, deadline_days=ship.deadline_days,
                         recommended=dec.chosen, family=c.family, modes=c.modes, path=c.path,
                         cost_usd=round(c.cost_usd), exp_days=round(c.exp_days, 1),
                         delay_prob=round(c.delay_prob, 3), p_ontime=round(c.p_ontime, 3),
                         risk_index=round(c.risk_index, 2), score=round(c.score, 1),
                         cheapest=t.cost_usd.idxmin(), fastest=t.exp_days.idxmin(),
                         confidence=dec.confidence, stability=dec.stability,
                         margin_pts=dec.margin, relaxed=dec.relaxed, needs_review=dec.needs_review,
                         headline=ex["headline"]))
        md.append(f"## {sid}\n\n```\n{ex['text']}\n```\n")
    df = pd.DataFrame(rows)
    df.to_csv(out / "recommendations.csv", index=False)
    (out / "explanations.md").write_text("\n".join(md))
    print(f"Wrote {len(df)} recommendations to {out}/recommendations.csv and explanations.md")
    print(df.family.value_counts().to_string())
    print("\nConfidence:", df.confidence.value_counts().to_dict(), "| needs review:", int(df.needs_review.sum()))


def _run_eval_and_sens(a, make_figs):
    from .evaluate import run_evaluation
    from .sensitivity import dataset_weight_sweep, delay_estimate_sensitivity
    out = Path(a.results_dir)
    res = run_evaluation(a.data_dir, out)
    ships, routes = load_dataset(a.data_dir)
    tabs = res["tables"]
    sweeps = {c: dataset_weight_sweep(ships, tabs, c, steps=21) for c in CRITERIA}
    pd.concat(sweeps.values()).to_csv(out / "sensitivity_weights.csv", index=False)
    dsens = delay_estimate_sensitivity(ships, routes)
    dsens.to_csv(out / "sensitivity_delay_estimates.csv", index=False)
    if make_figs:
        from .figures import fig_example, fig_method_comparison, fig_sensitivity
        figdir = out / "figures"
        figdir.mkdir(exist_ok=True)
        fig_method_comparison(res["summary"], figdir / "fig1_method_comparison.png")
        fig_sensitivity(sweeps, dsens, figdir / "fig2_sensitivity.png")
        sid = "S007" if "S007" in res["decisions"] else list(res["decisions"])[0]
        fig_example(res["decisions"][sid], ships.loc[sid], figdir / "fig3_example_tradeoff.png")
    return res, sweeps, dsens


def _print_eval(res):
    pd.set_option("display.width", 220)
    pd.set_option("display.max_columns", 30)
    s = res["summary"][["method", "mean_regret_pct_of_cargo_value", "mean_rel_regret_pct", "oracle_match_pct",
                        "mean_p_ontime_pct", "mean_freight_usd", "mean_exp_days"]]
    print("\n=== Method comparison (true expected business cost; lower regret is better) ===")
    print(s.round(2).to_string(index=False))
    print("\n=== Confidence calibration of 'Ours' ===")
    print(res["calibration"].round(2).to_string(index=False))
    print("\n=== Red Sea stress test ===")
    print(res["stress"].round(2).to_string(index=False))


def cmd_evaluate(a):
    _need_data(a.data_dir)
    res, _, _ = _run_eval_and_sens(a, make_figs=False)
    _print_eval(res)


def cmd_sensitivity(a):
    _need_data(a.data_dir)
    _, sweeps, dsens = _run_eval_and_sens(a, make_figs=False)
    for c, d in sweeps.items():
        print(f"\nWeight sweep on '{c}':")
        print(d[::4].round(1).to_string(index=False))
    print("\nDelay-estimate error:")
    print(dsens.round(1).to_string(index=False))


def cmd_all(a):
    from .generate_data import generate
    if a.regenerate or not (Path(a.data_dir) / "shipments.csv").exists():
        generate(40, 42, a.data_dir)
    cmd_batch(a)
    res, _, _ = _run_eval_and_sens(a, make_figs=True)
    _print_eval(res)
    print(f"\nFigures written to {Path(a.results_dir) / 'figures'}")


def build_parser():
    p = argparse.ArgumentParser(prog="routeopt", description="Shipment route recommendation under cost, time and risk.")
    p.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR))
    p.add_argument("--results-dir", default=str(DEFAULT_RESULTS_DIR))
    sub = p.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate", help="generate the synthetic dataset")
    g.add_argument("--n-shipments", type=int, default=40)
    g.add_argument("--seed", type=int, default=42)
    g.set_defaults(func=cmd_generate)

    sub.add_parser("list", help="list shipments").set_defaults(func=cmd_list)

    r = sub.add_parser("recommend", help="recommend and explain a route for one shipment")
    r.add_argument("shipment")
    r.add_argument("--profile", choices=list(PROFILES), help="override the cargo-type profile")
    r.add_argument("--weights", help="e.g. cost=0.2,time=0.5,reliability=0.2,risk=0.1")
    r.add_argument("--min-ontime", type=float, help="hard rule: minimum P(on-time), 0..1")
    r.add_argument("--max-geo", type=float, help="hard rule: maximum geopolitical risk, 0..1")
    r.add_argument("--exclude-modes", help="comma list, e.g. air,rail")
    r.add_argument("--scenario", choices=list(SCENARIOS), help="apply a disruption scenario to the risk inputs")
    r.add_argument("--sweep", choices=CRITERIA, help="also sweep this criterion's weight 0->1")
    r.add_argument("--json", action="store_true", help="machine-readable output")
    r.set_defaults(func=cmd_recommend)

    sub.add_parser("batch", help="recommend for all shipments").set_defaults(func=cmd_batch)
    sub.add_parser("evaluate", help="evaluate against baselines and ground truth").set_defaults(func=cmd_evaluate)
    sub.add_parser("sensitivity", help="weight and estimate-error sensitivity").set_defaults(func=cmd_sensitivity)
    al = sub.add_parser("all", help="batch + evaluation + sensitivity + figures")
    al.add_argument("--regenerate", action="store_true", help="regenerate the dataset first")
    al.set_defaults(func=cmd_all)
    return p


def main(argv=None):
    a = build_parser().parse_args(argv)
    a.func(a)


if __name__ == "__main__":
    main()
