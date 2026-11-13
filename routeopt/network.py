"""Synthetic global logistics network.

The network is a small, hand-built graph of ports / hubs connected by *lanes*
(edges).  Every lane has a mode (sea / air / rail / road) and *base* parameters
for cost, transit time, delay behaviour and risk.  Individual shipments see
noisy, shipment-specific realisations of these base parameters (see
``generate_data.py``).

The numbers are stylised but chosen to be roughly realistic in *ratio*:
air is ~20x the cost of sea per tonne but 10x faster, transpacific lanes are
congested, the Red Sea / Suez corridor carries high geopolitical risk, etc.
"""
from __future__ import annotations

from dataclasses import dataclass

NODES = {
    "SHA": "Shanghai",
    "SZX": "Shenzhen",
    "SIN": "Singapore",
    "NSA": "Nhava Sheva (Mumbai)",
    "CMB": "Colombo",
    "SUZ": "Suez / Red Sea gateway",
    "PIR": "Piraeus",
    "RTM": "Rotterdam",
    "HAM": "Hamburg",
    "CPT": "Cape Town",
    "PAN": "Panama Canal",
    "LAX": "Los Angeles / Long Beach",
    "NYC": "New York / New Jersey",
}

ORIGINS = ["SHA", "SZX", "NSA", "SIN"]
DESTINATIONS = ["RTM", "HAM", "NYC", "LAX"]

# Dwell (transshipment) time in days and handling cost in USD per tonne,
# applied at every *intermediate* node, by the mode of the arriving leg.
DWELL_DAYS = {"sea": 2.0, "air": 0.7, "rail": 1.5, "road": 0.5}
HANDLING_PER_T = {"sea": 14.0, "air": 60.0, "rail": 20.0, "road": 10.0}


@dataclass(frozen=True)
class Edge:
    idx: int
    a: str
    b: str
    mode: str
    cost_per_t: float   # USD per tonne
    days: float         # nominal transit days (excl. dwell)
    delay_p: float      # probability this leg is delayed
    delay_mean: float   # mean extra days if delayed (exponential)
    congestion: float   # 0..1
    geo: float          # 0..1 geopolitical / security risk
    corridor: str = ""  # tag used by disruption scenarios


