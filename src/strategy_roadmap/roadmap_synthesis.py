"""Assembles every module's output into the single implementation
roadmap document a case team would actually leave with a client.

This is the "Output" step of the methodology: workstream plan + RACI +
gated timeline + risk register + stakeholder comms/change management +
staffing/mentorship plan, combined into one coherent deliverable with
three embedded exhibits (Gantt timeline, RACI heatmap, risk heat map).
Analogous in spirit to `market_entry_toolkit.memo_synthesis`, but there
is no LLM step at this top level -- the one LLM-assisted piece already
lives in `stakeholder_comms.synthesize_change_narrative()`; this module
just assembles structured markdown deterministically.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from strategy_roadmap import (
    case_context as case_context_module,
)
from strategy_roadmap import (
    milestone_timeline,
    raci_builder,
    risk_register,
    staffing_plan,
    stakeholder_comms,
    workstream_planner,
)
from strategy_roadmap._viz import (
    plot_gantt_timeline,
    plot_raci_heatmap,
    plot_risk_heatmap,
)
from strategy_roadmap.case_context import CaseContext
from strategy_roadmap.milestone_timeline import Phase
from strategy_roadmap.raci_builder import RaciMatrix
from strategy_roadmap.risk_register import RiskItem
from strategy_roadmap.staffing_plan import OnboardingMilestone, StaffingAllocation
from strategy_roadmap.stakeholder_comms import CommunicationPlanRow
from strategy_roadmap.workstream_planner import Workstream


@dataclass(frozen=True)
class RoadmapBundle:
    """Every structured input the final roadmap document is built from,
    computed once so the notebook, the markdown renderer, and the
    exhibit generator all work from the same objects."""

    case: CaseContext
    workstreams: list[Workstream]
    raci_matrix: RaciMatrix
    phases: list[Phase]
    risks: list[RiskItem]
    comms_plan: list[CommunicationPlanRow]
    change_narrative: str
    change_narrative_mode: str
    staffing: list[StaffingAllocation]
    mentorship: list[OnboardingMilestone]


def build_roadmap_bundle(use_live_llm: bool | None = None) -> RoadmapBundle:
    """Run every module and assemble a `RoadmapBundle`.

    Args:
        use_live_llm: passed through to
            `stakeholder_comms.synthesize_change_narrative()` --
            None auto-detects `ANTHROPIC_API_KEY`, True/False forces a
            mode.
    """
    case = case_context_module.build_case_context()
    workstreams = workstream_planner.build_workstreams()
    raci_matrix = raci_builder.build_case_raci(workstreams)
    phases = milestone_timeline.build_timeline()
    risks = risk_register.build_risk_register()
    comms_plan = stakeholder_comms.build_communication_plan()

    change_inputs = stakeholder_comms.build_change_management_inputs(
        case, workstreams, risks
    )
    change_narrative, change_mode = stakeholder_comms.synthesize_change_narrative(
        change_inputs, use_live_llm=use_live_llm
    )

    staffing = staffing_plan.build_staffing_plan()
    mentorship = staffing_plan.build_mentorship_plan()

    return RoadmapBundle(
        case=case,
        workstreams=workstreams,
        raci_matrix=raci_matrix,
        phases=phases,
        risks=risks,
        comms_plan=comms_plan,
        change_narrative=change_narrative,
        change_narrative_mode=change_mode,
        staffing=staffing,
        mentorship=mentorship,
    )


def save_exhibits(bundle: RoadmapBundle, exhibits_dir: Path) -> dict[str, Path]:
    """Render and save the three exhibit PNGs. Returns a dict of exhibit
    name -> saved path."""
    exhibits_dir.mkdir(parents=True, exist_ok=True)

    paths: dict[str, Path] = {}

    gantt_fig = plot_gantt_timeline(bundle.phases)
    gantt_path = exhibits_dir / "gantt_timeline.png"
    gantt_fig.savefig(gantt_path)
    paths["gantt"] = gantt_path

    raci_fig = plot_raci_heatmap(bundle.raci_matrix)
    raci_path = exhibits_dir / "raci_heatmap.png"
    raci_fig.savefig(raci_path)
    paths["raci"] = raci_path

    risk_fig = plot_risk_heatmap(bundle.risks)
    risk_path = exhibits_dir / "risk_heatmap.png"
    risk_fig.savefig(risk_path)
    paths["risk"] = risk_path

    return paths


def render_roadmap_markdown(bundle: RoadmapBundle) -> str:
    """Render the full implementation roadmap document as markdown,
    with the three exhibits embedded by relative path."""
    case = bundle.case
    unresolved_bullets = "\n".join(
        f"- **[{h.id}]** {h.statement} -- *{h.original_verdict}*. "
        f"The pilot must prove: {h.what_the_pilot_must_prove}"
        for h in case.unresolved_hypotheses
    )

    sections = [
        f"# Implementation Roadmap: {case.client_name} GTA Pilot",
        "",
        (
            f"**Carried forward from the original case:** {case.original_recommendation}"
        ),
        "",
        (
            "This document is the implementation-planning layer that follows "
            "the [market-entry-case-toolkit](https://github.com/rxj0102/"
            "market-entry-case-toolkit)'s recommendation memo -- it does not "
            "re-run the market analysis. It takes the conditional-go decision "
            "as given and builds the workstream plan, RACI matrix, gated "
            "timeline, risk register, stakeholder communications, and staffing "
            "plan a case team delivers next."
        ),
        "",
        "## Unresolved Hypotheses This Pilot Must Close",
        "",
        unresolved_bullets,
        "",
        workstream_planner.to_markdown(bundle.workstreams),
        raci_builder.to_markdown(bundle.raci_matrix),
        "",
        "![RACI matrix](exhibits/raci_heatmap.png)",
        "",
        milestone_timeline.to_markdown(bundle.phases),
        "![Implementation timeline](exhibits/gantt_timeline.png)",
        "",
        risk_register.to_markdown(bundle.risks),
        "",
        "![Risk heat map](exhibits/risk_heatmap.png)",
        "",
        stakeholder_comms.to_markdown(bundle.comms_plan),
        bundle.change_narrative,
        "",
        staffing_plan.to_markdown(bundle.staffing, bundle.mentorship),
        "---",
        (
            f"*Change-management narrative generated in **{bundle.change_narrative_mode}** "
            "mode -- see `stakeholder_comms.py`. All names, figures, and dates "
            "in this document are illustrative, hand-set proxies for a "
            "portfolio case study, not real client data. See the README for "
            "the full disclaimer.*"
        ),
    ]
    return "\n".join(sections) + "\n"


def generate_roadmap(
    output_dir: Path | str = "outputs", use_live_llm: bool | None = None
) -> Path:
    """Top-level entry point: build the bundle, save the exhibits, write
    the final markdown document, return its path."""
    output_dir = Path(output_dir)
    bundle = build_roadmap_bundle(use_live_llm=use_live_llm)
    save_exhibits(bundle, output_dir / "exhibits")
    markdown = render_roadmap_markdown(bundle)
    doc_path = output_dir / "implementation_roadmap.md"
    doc_path.write_text(markdown)
    return doc_path
