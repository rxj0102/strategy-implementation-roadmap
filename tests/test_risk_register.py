from __future__ import annotations

import pytest

from strategy_roadmap.risk_register import RiskItem, build_risk_register, to_markdown


def test_build_risk_register_returns_ten_risks_with_unique_ids():
    risks = build_risk_register()
    assert len(risks) == 10
    ids = [r.id for r in risks]
    assert len(ids) == len(set(ids))


def test_score_is_likelihood_times_impact():
    risk = RiskItem(
        id="RX",
        category="Test",
        description="desc",
        workstream_id=None,
        likelihood=3,
        impact=4,
        mitigation="mitigation",
        mitigation_owner_id="MANAGER",
        early_warning_indicator="indicator",
    )
    assert risk.score == 12


@pytest.mark.parametrize(
    "likelihood,impact,expected_band",
    [(1, 1, "Low"), (2, 3, "Medium"), (2, 5, "High"), (5, 5, "Critical")],
)
def test_severity_band_boundaries(likelihood, impact, expected_band):
    risk = RiskItem(
        id="RX",
        category="Test",
        description="desc",
        workstream_id=None,
        likelihood=likelihood,
        impact=impact,
        mitigation="mitigation",
        mitigation_owner_id="MANAGER",
        early_warning_indicator="indicator",
    )
    assert risk.severity_band == expected_band


def test_out_of_range_likelihood_or_impact_raises():
    with pytest.raises(ValueError):
        RiskItem(
            id="RX",
            category="Test",
            description="desc",
            workstream_id=None,
            likelihood=6,
            impact=3,
            mitigation="m",
            mitigation_owner_id="MANAGER",
            early_warning_indicator="i",
        )
    with pytest.raises(ValueError):
        RiskItem(
            id="RX",
            category="Test",
            description="desc",
            workstream_id=None,
            likelihood=3,
            impact=0,
            mitigation="m",
            mitigation_owner_id="MANAGER",
            early_warning_indicator="i",
        )


def test_risks_tied_to_hypotheses_cover_all_three_unresolved_branches():
    risks = build_risk_register()
    tied_ids = {r.tied_hypothesis_id for r in risks if r.tied_hypothesis_id}
    assert tied_ids == {"3.1", "3.2", "4"}


def test_to_markdown_ranks_by_severity_descending():
    risks = build_risk_register()
    markdown = to_markdown(risks)
    lines = [l for l in markdown.splitlines() if l.startswith("| R")]
    scores = [int(line.split("|")[6].strip()) for line in lines]
    assert scores == sorted(scores, reverse=True)
