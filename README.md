# Shipment Route Recommendation under Cost, Time and Risk

Take-home for the **Aiqon AI Internship**. Given a shipment and several candidate routes (multi-leg, multi-modal),
the system recommends one route and explains in plain language why it beats the alternatives.

* **Technical report (3 pages):** [`report/Aiqon_Route_Optimization_Report.pdf`](report/Aiqon_Route_Optimization_Report.pdf)
* **Demo script (optional, 5 min):** [`demo/DEMO_SCRIPT.md`](demo/DEMO_SCRIPT.md), `demo/run_demo.sh`

## Quick start

```bash
pip install -r requirements.txt
python -m routeopt all                      # data -> recommendations -> evaluation -> sensitivity -> figures (~30 s)
python -m routeopt recommend S007           # recommend + explain one shipment
pytest -q                                   # 13 unit tests
python report/build_report.py               # rebuild the PDF from results/
```

More examples:

```bash
python -m routeopt list                                         # shipments in the dataset
python -m routeopt recommend S007 --profile urgent              # override the cargo profile
python -m routeopt recommend S007 --weights cost=0.2,time=0.5,reliability=0.2,risk=0.1
python -m routeopt recommend S004 --exclude-modes air           # operator rule
python -m routeopt recommend S006 --scenario red_sea            # disruption scenario (also: lax_congestion)
python -m routeopt recommend S007 --sweep cost                  # where does the pick flip as the cost weight changes?
python -m routeopt recommend S007 --json                        # machine-readable output
python -m routeopt generate --n-shipments 40 --seed 42          # regenerate the synthetic data
python scripts/calibrate_profiles.py                            # re-calibrate cost weights on a separate dataset (seed 7)
```

## How it works

For each shipment:

1. **Metrics** - Monte Carlo (4,000 trips, correlated legs via a shared systemic factor) gives expected days, P90,
   delay probability, P(on-time), and a congestion / geopolitical risk index per route.
2. **Hard rules** (non-compensatory) - minimum P(on-time), maximum geopolitical risk (cargo-specific), excluded
   modes. If nothing survives, the system relaxes the on-time rule and says so.
3. **Pareto screen** - flags dominated routes.
4. **Weighted score** over four penalties on absolute scales (freight as a share of cargo value, deadline buffer,
   delay probability, risk), with weights set by cargo profile (`standard`, `perishable`, `high_value`, `urgent`).
5. **Robustness** - 300 perturbed re-runs (cost, time, delay odds, risk, weights) -> High / Medium / Low confidence.
6. **Explanation** - deterministic text from the same numbers: comparison vs cheapest / fastest / runner-up,
   rejection reason for every alternative, deciding factor, confidence, and a *price of the hard rules* check that
   flags decisions where rules force a very expensive pick.

## Data (synthetic)

`data/shipments.csv` (40 shipments), `data/route_options.csv` (157 route options, planner-friendly view),
`data/route_legs.csv` (leg-level **estimates** the system sees) and `data/route_legs_truth.csv`
(hidden **ground truth**, used only by the evaluation). Construction is described in the report and in
`routeopt/generate_data.py`. `data/calibration/` is a separate 200-shipment dataset (seed 7) used only to calibrate
the cost weight of each profile.

## Evaluation

`python -m routeopt evaluate` scores each method's pick against the ground truth with a dollar-based business cost
(freight + carrying + lateness + incident loss) and compares it with the hindsight-best route.

| Method | Excess cost (% of cargo value) | Matches oracle | True P(on-time) |
|---|---|---|---|
| **Ours** | 0.58% | 80% | 99% |
| EV-cost baseline* | 0.02% | 95% | 86% |
| Fixed weights, no rules | 2.33% | 75% | 97% |
| Cheapest | 3.57% | 58% | 70% |
| Fastest | 26.0% | 15% | 100% |
| Lowest risk | 23.0% | 15% | 64% |
| Random | 15.3% | - | 59% |

\*shares the yardstick's economic model, so it is an upper bound rather than independent evidence, and it does not
honour service-level rules. Also produced: confidence calibration, Red Sea / LA-congestion stress tests, weight and
delay-estimate sensitivity (`results/*.csv`, `results/figures/*.png`). See the report for discussion and limitations.

## Repository layout

```
routeopt/      network.py  generate_data.py  model.py  simulate.py  economics.py
               scoring.py  explain.py  sensitivity.py  evaluate.py  figures.py  cli.py
data/          synthetic dataset (+ calibration/ for profile calibration)
results/       recommendations.csv, explanations.md, eval_*.csv, sensitivity_*.csv, figures/
report/        build_report.py + the PDF report
scripts/       calibrate_profiles.py
tests/         pytest suite
demo/          demo script
```

Everything is seeded and deterministic (`--seed 42`).
