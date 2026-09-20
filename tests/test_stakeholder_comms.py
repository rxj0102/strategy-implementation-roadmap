from __future__ import annotations

import pytest

from strategy_roadmap.case_context import build_case_context
from strategy_roadmap.risk_register import build_risk_register
from strategy_roadmap.stakeholder_comms import (
    LiveSynthesisUnavailable,
    build_change_management_inputs,
    build_communication_plan,
    draft_change_narrative_live,
    draft_change_narrative_template,
    synthesize_change_narrative,
    to_markdown,
)
from strategy_roadmap.workstream_planner import build_workstreams


def test_build_communication_plan_covers_six_distinct_audiences():
    plan = build_communication_plan()
    audiences = {row.audience for row in plan}
    assert len(plan) == 6
    assert len(audiences) == 6


def test_communication_plan_has_at_least_one_daily_and_one_monthly_cadence():
    plan = build_communication_plan()
    frequencies = {row.frequency for row in plan}
    assert "Daily" in frequencies
    assert "Monthly" in frequencies


def test_build_change_management_inputs_references_new_hires_and_friction():
    ctx = build_case_context()
    workstreams = build_workstreams()
    risks = build_risk_register()
    inputs = build_change_management_inputs(ctx, workstreams, risks)
    assert "market lead" in inputs.new_hires_context
    assert "R9" in inputs.friction_points


def test_draft_change_narrative_template_is_deterministic_and_grounded():
    ctx = build_case_context()
    workstreams = build_workstreams()
    risks = build_risk_register()
    inputs = build_change_management_inputs(ctx, workstreams, risks)
    draft_1 = draft_change_narrative_template(inputs)
    draft_2 = draft_change_narrative_template(inputs)
    assert draft_1 == draft_2
    assert "Change Management Narrative" in draft_1


def test_draft_change_narrative_live_raises_without_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    ctx = build_case_context()
    workstreams = build_workstreams()
    risks = build_risk_register()
    inputs = build_change_management_inputs(ctx, workstreams, risks)
    with pytest.raises(LiveSynthesisUnavailable):
        draft_change_narrative_live(inputs)


def test_synthesize_change_narrative_falls_back_to_template_without_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    ctx = build_case_context()
    workstreams = build_workstreams()
    risks = build_risk_register()
    inputs = build_change_management_inputs(ctx, workstreams, risks)
    text, mode = synthesize_change_narrative(inputs)
    assert mode == "template"
    assert text == draft_change_narrative_template(inputs)


def test_to_markdown_renders_all_audiences():
    plan = build_communication_plan()
    markdown = to_markdown(plan)
    for row in plan:
        assert row.audience in markdown
