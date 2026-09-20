from __future__ import annotations

import pytest

from strategy_roadmap.workstream_planner import (
    CyclicDependencyError,
    Workstream,
    build_workstreams,
    compute_waves,
    sequence_workstreams,
    to_markdown,
)


def test_build_workstreams_returns_five_named_streams():
    workstreams = build_workstreams()
    assert len(workstreams) == 5
    names = {ws.name for ws in workstreams}
    assert names == {
        "Regulatory & Licensing",
        "Fulfillment Infrastructure",
        "Local Hiring & Talent",
        "Technology Integration",
        "Marketing Launch",
    }


def test_all_dependency_ids_reference_real_workstreams():
    workstreams = build_workstreams()
    ids = {ws.id for ws in workstreams}
    for ws in workstreams:
        for dep_id in ws.dependencies:
            assert dep_id in ids


def test_sequence_workstreams_respects_dependencies():
    workstreams = build_workstreams()
    sequenced = sequence_workstreams(workstreams)
    position = {ws.id: i for i, ws in enumerate(sequenced)}
    for ws in workstreams:
        for dep_id in ws.dependencies:
            assert position[dep_id] < position[ws.id]


def test_regulatory_licensing_has_no_dependencies_and_comes_first():
    workstreams = build_workstreams()
    sequenced = sequence_workstreams(workstreams)
    assert sequenced[0].id == "WS1"
    assert sequenced[0].dependencies == ()


def test_marketing_launch_depends_on_fulfillment_hiring_and_tech():
    workstreams = build_workstreams()
    marketing = next(ws for ws in workstreams if ws.id == "WS5")
    assert set(marketing.dependencies) == {"WS2", "WS3", "WS4"}


def test_compute_waves_assigns_zero_to_root_and_increments_downstream():
    workstreams = build_workstreams()
    waves = compute_waves(workstreams)
    assert waves["WS1"] == 0
    assert waves["WS2"] == 1
    assert waves["WS3"] == 1
    assert waves["WS4"] == 1
    assert waves["WS5"] == 2


def test_sequence_workstreams_raises_on_cycle():
    a = Workstream("A", "A", "desc", "owner", dependencies=("B",), key_deliverables=())
    b = Workstream("B", "B", "desc", "owner", dependencies=("A",), key_deliverables=())
    with pytest.raises(CyclicDependencyError):
        sequence_workstreams([a, b])


def test_to_markdown_includes_every_workstream_and_hypothesis_link():
    workstreams = build_workstreams()
    markdown = to_markdown(workstreams)
    for ws in workstreams:
        assert ws.name in markdown
    assert "3.1" in markdown
    assert "3.2" in markdown
