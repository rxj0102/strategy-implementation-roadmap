from __future__ import annotations

import pytest

from strategy_roadmap.raci_builder import (
    InvalidRaciRowError,
    RaciRole,
    RaciRow,
    build_case_raci,
    build_stakeholders,
    to_markdown,
)
from strategy_roadmap.workstream_planner import build_workstreams


def test_build_stakeholders_covers_client_and_case_team():
    stakeholders = build_stakeholders()
    orgs = {s.org for s in stakeholders}
    assert orgs == {"client", "case_team"}
    seniorities = {s.seniority for s in stakeholders if s.org == "case_team"}
    assert seniorities == {"Partner", "Manager", "Consultant", "Associate Consultant"}


def test_build_case_raci_has_one_row_per_workstream_plus_governance():
    workstreams = build_workstreams()
    matrix = build_case_raci(workstreams)
    row_ids = {row.row_id for row in matrix.rows}
    assert row_ids == {ws.id for ws in workstreams} | {"GOV"}


def test_every_row_has_exactly_one_accountable_stakeholder():
    workstreams = build_workstreams()
    matrix = build_case_raci(workstreams)
    for row in matrix.rows:
        accountable = [
            sid for sid, role in row.assignments.items() if role == RaciRole.ACCOUNTABLE
        ]
        assert len(accountable) == 1, f"row {row.row_id} has {len(accountable)} A's"


def test_every_row_assigns_every_stakeholder():
    workstreams = build_workstreams()
    matrix = build_case_raci(workstreams)
    stakeholder_ids = {s.id for s in matrix.stakeholders}
    for row in matrix.rows:
        assert set(row.assignments) == stakeholder_ids


def test_governance_row_is_accountable_to_sponsor():
    workstreams = build_workstreams()
    matrix = build_case_raci(workstreams)
    gov_row = next(row for row in matrix.rows if row.row_id == "GOV")
    assert gov_row.assignments["SPONSOR"] == RaciRole.ACCOUNTABLE


def test_validate_row_rejects_zero_accountable():
    stakeholders = build_stakeholders()
    stakeholder_ids = {s.id for s in stakeholders}
    from strategy_roadmap.raci_builder import _validate_row

    bad_row = RaciRow(
        row_id="BAD",
        row_label="Bad row",
        assignments={sid: RaciRole.INFORMED for sid in stakeholder_ids},
    )
    with pytest.raises(InvalidRaciRowError):
        _validate_row(bad_row, stakeholder_ids)


def test_validate_row_rejects_two_accountable():
    stakeholders = build_stakeholders()
    stakeholder_ids = {s.id for s in stakeholders}
    from strategy_roadmap.raci_builder import _validate_row

    assignments = {sid: RaciRole.INFORMED for sid in stakeholder_ids}
    ids = list(stakeholder_ids)
    assignments[ids[0]] = RaciRole.ACCOUNTABLE
    assignments[ids[1]] = RaciRole.ACCOUNTABLE
    bad_row = RaciRow(row_id="BAD", row_label="Bad row", assignments=assignments)
    with pytest.raises(InvalidRaciRowError):
        _validate_row(bad_row, stakeholder_ids)


def test_validate_row_rejects_unknown_stakeholder_id():
    stakeholders = build_stakeholders()
    stakeholder_ids = {s.id for s in stakeholders}
    from strategy_roadmap.raci_builder import _validate_row

    assignments = {sid: RaciRole.INFORMED for sid in stakeholder_ids}
    assignments["NOT_REAL"] = RaciRole.ACCOUNTABLE
    bad_row = RaciRow(row_id="BAD", row_label="Bad row", assignments=assignments)
    with pytest.raises(InvalidRaciRowError):
        _validate_row(bad_row, stakeholder_ids)


def test_to_markdown_renders_table_with_legend():
    workstreams = build_workstreams()
    matrix = build_case_raci(workstreams)
    markdown = to_markdown(matrix)
    assert "| Workstream |" in markdown
    assert "**Legend:**" in markdown
    for ws in workstreams:
        assert ws.name in markdown
