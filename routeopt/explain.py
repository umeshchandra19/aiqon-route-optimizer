"""Plain-language explanations of a routing decision.

Fully deterministic and template-based (no LLM): every sentence is generated
from numbers in the decision table, so the explanation can never disagree with
the score that produced the recommendation.
"""
from __future__ import annotations

import pandas as pd

from .scoring import CRITERIA, CRITERIA_LABEL, Decision, TIME_COMFORT


def money(x: float) -> str:
    return f"${x:,.0f}"


def pct(x: float) -> str:
    return f"{100 * x:.0f}%"


def share(x: float) -> str:
    """Share of cargo value; one decimal below 10% so small freight bills do not show as 0%."""
    return f"{100 * x:.1f}%" if x < 0.10 else f"{100 * x:.0f}%"


def prob(x: float) -> str:
    """Probability as a percentage, avoiding a misleading '0%' / '100%'."""
    if x < 0.005:
        return "<1%"
    if x > 0.995:
        return ">99%"
    return f"{100 * x:.0f}%"


def _arrow(path: str) -> str:
    return path.replace(" > ", " → ")


def _describe_route(row) -> str:
    return f"{row.route_id} [{row.modes.replace('>', ' → ')}] {_arrow(row.path)}"


def compare(c, o, label: str, value: float) -> str:
    """Sentence comparing chosen route ``c`` against alternative ``o``."""
    worse, better = [], []
    dcost = c.cost_usd - o.cost_usd
    dcost_rel = dcost / max(o.cost_usd, 1e-9)
    if abs(dcost_rel) >= 0.05 and abs(dcost) >= 0.002 * value:
        if dcost > 0:
            mult = f"{1 + dcost_rel:.0f}x the price" if dcost_rel >= 1.0 else f"+{pct(dcost_rel)}"
            worse.append(f"costs {money(dcost)} more ({mult})")
        else:
            better.append(f"saves {money(-dcost)} ({pct(-dcost_rel)})")
    ddays = c.exp_days - o.exp_days
    if abs(ddays) >= 1.0:
        (worse if ddays > 0 else better).append(
            f"arrives {abs(ddays):.0f} days {'later' if ddays > 0 else 'earlier'}")
    ddp = c.delay_prob - o.delay_prob
    if abs(ddp) >= 0.03:
        verb = "raises" if ddp > 0 else "cuts"
        (worse if ddp > 0 else better).append(
            f"{verb} delay probability from {pct(o.delay_prob)} to {pct(c.delay_prob)}")
    dpo = c.p_ontime - o.p_ontime
    if abs(dpo) >= 0.05:
        (better if dpo > 0 else worse).append(
            f"{'raises' if dpo > 0 else 'lowers'} on-time probability from {prob(o.p_ontime)} to {prob(c.p_ontime)}")
    drisk = c.risk_index - o.risk_index
    if abs(drisk) >= 0.08:
        (better if drisk < 0 else worse).append(
            f"carries {'lower' if drisk < 0 else 'higher'} congestion/geopolitical risk "
            f"({c.risk_index:.2f} vs {o.risk_index:.2f})")

    head = f"Versus the {label} ({o.route_id}, {o.family})"
    if worse and better:
        return f"{head}, it {_join(worse)}, but {_join(better)}."
    if better:
        return f"{head}, it {_join(better)}."
    if worse:
        return f"{head}, it {_join(worse)}, but scores better overall on the weighted criteria."
    return f"{head}, it is broadly similar on every metric; the weighted score breaks the tie."


def _join(items):
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def _drawback(o, c, crit: str, value: float, deadline: float) -> str:
    if crit == "cost":
        return (f"freight is {share(o.cost_usd / value)} of cargo value "
                f"({money(o.cost_usd)}) vs {share(c.cost_usd / value)} for the pick")
    if crit == "time":
        return (f"expected arrival uses {pct(o.exp_days / deadline)} of the {deadline:.0f}-day deadline "
                f"vs {pct(c.exp_days / deadline)} for the pick, so the schedule buffer is thinner")
    if crit == "reliability":
        return f"{pct(o.delay_prob)} delay probability vs {pct(c.delay_prob)} for the pick"
    return f"risk index {o.risk_index:.2f} vs {c.risk_index:.2f} for the pick"


