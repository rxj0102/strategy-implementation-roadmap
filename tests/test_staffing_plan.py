from __future__ import annotations

import pytest

from strategy_roadmap.staffing_plan import (
    StaffingAllocation,
    build_mentorship_plan,
    build_staffing_plan,
    to_markdown,
)


def test_build_staffing_plan_covers_four_seniority_levels():
    staffing = build_staffing_plan()
    seniorities = {s.seniority for s in staffing}
    assert seniorities == {"Partner", "Manager", "Consultant", "Associate Consultant"}


def test_every_allocation_sums_to_100():
    for allocation in build_staffing_plan():
        assert sum(allocation.time_allocation.values()) == 100


def test_every_seniority_level_has_nonzero_mentorship_time():
    for allocation in build_staffing_plan():
        assert allocation.time_allocation["MENTORSHIP"] > 0


def test_allocation_rejects_totals_not_equal_100():
    with pytest.raises(ValueError):
        StaffingAllocation(
            seniority="Test",
            overall_engagement_pct=50,
            time_allocation={
                "WS1": 10, "WS2": 10, "WS3": 10, "WS4": 10, "WS5": 10,
                "GOV": 10, "MENTORSHIP": 10,
            },
        )


def test_allocation_rejects_unknown_category():
    with pytest.raises(ValueError):
        StaffingAllocation(
            seniority="Test",
            overall_engagement_pct=50,
            time_allocation={"NOT_REAL": 100},
        )


def test_allocation_rejects_out_of_range_engagement_pct():
    with pytest.raises(ValueError):
        StaffingAllocation(
            seniority="Test",
            overall_engagement_pct=150,
            time_allocation={
                "WS1": 20, "WS2": 20, "WS3": 20, "WS4": 20, "WS5": 20,
                "GOV": 0, "MENTORSHIP": 0,
            },
        )


def test_partner_is_lightly_staffed_relative_to_consultant():
    staffing = build_staffing_plan()
    by_seniority = {s.seniority: s for s in staffing}
    assert by_seniority["Partner"].overall_engagement_pct < by_seniority["Consultant"].overall_engagement_pct


def test_build_mentorship_plan_starts_at_week_zero_and_is_ordered():
    plan = build_mentorship_plan()
    assert plan[0].week_offset == 0
    weeks = [m.week_offset for m in plan]
    assert weeks == sorted(weeks)


def test_mentorship_plan_extends_beyond_initial_onboarding_burst():
    plan = build_mentorship_plan()
    assert max(m.week_offset for m in plan) >= 12


def test_to_markdown_includes_staffing_and_mentorship_sections():
    staffing = build_staffing_plan()
    mentorship = build_mentorship_plan()
    markdown = to_markdown(staffing, mentorship)
    assert "Staffing Allocation" in markdown
    assert "Onboarding & Mentorship Plan" in markdown
    for allocation in staffing:
        assert allocation.seniority in markdown
    for milestone in mentorship:
        assert milestone.title in markdown
