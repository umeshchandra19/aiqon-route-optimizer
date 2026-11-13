import numpy as np
import pytest

from routeopt.explain import explain
from routeopt.generate_data import generate
from routeopt.model import apply_scenario, load_dataset
from routeopt.network import enumerate_paths
from routeopt.scoring import (CRITERIA, PROFILES, Constraints, compute_metrics, decide,
                              normalise_weights, penalty_matrix, recommend)
from routeopt.sensitivity import reweight, weight_sweep_one
from routeopt.simulate import analytic_summary, route_seed, simulate_transit


@pytest.fixture(scope="module")
def data(tmp_path_factory):
    d = tmp_path_factory.mktemp("data")
    generate(16, seed=3, out_dir=d)
    ships, routes = load_dataset(d)
    return ships, routes, d


def test_paths_are_simple_and_bounded():
    paths = enumerate_paths("SHA", "RTM", max_legs=4)
    assert paths
    for p in paths:
        nodes = [p[0][0]] + [t for _, t, _ in p]
        assert nodes[0] == "SHA" and nodes[-1] == "RTM"
        assert len(set(nodes)) == len(nodes) and len(p) <= 4


def test_dataset_shape_and_determinism(data, tmp_path):
    ships, routes, _ = data
    assert len(ships) == 16
    for sid, rs in routes.items():
        assert 3 <= len(rs) <= 5
        for r in rs:
            assert (r.p >= 0).all() and (r.p <= 1).all() and (r.cost > 0).all()
    generate(16, seed=3, out_dir=tmp_path)
    s2, _ = load_dataset(tmp_path)
    assert s2["deadline_days"].tolist() == ships["deadline_days"].tolist()


def test_monte_carlo_matches_analytic(data):
    _, routes, _ = data
    r = next(iter(routes.values()))[0]
    T = simulate_transit(r, 60000, np.random.default_rng(1))
    assert abs(T.mean() - analytic_summary(r)["exp_days_analytic"]) < 0.5


def test_penalties_in_unit_interval_and_monotone():
    P = penalty_matrix(np.array([1000, 5000]), np.array([10, 30]), np.array([.1, .4]), np.array([.2, .8]), 50000, 40)
    assert (P >= 0).all() and (P <= 1).all()
    assert (P[1] >= P[0]).all()


def test_weights_normalise():
    w = normalise_weights({"cost": 2, "time": 1, "reliability": 1})
    assert abs(sum(w.values()) - 1) < 1e-9 and w["risk"] == 0
    with pytest.raises(ValueError):
        normalise_weights({"cost": -1})


def test_recommendation_is_feasible_and_explained(data):
    ships, routes, _ = data
    for sid in ships.index:
        ship = ships.loc[sid]
        d = recommend(ship, routes[sid], robustness_draws=50)
        row = d.table.loc[d.chosen]
        assert d.relaxed or row.feasible
        text = explain(d, ship)["text"]
        assert d.chosen in text and "Why this route" in text


def test_mode_exclusion_respected(data):
    ships, routes, _ = data
    sid = ships.index[0]
    d = recommend(ships.loc[sid], routes[sid], exclude_modes=("air",), robustness_draws=0)
    assert "air" not in d.table.loc[d.chosen, "modes"]


def test_cost_only_weight_picks_cheapest_in_pool(data):
    ships, routes, _ = data
    sid = ships.index[1]
    ship = ships.loc[sid]
    t = compute_metrics(routes[sid], ship)
    d = decide(t, {"cost": 1.0}, Constraints(), float(ship.value_usd), float(ship.deadline_days), sid, 0)
    assert d.chosen == t["cost_usd"].idxmin()


def test_high_value_geo_cap_excludes_red_sea(data):
    ships, routes, _ = data
    for sid in ships.index:
        d = recommend(ships.loc[sid], routes[sid], profile="high_value", robustness_draws=0)
        if not d.relaxed:
            assert d.table.loc[d.chosen, "geo"] <= PROFILES["high_value"].max_geo + 1e-9


def test_relaxed_mode_when_deadline_impossible(data):
    ships, routes, _ = data
    sid = ships.index[0]
    ship = ships.loc[sid].copy()
    ship["deadline_days"] = 0.5
    d = recommend(ship, routes[sid], exclude_modes=("air",), robustness_draws=0)
    assert d.relaxed and "No route meets" in d.relax_note


def test_pareto_dominated_flag_consistent(data):
    ships, routes, _ = data
    sid = ships.index[2]
    d = recommend(ships.loc[sid], routes[sid], robustness_draws=0)
    assert not d.table.loc[d.chosen, "dominated"]


def test_scenario_increases_risk(data):
    _, routes, _ = data
    for rs in routes.values():
        for r in rs:
            if "red_sea" in r.corridors:
                r2 = apply_scenario(r, "red_sea")
                assert (r2.p >= r.p).all() and r2.geo.max() >= 0.95
                return
    pytest.skip("no red-sea route in this small dataset")


def test_weight_sweep_endpoints(data):
    ships, routes, _ = data
    sid = ships.index[3]
    ship = ships.loc[sid]
    t = compute_metrics(routes[sid], ship)
    sw = weight_sweep_one(t, ship, "cost", steps=5)
    assert len(sw) == 5 and sw.iloc[-1]["weight"] == 1.0
    assert abs(sum(reweight(PROFILES["standard"].weights, "time", 0.3).values()) - 1) < 1e-9