def explain(dec: Decision, ship) -> dict:
    df = dec.table
    c = df.loc[dec.chosen]
    value = float(ship["value_usd"])
    deadline = float(ship["deadline_days"])
    others = df.drop(index=dec.chosen)
    feas = df[df["in_pool"]]

    lines = []
    lines.append(f"Shipment {ship['shipment_id']}: {ship['origin_name']} → {ship['destination_name']} | "
                 f"{ship['cargo_type']} | {ship['weight_t']:.1f} t | cargo value {money(value)} | "
                 f"deadline {deadline:.0f} days")
    w = dec.weights
    lines.append("Priorities (" + (f"profile '{dec.profile}'" if dec.profile else "custom") + "): " +
                 ", ".join(f"{k} {pct(w[k])}" for k in CRITERIA) +
                 f". Hard rules: P(on-time) ≥ {pct(dec.constraints.min_ontime)}, "
                 f"geopolitical risk ≤ {dec.constraints.max_geo:.2f}" +
                 (f", excluded modes: {', '.join(dec.constraints.exclude_modes)}" if dec.constraints.exclude_modes else "") + ".")
    lines.append("")
    lines.append(f"RECOMMENDED: {_describe_route(c)}")
    lines.append(f"  cost {money(c.cost_usd)} ({share(c.cost_usd / value)} of cargo value) | expected transit "
                 f"{c.exp_days:.1f} d (P90 {c.p90_days:.1f} d) | delay probability {pct(c.delay_prob)} | "
                 f"P(on-time) {pct(c.p_ontime)} | risk index {c.risk_index:.2f} | score {c.score:.0f}/100")
    if dec.relaxed:
        lines.append(f"  WARNING: {dec.relax_note}")

    # --- why ---------------------------------------------------------------
    lines.append("")
    lines.append("Why this route:")
    alts = feas.drop(index=dec.chosen)
    comparisons = []
    seen = {dec.chosen}
    if len(alts):
        cheapest = alts["cost_usd"].idxmin()
        fastest = alts["exp_days"].idxmin()
        reliable = alts["delay_prob"].idxmin()
        for rid, label in [(cheapest, "cheapest allowed alternative"),
                           (fastest, "fastest allowed alternative"),
                           (dec.runner_up, "runner-up"),
                           (reliable, "most reliable allowed alternative")]:
            if rid is not None and rid not in seen:
                seen.add(rid)
                comparisons.append(compare(c, df.loc[rid], label, value))
    if comparisons:
        for s in comparisons[:3]:
            lines.append(f"  - {s}")
    else:
        lines.append("  - It is the only route that satisfies the hard constraints.")

    if dec.runner_up is not None:
        r = df.loc[dec.runner_up]
        gaps = {k: (r[f"pen_{k}"] - c[f"pen_{k}"]) * dec.weights[k] for k in CRITERIA}
        key = max(gaps, key=gaps.get)
        if gaps[key] > 0.01:
            lines.append(f"  - Deciding factor over the runner-up: {CRITERIA_LABEL[key]} "
                         f"({_drawback(r, c, key, value, deadline)}).")

    # --- price of the hard rules ------------------------------------------------
    if dec.unconstrained_best and dec.unconstrained_best != dec.chosen:
        u = df.loc[dec.unconstrained_best]
        lines.append(f"  - Hard rules changed the outcome: ignoring them, {u.route_id} ({u['family']}) would rank first, "
                     f"but it was ruled out ({u['violations']}). The rules add {money(dec.constraint_premium)} "
                     f"({share(dec.constraint_premium / value)} of cargo value) to freight.")
        if dec.needs_review:
            lines.append("  - REVIEW SUGGESTED: the hard rules force a very expensive option. A planner may prefer to "
                         "relax the on-time or risk rule, renegotiate the deadline, or approve the excluded route.")

    # --- rejected ------------------------------------------------------------
    if len(others):
        lines.append("")
        lines.append("Alternatives not selected:")
        for rid, o in others.iterrows():
            if o["violations"]:
                why = f"excluded - {o['violations']}"
            elif o["dominated"]:
                why = f"dominated by {o['dominated_by']} (no better on any criterion)"
            elif not o["in_pool"]:
                why = "not eligible in this (relaxed) decision"
            else:
                gaps = {k: (o[f"pen_{k}"] - c[f"pen_{k}"]) * dec.weights[k] for k in CRITERIA}
                key = max(gaps, key=gaps.get)
                why = (f"lower overall score ({o['score']:.0f} vs {c['score']:.0f}); main drawback: "
                       f"{_drawback(o, c, key, value, deadline)}")
            lines.append(f"  - {rid} ({o['family']}, {money(o['cost_usd'])}, {o['exp_days']:.0f} d): {why}")

    # --- confidence -----------------------------------------------------------
    lines.append("")
    if dec.stability is not None and dec.runner_up is not None:
        lines.append(f"Confidence: {dec.confidence} - the same route wins in {pct(dec.stability)} of what-if runs "
                     f"(cost ±10%, time ±8%, delay odds ±30%, risk ±0.10, weights jittered); "
                     f"margin over runner-up {dec.margin:.1f} score points.")
    elif dec.stability is not None:
        lines.append(f"Confidence: {dec.confidence}.")

    # --- headline -------------------------------------------------------------
    head = comparisons[0] if comparisons else "Only feasible route."
    headline = f"{dec.chosen} ({c['family']}): " + head.replace("Versus", "versus", 1)
    return {"shipment_id": dec.shipment_id, "recommended_route": dec.chosen, "headline": headline,
            "text": "\n".join(lines)}
