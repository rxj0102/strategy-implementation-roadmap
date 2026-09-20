from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

from strategy_roadmap.roadmap_synthesis import (
    build_roadmap_bundle,
    generate_roadmap,
    render_roadmap_markdown,
    save_exhibits,
)


def test_build_roadmap_bundle_runs_without_live_llm():
    bundle = build_roadmap_bundle(use_live_llm=False)
    assert bundle.change_narrative_mode == "template"
    assert len(bundle.workstreams) == 5
    assert len(bundle.risks) == 10
    assert len(bundle.phases) == 4


def test_render_roadmap_markdown_includes_every_section():
    bundle = build_roadmap_bundle(use_live_llm=False)
    markdown = render_roadmap_markdown(bundle)
    assert "# Implementation Roadmap" in markdown
    assert "## Workstream Plan" in markdown
    assert "## RACI Matrix" in markdown
    assert "## Milestone Timeline" in markdown
    assert "## Implementation Risk Register" in markdown
    assert "## Stakeholder Communication Plan" in markdown
    assert "## Change Management Narrative" in markdown
    assert "## Team Staffing & Mentorship Plan" in markdown
    assert "market-entry-case-toolkit" in markdown


def test_render_roadmap_markdown_embeds_all_three_exhibits():
    bundle = build_roadmap_bundle(use_live_llm=False)
    markdown = render_roadmap_markdown(bundle)
    assert "exhibits/gantt_timeline.png" in markdown
    assert "exhibits/raci_heatmap.png" in markdown
    assert "exhibits/risk_heatmap.png" in markdown


def test_save_exhibits_writes_three_png_files(tmp_path):
    bundle = build_roadmap_bundle(use_live_llm=False)
    paths = save_exhibits(bundle, tmp_path / "exhibits")
    assert set(paths) == {"gantt", "raci", "risk"}
    for path in paths.values():
        assert path.exists()
        assert path.stat().st_size > 0


def test_generate_roadmap_writes_markdown_and_exhibits(tmp_path):
    doc_path = generate_roadmap(tmp_path, use_live_llm=False)
    assert doc_path.exists()
    assert (tmp_path / "exhibits" / "gantt_timeline.png").exists()
    assert (tmp_path / "exhibits" / "raci_heatmap.png").exists()
    assert (tmp_path / "exhibits" / "risk_heatmap.png").exists()