# (a, b, mode, cost_per_t, days, delay_p, delay_mean, congestion, geo, corridor)
_RAW = [
    # --- sea: Asia feeder / hub lanes
    ("SHA", "SIN", "sea", 40, 6, .08, 2.0, .45, .10, ""),
    ("SZX", "SIN", "sea", 35, 4, .07, 2.0, .40, .10, ""),
    ("SIN", "CMB", "sea", 35, 4, .06, 1.5, .30, .10, ""),
    ("NSA", "CMB", "sea", 30, 4, .05, 1.5, .30, .10, ""),
    ("NSA", "SIN", "sea", 45, 7, .07, 2.0, .35, .10, ""),
    # --- sea: Red Sea / Suez entry lanes (high geopolitical risk)
    ("CMB", "SUZ", "sea", 40, 8, .14, 3.0, .35, .75, "red_sea"),
    ("NSA", "SUZ", "sea", 50, 9, .14, 3.0, .35, .75, "red_sea"),
    ("SIN", "SUZ", "sea", 60, 12, .14, 3.0, .40, .75, "red_sea"),
    # --- sea: Mediterranean / Europe side
    ("SUZ", "PIR", "sea", 25, 4, .07, 1.5, .30, .15, ""),
    ("SUZ", "RTM", "sea", 55, 9, .10, 2.0, .35, .20, ""),
    ("PIR", "RTM", "sea", 30, 6, .08, 2.0, .40, .10, ""),
    ("PIR", "HAM", "sea", 40, 8, .08, 2.0, .35, .10, ""),
    # --- sea: Atlantic
    ("RTM", "NYC", "sea", 55, 10, .10, 3.0, .40, .05, ""),
    ("HAM", "NYC", "sea", 55, 11, .10, 3.0, .40, .05, ""),
    # --- sea: Cape of Good Hope (long but safe)
    ("CMB", "CPT", "sea", 70, 12, .10, 3.0, .25, .10, ""),
    ("CPT", "RTM", "sea", 75, 15, .10, 3.0, .25, .10, ""),
    ("CPT", "NYC", "sea", 80, 16, .09, 3.0, .25, .05, ""),
    # --- sea: transpacific (congested US west coast)
    ("SHA", "LAX", "sea", 110, 14, .14, 3.0, .70, .10, "lax"),
    ("SZX", "LAX", "sea", 115, 15, .14, 3.0, .70, .10, "lax"),
    ("SIN", "LAX", "sea", 130, 18, .15, 3.0, .65, .10, "lax"),
    # --- sea: Panama
    ("SHA", "PAN", "sea", 130, 22, .10, 3.0, .35, .15, ""),
    ("SZX", "PAN", "sea", 135, 23, .10, 3.0, .35, .15, ""),
    ("SIN", "PAN", "sea", 150, 26, .10, 3.0, .30, .15, ""),
    ("PAN", "NYC", "sea", 40, 5, .10, 2.0, .40, .05, ""),
    ("PAN", "RTM", "sea", 60, 13, .08, 2.0, .35, .10, ""),
    # --- rail / road
    ("LAX", "NYC", "rail", 120, 6, .12, 2.0, .55, .05, "lax"),
    ("RTM", "HAM", "road", 25, 1.5, .06, 1.0, .50, .05, ""),
    ("SHA", "HAM", "rail", 450, 18, .12, 4.0, .55, .55, "eurasia_rail"),
    ("SZX", "HAM", "rail", 460, 19, .12, 4.0, .55, .55, "eurasia_rail"),
    # --- air (fast, expensive, fairly reliable)
    ("SHA", "RTM", "air", 3200, 2.0, .05, 1.0, .45, .10, ""),
    ("SHA", "HAM", "air", 3250, 2.0, .05, 1.0, .45, .10, ""),
    ("SHA", "NYC", "air", 3000, 2.0, .05, 1.0, .45, .10, ""),
    ("SHA", "LAX", "air", 2800, 1.5, .05, 1.0, .45, .10, ""),
    ("SZX", "RTM", "air", 3250, 2.0, .05, 1.0, .40, .10, ""),
    ("SZX", "HAM", "air", 3300, 2.0, .05, 1.0, .40, .10, ""),
    ("SZX", "NYC", "air", 3100, 2.2, .05, 1.0, .40, .10, ""),
    ("SZX", "LAX", "air", 2850, 1.6, .05, 1.0, .40, .10, ""),
    ("NSA", "RTM", "air", 3000, 2.2, .06, 1.0, .35, .10, ""),
    ("NSA", "HAM", "air", 3050, 2.3, .06, 1.0, .35, .10, ""),
    ("NSA", "NYC", "air", 3300, 2.8, .06, 1.0, .35, .10, ""),
    ("NSA", "LAX", "air", 3500, 3.0, .06, 1.0, .35, .10, ""),
    ("SIN", "RTM", "air", 3100, 2.1, .05, 1.0, .30, .08, ""),
    ("SIN", "HAM", "air", 3150, 2.2, .05, 1.0, .30, .08, ""),
    ("SIN", "NYC", "air", 3400, 2.8, .05, 1.0, .30, .08, ""),
    ("SIN", "LAX", "air", 3100, 2.4, .05, 1.0, .30, .08, ""),
]

EDGES = [Edge(i, *row) for i, row in enumerate(_RAW)]
EDGE_BY_IDX = {e.idx: e for e in EDGES}


def adjacency():
    adj: dict[str, list[tuple[str, Edge]]] = {n: [] for n in NODES}
    for e in EDGES:
        adj[e.a].append((e.b, e))
        adj[e.b].append((e.a, e))
    return adj


def enumerate_paths(origin: str, destination: str, max_legs: int = 4):
    """All simple (node-disjoint) paths with at most ``max_legs`` legs.

    Returns a list of paths; a path is a list of ``(from_node, to_node, Edge)``.
    """
    adj = adjacency()
    out = []

    def dfs(node, visited, path):
        if len(path) > max_legs:
            return
        if node == destination and path:
            out.append(list(path))
            return
        if len(path) == max_legs:
            return
        for nxt, e in adj[node]:
            if nxt in visited:
                continue
            path.append((node, nxt, e))
            visited.add(nxt)
            dfs(nxt, visited, path)
            visited.discard(nxt)
            path.pop()

    dfs(origin, {origin}, [])
    return out
