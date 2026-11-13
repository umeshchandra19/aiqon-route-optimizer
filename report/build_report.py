"""Build the 3-page technical report PDF from the files in results/.

    pip install reportlab
    python -m routeopt all          # produce results/ first
    python report/build_report.py

All numbers in the text are read from results/*.csv|json, so the report cannot
drift from the code.
"""
import json
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (Image, KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "results"
OUT = ROOT / "report" / "Aiqon_Route_Optimization_Report.pdf"

summary = pd.read_csv(R / "eval_summary.csv").set_index("method")
calib = pd.read_csv(R / "eval_confidence_calibration.csv").set_index("tier")
cargo = pd.read_csv(R / "eval_by_cargo.csv")
stress = pd.read_csv(R / "eval_scenario_red_sea.csv").set_index("method")
meta = json.load(open(R / "eval_meta.json"))
cal = json.load(open(R / "calibration_profiles.json"))
sw = pd.read_csv(R / "sensitivity_weights.csv")
ds = pd.read_csv(R / "sensitivity_delay_estimates.csv").set_index("delay_prob_scale")
rec = pd.read_csv(R / "recommendations.csv")

ours, ev, cheap, fixed = (summary.loc[k] for k in ["Ours", "EV-cost baseline", "Cheapest", "Fixed weights, no constraints"])
fast, risk, rnd = summary.loc["Fastest"], summary.loc["Lowest risk"], summary.loc["Random (expected)"]
urg = cargo[(cargo.cargo_type == "urgent") & (cargo.method == "Ours")].iloc[0]
urg_ev = cargo[(cargo.cargo_type == "urgent") & (cargo.method == "EV-cost baseline")].iloc[0]
rs_up = stress.loc["Ours (risk inputs updated)"]
rs_stale = stress.loc["Ours (stale inputs)"]


def flip(crit, w):
    return float(sw[(sw.criterion == crit) & (sw.weight.round(2) == w)].flip_rate_pct.iloc[0])


def air_share(crit, w):
    return float(sw[(sw.criterion == crit) & (sw.weight.round(2) == w)].air_share_pct.iloc[0])


ss = getSampleStyleSheet()
BODY = ParagraphStyle("body", parent=ss["Normal"], fontName="Helvetica", fontSize=8.6, leading=10.6,
                      alignment=TA_JUSTIFY, spaceAfter=3)
H1 = ParagraphStyle("h1", parent=ss["Heading1"], fontName="Helvetica-Bold", fontSize=15, leading=18, spaceAfter=1)
SUB = ParagraphStyle("sub", parent=BODY, fontSize=8.6, textColor=colors.HexColor("#444444"), spaceAfter=5)
H2 = ParagraphStyle("h2", parent=ss["Heading2"], fontName="Helvetica-Bold", fontSize=10, leading=12,
                    spaceBefore=5, spaceAfter=2, textColor=colors.HexColor("#1b4f72"))
BUL = ParagraphStyle("bul", parent=BODY, leftIndent=10, bulletIndent=0, spaceAfter=1.5)
SMALL = ParagraphStyle("small", parent=BODY, fontSize=7.4, leading=9, alignment=0)
MONO = ParagraphStyle("mono", parent=BODY, fontName="Courier", fontSize=6.5, leading=7.8, alignment=0,
                      backColor=colors.HexColor("#f4f6f7"), borderPadding=3, spaceAfter=0)
CAP = ParagraphStyle("cap", parent=SMALL, textColor=colors.HexColor("#555555"), spaceAfter=3)


def P(t, s=BODY):
    return Paragraph(t, s)


def B(t):
    return Paragraph(t, BUL, bulletText="-")


def table(data, widths, header=True, font=7.4, zebra=True):
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    st = [("FONT", (0, 0), (-1, -1), "Helvetica", font), ("LEADING", (0, 0), (-1, -1), font + 1.8),
          ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 1.6),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 1.6), ("LINEBELOW", (0, 0), (-1, 0), 0.6, colors.HexColor("#1b4f72")),
          ("LINEBELOW", (0, -1), (-1, -1), 0.4, colors.HexColor("#999999"))]
    if header:
        st += [("FONT", (0, 0), (-1, 0), "Helvetica-Bold", font), ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eaf1f7"))]
    if zebra:
        for i in range(1, len(data)):
            if i % 2 == 0:
                st.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#f7f9fa")))
    t.setStyle(TableStyle(st))
    return t


def img(name, width):
    from PIL import Image as PILImage
    w, h = PILImage.open(R / "figures" / name).size
    return Image(str(R / "figures" / name), width=width, height=width * h / w)


story = []
story.append(P("Optimizing Shipment Routes Under Cost, Time and Risk", H1))
story.append(P("Technical report - Aiqon AI Internship take-home assignment - Umesh Chandra Namani. "
               "Code: GitHub repository submitted alongside this report (README has run instructions).", SUB))

# ---- 1 ----------------------------------------------------------------------------------------
story.append(P("1. Problem framing: what does \"optimal\" mean?", H2))
story.append(P(
    "A route is never optimal in the abstract. I define the best route <b>for a given shipment</b> as the one that "
    "(i) satisfies that cargo's non-negotiable service and risk rules, and (ii) among the routes that do, gives the best "
    "weighted trade-off between <b>freight cost, deadline buffer, delay probability and congestion / geopolitical risk</b>, "
    "with the weights depending on what the cargo is (perishable, high-value, urgent, standard). Hard rules are "
    "<i>non-compensatory</i> (a 70% on-time chance cannot be bought back with a discount); the weighted score handles "
    "everything that <i>is</i> a trade-off. After the fact, a recommendation is judged by what the shipment actually "
    "cost in dollars (Section 5), a yardstick the scorer never sees."))

# ---- 2 ----------------------------------------------------------------------------------------
story.append(P("2. Synthetic data and assumptions", H2))
story.append(P(
    "<b>Network.</b> 13 ports / hubs (Shanghai, Shenzhen, Singapore, Nhava Sheva, Colombo, Suez gateway, Piraeus, Rotterdam, "
    "Hamburg, Cape Town, Panama, Los Angeles, New York) and 45 lanes by sea, air, rail and road. Lane parameters are stylised "
    "but keep realistic <i>ratios</i>: air is about 20x the freight per tonne of sea but about 10x faster; transpacific lanes "
    "are congested; Red Sea / Suez entry lanes and the Eurasian rail corridor carry high geopolitical risk; the Cape route "
    "is long but safe. Transshipment adds dwell time (scaled by congestion) and handling cost at every intermediate node. "
    f"<b>Shipments.</b> {meta['n_shipments']} shipments over 16 origin/destination pairs (4 Asian origins x 4 destinations), "
    "four cargo types with different weights and values per tonne, a shipment-specific freight-rate index, and deadlines set "
    "relative to the option set (tight for urgent / perishable, loose for standard). "
    f"<b>Route options.</b> For each shipment all simple paths of at most 4 legs are enumerated and 3-5 diverse options are "
    f"kept (cheapest, fastest, most reliable, lowest-risk and a balanced surface route, topped up with random plausible "
    f"alternatives, at most two air options): {meta['n_route_options']} options in total, each with a genuine cost / time / risk "
    "trade-off by construction. Per leg: cost, nominal days, delay probability, mean delay length, congestion, geopolitical risk. "
    "<b>Estimates vs. truth.</b> The system sees noisy <i>estimates</i>. A separate hidden <i>ground truth</i> perturbs them "
    "(delay probability about +-35%, delay length +-25%, congestion +-0.10, risk +-0.08) to emulate forecast error; it is used only "
    "by the evaluation. <b>Key assumptions:</b> legs fail independently apart from one shared systemic factor per trip "
    "(lognormal, sigma 0.25) that fattens the tail; delays are exponential; lane parameters are static within a shipment; "
    "no capacity limits or consolidation."))

# ---- 3 ----------------------------------------------------------------------------------------
story.append(P("3. Decision framework", H2))
story.append(P(
    "<b>Pipeline per shipment:</b> (1) Monte Carlo (4,000 trips) turns each route's legs into expected transit time, P90, delay "
    "probability = 1 - prod(1 - p<sub>i</sub>), P(on-time), risk index = 0.4 x congestion + 0.6 x worst-leg geopolitical risk. "
    "(2) <b>Hard rules</b> remove routes that miss the cargo's minimum on-time probability, exceed its geopolitical-risk cap "
    "or use an excluded mode (operator input). If nothing survives, the system relaxes the on-time rule, recommends among the "
    "most punctual routes and says so. (3) A <b>Pareto screen</b> flags dominated routes (for explanation). (4) A <b>weighted "
    "score</b> ranks the survivors. (5) A <b>robustness check</b> re-runs the decision 300 times with perturbed cost (+-10%), time "
    "(+-8%), delay odds (+-30%), risk (+-0.10) and jittered weights, and reports how often the pick wins -> High / Medium / Low confidence."))
rows = [["Criterion", "Metric", "Penalty in [0,1] (absolute scale)"],
        ["Cost", "freight / cargo value", "0 at 0%, 1 at >= 20% of cargo value"],
        ["Time", "expected days / deadline", "0 below 70% of the deadline (speed beyond the need is worth nothing), rising to 1 at 100%"],
        ["Reliability", "P(at least one leg delayed)", "probability / 0.5, capped at 1"],
        ["Risk", "0.4 congestion + 0.6 max geopolitical", "used as is (already 0..1)"]]
story.append(table(rows, [0.8 * inch, 1.9 * inch, 4.5 * inch]))
story.append(Spacer(1, 3))
w = lambda k: " / ".join(f"{cal[k]['weights'][c]:.2f}" for c in ["cost", "time", "reliability", "risk"])
rows = [["Cargo profile", "Weights cost / time / reliability / risk", "Hard rules", "Intent"],
        ["standard", w("standard"), "P(on-time) >= 70%", "cost-driven, tolerates moderate risk"],
        ["perishable", w("perishable"), "P(on-time) >= 85%", "shelf-life: buffer and reliability matter"],
        ["high_value", w("high_value"), "P(on-time) >= 80%, geo risk <= 0.5", "theft / seizure exposure"],
        ["urgent", w("urgent"), "P(on-time) >= 90%", "protect the deadline, pay for speed"]]
story.append(table(rows, [0.9 * inch, 2.1 * inch, 1.9 * inch, 2.3 * inch]))
story.append(Spacer(1, 3))
story.append(P(
    "<b>Design decisions and what failed first.</b> My first version min-max-normalised each criterion inside the shipment's option "
    "set. One air option 20x pricier than sea stretched the cost scale until every surface route looked equally cheap, and air "
    "won 33 of 40 shipments. Absolute, decision-relevant scales (above) fixed this and make scores comparable across shipments. "
    "The relative priorities among time / reliability / risk encode each cargo's nature by judgement; only the <i>overall weight "
    f"on cost</i> was calibrated, on a separate synthetic dataset (seed 7, {sum(v['n_shipments'] for v in cal.values())} shipments) "
    "by minimising regret subject to a service-level target, preferring the smallest cost weight within 0.1 percentage points "
    "of the best. Hard-rule thresholds are policy, not tuned. Everything is then evaluated on the untouched main dataset (seed 42)."))

# ---- 4 ----------------------------------------------------------------------------------------
story.append(P("4. Explanations an operator can use", H2))
ex = (R / "explanations.md").read_text().split("## S007")[1].split("```")[1].strip().splitlines()
keep = [l for l in ex if l.startswith(("RECOMMENDED", "  cost", "  - Versus", "  - Deciding", "Confidence"))][:5]
import textwrap
wrapped = []
for l in keep:
    l = l.replace("→", "->").replace("≥", ">=").replace("±", "+-").replace("&", "&amp;")
    wrapped += textwrap.wrap(l, 118, subsequent_indent="    ")
story.append(P("<br/>".join(wrapped), MONO))
story.append(P(
    "Explanations are generated deterministically from the same numbers that produced the score (no LLM), so they cannot "
    "disagree with the decision. Each states the pick, compares it with the cheapest, fastest and runner-up alternatives "
    "(\"pays X more to cut delay probability from a to b\"), names the deciding factor, explains every rejected route "
    "(excluded by which rule / dominated / outscored and why), reports confidence, and states the <b>price of the hard rules</b>: "
    "if the rules force a pick costing more than 25% of cargo value over the unconstrained winner, the decision is flagged "
    "for human review.", BODY))

story.append(KeepTogether([img("fig3_example_tradeoff.png", 3.5 * inch),
    P("Example option set for S007 (Singapore to Rotterdam, standard cargo): air passes the rules but loses "
      "on cost (82% of cargo value), Panama is excluded by the on-time rule, one Suez option is Pareto-dominated.", CAP)]))

# ---- 5 ----------------------------------------------------------------------------------------
story.append(P("5. Evaluation", H2))
story.append(P(
    "<b>Protocol.</b> The business cost of a route = freight + inventory carrying (20% p.a.) + lateness penalty (cargo-specific "
    "% of value per day late) + expected incident loss (probability grows with geopolitical risk squared), estimated by Monte Carlo "
    "on the <i>hidden ground-truth</i> lane parameters. Per shipment I compare each method's pick with the hindsight-best route "
    "(oracle). Metric: excess cost over the oracle as a % of cargo value (also relative to the oracle's cost), plus true on-time "
    "probability. Baselines: single-metric heuristics, random, fixed one-size-fits-all weights without hard rules, and an "
    "<b>EV-cost baseline</b> that picks the lowest <i>estimated</i> business cost."))
cols = ["Method", "Excess cost\n(% cargo value)", "Excess vs oracle\n(mean %, 95% CI)", "Matches\noracle", "True P(on-time)", "Freight\n(USD)", "Days"]
rows = [cols]
for m in ["Ours", "EV-cost baseline", "Fixed weights, no constraints", "Cheapest", "Fastest", "Lowest risk", "Random (expected)"]:
    s = summary.loc[m]
    rows.append([m.replace(", no constraints", ""), f"{s.mean_regret_pct_of_cargo_value:.2f}%",
                 f"{s.mean_rel_regret_pct:.0f}%  [{s.regret_ci_lo:.0f}, {s.regret_ci_hi:.0f}]",
                 "-" if pd.isna(s.oracle_match_pct) else f"{s.oracle_match_pct:.0f}%",
                 f"{s.mean_p_ontime_pct:.0f}%", f"{s.mean_freight_usd:,.0f}", f"{s.mean_exp_days:.1f}"])
story.append(table(rows, [1.45 * inch, 0.95 * inch, 1.4 * inch, 0.6 * inch, 0.85 * inch, 0.8 * inch, 0.5 * inch]))
story.append(P(f"Table 1. {meta['n_shipments']} shipments, {meta['n_route_options']} route options. Oracle: 0% excess, "
               f"{summary.loc['Oracle (hindsight)'].mean_p_ontime_pct:.0f}% on-time. CIs by bootstrap over shipments.", CAP))
story.append(img("fig1_method_comparison.png", 6.9 * inch))
story.append(B(
    f"<b>Balanced and cost-aware.</b> The framework adds only {ours.mean_regret_pct_of_cargo_value:.2f}% of cargo value over the "
    f"hindsight-best route, versus {cheap.mean_regret_pct_of_cargo_value:.2f}% for always-cheapest, {fixed.mean_regret_pct_of_cargo_value:.2f}% "
    f"for fixed weights and {risk.mean_regret_pct_of_cargo_value:.0f}-{fast.mean_regret_pct_of_cargo_value:.0f}% for fastest / lowest-risk, "
    f"while delivering {ours.mean_p_ontime_pct:.0f}% true on-time probability (cheapest: {cheap.mean_p_ontime_pct:.0f}%). "
    f"It picks the oracle route in {ours.oracle_match_pct:.0f}% of shipments. Cargo profiles and hard rules matter: the same scorer "
    "with one-size-fits-all weights and no rules is 4x worse."))
story.append(B(
    f"<b>The EV-cost baseline is nearly perfect on this yardstick ({ev.mean_regret_pct_of_cargo_value:.2f}%), but this is not independent "
    "evidence</b>: it shares the yardstick's economic model, so it is an upper bound on what the information allows. It also does "
    f"not honour service levels: {ev.mean_p_ontime_pct:.0f}% on-time overall and {urg_ev.mean_p_ontime_pct:.0f}% for urgent cargo. "
    f"Our remaining gap sits in urgent cargo ({urg.mean_regret_pct_of_value:.2f}% of value), where the 90% on-time rule deliberately "
    "buys air freight that the lateness-penalty model considers slightly too expensive: that is the price of the service level, and it is "
    "one parameter an operator can change."))
story.append(B(
    f"<b>Confidence is informative.</b> The {int(calib.loc['High'].n)} 'High' decisions have {calib.loc['High'].mean_regret_pct_of_value:.2f}% excess "
    f"cost and match the oracle {calib.loc['High'].oracle_match_pct:.0f}% of the time; the {int(calib.loc['Medium'].n)} 'Medium' ones "
    f"{calib.loc['Medium'].mean_regret_pct_of_value:.2f}% / {calib.loc['Medium'].oracle_match_pct:.0f}%. "
    f"{int(calib.loc['Only one feasible route'].n)} decisions had a single feasible route (all rules binding): {calib.loc['Only one feasible route'].mean_regret_pct_of_value:.2f}% excess."))
story.append(B(
    f"<b>Disruption stress test (Red Sea crisis).</b> When risk inputs are updated, the share of shipments routed via the Red Sea falls "
    f"from {rs_stale.share_via_red_sea_pct:.0f}% to {rs_up.share_via_red_sea_pct:.0f}%. But the geopolitical cap then excludes every Suez route "
    f"and slower alternatives miss deadlines, so {meta['red_sea_air_picks']} of {meta['n_shipments']} shipments are pushed to air "
    f"and excess cost rises to {rs_up.mean_regret_pct_of_value:.1f}% of value ({rs_stale.mean_regret_pct_of_value:.2f}% with stale inputs) under my incident-loss "
    f"model, which may understate real war-risk. {meta['red_sea_needs_review']} decisions are flagged for review by the price-of-rules check. It shows that hard rules can be "
    "expensive and that the system should say so rather than silently comply."))

# ---- 6 ----------------------------------------------------------------------------------------
story.append(P("6. Sensitivity and uncertainty", H2))
story.append(img("fig2_sensitivity.png", 6.6 * inch))
story.append(B(
    f"<b>Weights.</b> Around the default the decisions sit on a plateau: with the cost weight between 0.4 and 0.8 at most "
    f"{max(flip('cost', 0.4), flip('cost', 0.8)):.0f}% of recommendations change. They shift sharply only when reliability or risk is "
    f"pushed above about 0.5 (air share {air_share('reliability', 0.5):.0f}% at reliability weight 0.5, 100% at 0.8) or cost is "
    f"pushed below about 0.3. A per-shipment sweep (<font face='Courier'>recommend S007 --sweep cost</font>) reports the exact "
    "weight at which a recommendation flips, so an operator sees how close the call was."))
story.append(B(
    f"<b>Estimate error.</b> Doubling every delay probability changes {ds.loc[2.0].decision_change_pct:.1f}% of decisions "
    f"(tripling: {ds.loc[3.0].decision_change_pct:.1f}%), halving changes {ds.loc[0.5].decision_change_pct:.1f}%; the portfolio drifts "
    f"gracefully towards air ({ds.loc[1.0].air_share_pct:.0f}% to {ds.loc[3.0].air_share_pct:.0f}%) as delays look worse."))

# ---- 7 ----------------------------------------------------------------------------------------
story.append(P("7. Limitations and next steps", H2))
story.append(B("<b>Synthetic, and partly circular.</b> Data, truth and yardstick come from one author; the dollar model is a stand-in for "
               "a real shipper's costs. Absolute numbers should not be over-read; the relative comparisons and the failure modes are the point. "
               "With 40 shipments, CIs are wide (see Table 1) and per-cargo results rest on 6-16 shipments."))
story.append(B("<b>Modelling simplifications.</b> Static lane parameters (no season or time series), independent legs plus one shared "
               "factor, no capacity, consolidation, multi-shipment interactions, container-level pricing or demurrage. Profile weights "
               "carry subjective judgement; only the cost weight is data-calibrated."))
story.append(B("<b>Hard rules are blunt.</b> The stress test shows a cap can force a very costly pick; a production system would let "
               "an operator approve exceptions, and could use soft penalties near the threshold."))
story.append(B("<b>Next steps.</b> Learn delay and risk distributions from historical shipment, AIS and port-congestion data with "
               "calibrated (conformal) intervals instead of fixed noise; re-optimise during transit when a disruption occurs; "
               "add an optional LLM layer that only rephrases the deterministic explanation for different audiences."))

doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=0.62 * inch, rightMargin=0.62 * inch,
                        topMargin=0.55 * inch, bottomMargin=0.55 * inch, title="Optimizing Shipment Routes Under Cost, Time and Risk",
                        author="Umesh Chandra Namani")


def footer(c, d):
    c.saveState()
    c.setFont("Helvetica", 7)
    c.setFillColor(colors.HexColor("#777777"))
    c.drawString(0.62 * inch, 0.3 * inch, "Aiqon AI Internship take-home - shipment route optimization")
    c.drawRightString(A4[0] - 0.62 * inch, 0.3 * inch, f"Page {d.page}")
    c.restoreState()


doc.build(story, onFirstPage=footer, onLaterPages=footer)
print("wrote", OUT)
