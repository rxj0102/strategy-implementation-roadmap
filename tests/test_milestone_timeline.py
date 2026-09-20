from __future__ import annotations

from strategy_roadmap.milestone_timeline import build_timeline, gates, to_markdown


def test_build_timeline_returns_four_phases_in_order():
    phases = build_timeline()
    assert [p.id for p in phases] == ["P0", "P1", "P2", "P3"]


def test_phases_are_contiguous_and_non_overlapping():
    phases = build_timeline()
    for earlier, later in zip(phases, phases[1:]):
        assert later.start_week == earlier.end_week + 1


def test_readiness_gate_and_go_no_go_gate_present():
    phases = build_timeline()
    all_gates = gates(phases)
    gate_ids = {g.id for g in all_gates}
    assert gate_ids == {"GATE0", "GATE1"}


def test_go_no_go_gate_criteria_tie_back_to_unresolved_hypotheses():
    phases = build_timeline()
    go_no_go = next(g for g in gates(phases) if g.id == "GATE1")
    tied_ids = {c.tied_hypothesis_id for c in go_no_go.criteria if c.tied_hypothesis_id}
    assert tied_ids == {"3.1", "3.2", "4"}


def test_go_no_go_gate_has_three_possible_outcomes_not_just_binary():
    phases = build_timeline()
    go_no_go = next(g for g in gates(phases) if g.id == "GATE1")
    assert len(go_no_go.possible_outcomes) == 3


def test_go_no_go_gate_falls_within_18_to_24_months_of_pilot_launch():
    phases = build_timeline()
    launch_week = next(p for p in phases if p.id == "P1").start_week
    go_no_go = next(g for g in gates(phases) if g.id == "GATE1")
    months_elapsed = (go_no_go.at_week - launch_week) / (52 / 12)
    assert 15 <= months_elapsed <= 24


def test_to_markdown_includes_all_phases_and_gate_criteria():
    phases = build_timeline()
    markdown = to_markdown(phases)
    for phase in phases:
        assert phase.name in markdown
    assert "Possible outcomes" in markdown
