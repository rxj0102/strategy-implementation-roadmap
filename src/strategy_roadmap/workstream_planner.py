"""Workstream decomposition for the FreshRoute GTA pilot implementation.

A recommendation memo says *what* to do ("conditional go via a
milestone-gated pilot"). This module does what a real case team does
next: break that recommendation into the discrete, owned, sequenced
workstreams an execution team actually staffs and runs. Each workstream
optionally links back to the specific unresolved hypothesis
(`case_context.UnresolvedHypothesis`) it exists to close, so the
implementation plan reads as a direct continuation of the original case
rather than a generic project plan.

This is a plain data structure (dataclasses + a dependency graph), no
external dependencies -- consistent with the sibling toolkit's
`hypothesis_tree.py`, which keeps the structural logic of a case fully
transparent and unit-testable rather than hidden inside prose.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Workstream:
    """A single implementation workstream.

    Attributes:
        id: Short stable identifier (e.g. "WS1") used for cross-referencing
            from the RACI matrix, timeline, risk register, and staffing plan.
        name: Short workstream name (e.g. "Regulatory & Licensing").
        description: What this workstream is responsible for delivering.
        owner_role: The role accountable for this workstream's delivery
            (e.g. "Fulfillment Lead (client)"). This is a role, not a named
            person -- the RACI matrix assigns the actual R/A/C/I across the
            full stakeholder set.
        dependencies: Ids of workstreams that must reach their key
            deliverables before this one can start in earnest. Used by
            `sequence_workstreams()` to compute execution order.
        key_deliverables: The concrete outputs this workstream must produce.
        resolves_hypothesis_id: Optional id (e.g. "3.1") of the
            `case_context.UnresolvedHypothesis` this workstream exists to
            close, if any. Not every workstream resolves an original
            hypothesis -- marketing launch, for instance, is net-new
            execution work rather than de-risking an open question.
    """

    id: str
    name: str
    description: str
    owner_role: str
    dependencies: tuple[str, ...]
    key_deliverables: tuple[str, ...]
    resolves_hypothesis_id: str | None = None


class CyclicDependencyError(ValueError):
    """Raised when workstream dependencies contain a cycle."""


def build_workstreams() -> list[Workstream]:
    """Decompose the FreshRoute GTA pilot into its five workstreams.

    Sequencing logic, at a glance: regulatory/licensing and fulfillment
    infrastructure are the critical path (nothing else can safely launch
    in-market before a business can legally operate and has somewhere to
    fulfill orders from); local hiring and technology integration can run
    in parallel once regulatory clearance is underway; marketing launch is
    deliberately last, since spending customer-acquisition dollars before
    the fulfillment model is proven would burn the exact CAC assumption
    (case_context hypothesis 4) the pilot exists to test cleanly.
    """

    regulatory_licensing = Workstream(
        id="WS1",
        name="Regulatory & Licensing",
        description=(
            "Obtain the business licenses, tax registrations, and "
            "compliance clearances required to operate a grocery-delivery "
            "business in Ontario, and confirm cross-border data handling "
            "meets FreshRoute's existing compliance posture."
        ),
        owner_role="Regulatory & Compliance Lead (client)",
        dependencies=(),
        key_deliverables=(
            "Ontario business license and GST/HST registration secured",
            "Cross-border data-handling review signed off by client legal",
            "Employment-standards compliance review for Ontario hires",
        ),
        resolves_hypothesis_id="3.2",
    )

    fulfillment_infrastructure = Workstream(
        id="WS2",
        name="Fulfillment Infrastructure",
        description=(
            "Stand up partner-store picking agreements and a third-party "
            "last-mile courier network for the single pilot zone -- "
            "deliberately capital-light, no new owned warehouse."
        ),
        owner_role="Fulfillment Lead (client)",
        dependencies=("WS1",),
        key_deliverables=(
            "Signed partner-store picking agreements covering the pilot zone",
            "Contracted last-mile courier network with agreed SLAs",
            "Pilot-zone fulfillment cost-per-order baseline established",
        ),
        resolves_hypothesis_id="3.1",
    )

    local_hiring = Workstream(
        id="WS3",
        name="Local Hiring & Talent",
        description=(
            "Recruit and onboard the pilot-zone operations team: local "
            "market lead, courier-network coordinator, and customer "
            "support staff, under Ontario employment law."
        ),
        owner_role="HR / Local Operations Lead (client)",
        dependencies=("WS1",),
        key_deliverables=(
            "Pilot-zone operations team hired and onboarded",
            "Local market lead in place ahead of pilot launch",
        ),
        resolves_hypothesis_id="3.2",
    )

    technology_integration = Workstream(
        id="WS4",
        name="Technology Integration",
        description=(
            "Adapt FreshRoute's existing US ordering, routing, and payments "
            "platform for the Canadian market: currency, tax calculation, "
            "payments rails, and partner-store inventory integration."
        ),
        owner_role="Technology Integration Lead (client)",
        dependencies=("WS1",),
        key_deliverables=(
            "Platform localized for CAD pricing, GST/HST tax calculation, "
            "and Canadian payments rails",
            "Partner-store inventory feed integrated for the pilot zone",
        ),
        resolves_hypothesis_id=None,
    )

    marketing_launch = Workstream(
        id="WS5",
        name="Marketing Launch",
        description=(
            "Design and execute a pilot-zone customer-acquisition campaign "
            "sized to test CAC assumptions cleanly, not to maximize volume."
        ),
        owner_role="Marketing Lead (client)",
        dependencies=("WS2", "WS3", "WS4"),
        key_deliverables=(
            "Pilot-zone launch campaign live",
            "CAC-by-channel tracking in place from day one of the pilot",
        ),
        resolves_hypothesis_id="4",
    )

    return [
        regulatory_licensing,
        fulfillment_infrastructure,
        local_hiring,
        technology_integration,
        marketing_launch,
    ]


def sequence_workstreams(workstreams: list[Workstream]) -> list[Workstream]:
    """Return workstreams in dependency order (a topological sort).

    Raises:
        CyclicDependencyError: if the dependency graph contains a cycle.
    """
    by_id = {ws.id: ws for ws in workstreams}
    resolved: list[Workstream] = []
    resolved_ids: set[str] = set()
    visiting: set[str] = set()

    def visit(ws: Workstream) -> None:
        if ws.id in resolved_ids:
            return
        if ws.id in visiting:
            raise CyclicDependencyError(
                f"Cyclic dependency detected involving workstream '{ws.id}'"
            )
        visiting.add(ws.id)
        for dep_id in ws.dependencies:
            visit(by_id[dep_id])
        visiting.remove(ws.id)
        resolved.append(ws)
        resolved_ids.add(ws.id)

    for ws in workstreams:
        visit(ws)
    return resolved


def compute_waves(workstreams: list[Workstream]) -> dict[str, int]:
    """Compute each workstream's execution "wave" (0-indexed).

    A workstream's wave is one more than the maximum wave of its
    dependencies (0 if it has none) -- workstreams in the same wave have
    no dependency relationship between them and can run in parallel. This
    is what lets a staffing plan claim two workstreams can be resourced
    concurrently rather than sequentially.
    """
    by_id = {ws.id: ws for ws in workstreams}
    waves: dict[str, int] = {}

    def wave_of(ws_id: str) -> int:
        if ws_id in waves:
            return waves[ws_id]
        ws = by_id[ws_id]
        if not ws.dependencies:
            waves[ws_id] = 0
        else:
            waves[ws_id] = 1 + max(wave_of(dep_id) for dep_id in ws.dependencies)
        return waves[ws_id]

    for ws in workstreams:
        wave_of(ws.id)
    return waves


def to_markdown(workstreams: list[Workstream]) -> str:
    """Render the workstream plan as a markdown section, in sequenced order."""
    sequenced = sequence_workstreams(workstreams)
    waves = compute_waves(workstreams)
    lines = ["## Workstream Plan", ""]
    for ws in sequenced:
        dep_str = ", ".join(ws.dependencies) if ws.dependencies else "None"
        lines.append(f"### [{ws.id}] {ws.name} (wave {waves[ws.id]})")
        lines.append(f"- **Owner:** {ws.owner_role}")
        lines.append(f"- **Depends on:** {dep_str}")
        if ws.resolves_hypothesis_id:
            lines.append(
                f"- **Resolves case hypothesis:** {ws.resolves_hypothesis_id}"
            )
        lines.append(f"- **Description:** {ws.description}")
        lines.append("- **Key deliverables:**")
        for deliverable in ws.key_deliverables:
            lines.append(f"  - {deliverable}")
        lines.append("")
    return "\n".join(lines)
