"""Phased rollout timeline for the FreshRoute GTA pilot, with explicit
go/no-go gates.

The recommendation memo's whole point was that the financial case for a
full-scale launch didn't clear payback, so the client is being asked to
commit money in stages instead of all at once. This module encodes that
directly: each gate has named, falsifiable criteria, each one tied back
(where relevant) to a specific unresolved hypothesis from
`case_context.py`. A gate with vague criteria like "evaluate progress" is
not a real gate -- it's a calendar reminder. These are not.

Timeline, at a glance:

    Phase 0 (Diligence & Mobilization) -> Readiness Gate
    Phase 1 (Pilot Launch & Live Operation)
    Phase 2 (Go/No-Go Gate) -- assessed ~18 months post-launch, inside
        the "18-24 month" reassessment horizon `case_context` describes
    Phase 3 (Scale-Up Mobilization) -- conditional on a "scale-up" outcome
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GateCriterion:
    """A single, falsifiable condition evaluated at a gate.

    Attributes:
        id: Short stable identifier.
        description: The condition itself, written so it can be checked
            against a real number or a real yes/no fact -- not a vibe.
        tied_hypothesis_id: Id (e.g. "3.1") of the
            `case_context.UnresolvedHypothesis` this criterion is
            designed to resolve, if any. Operational-readiness criteria
            (Phase 0's gate) mostly aren't tied to a hypothesis; the
            Phase 2 go/no-go criteria mostly are.
    """

    id: str
    description: str
    tied_hypothesis_id: str | None = None


@dataclass(frozen=True)
class Gate:
    """A go/no-go decision point at a phase boundary.

    Attributes:
        id: Short stable identifier (e.g. "GATE1").
        name: Display name.
        at_week: Week number (from pilot-plan day zero) the gate is
            convened.
        decision_owner_id: Stakeholder id (from `raci_builder`) who is
            Accountable for the decision made at this gate.
        criteria: The falsifiable conditions evaluated at this gate.
        possible_outcomes: The decisions this gate can actually produce
            (real gates rarely have only "go" and "kill" as options --
            "extend and re-test" is usually the realistic middle
            outcome).
    """

    id: str
    name: str
    at_week: int
    decision_owner_id: str
    criteria: tuple[GateCriterion, ...]
    possible_outcomes: tuple[str, ...]


@dataclass(frozen=True)
class Phase:
    """A phase of the rollout timeline.

    Attributes:
        id: Short stable identifier (e.g. "P0").
        name: Display name.
        start_week: Start week (inclusive), from pilot-plan day zero.
        end_week: End week (inclusive).
        objectives: What this phase is meant to accomplish.
        active_workstream_ids: Ids of `workstream_planner.Workstream`
            entries with meaningful activity during this phase.
        gate: The gate convened at the end of this phase, if any.
    """

    id: str
    name: str
    start_week: int
    end_week: int
    objectives: tuple[str, ...]
    active_workstream_ids: tuple[str, ...]
    gate: Gate | None = None

    @property
    def duration_weeks(self) -> int:
        return self.end_week - self.start_week + 1


def build_timeline() -> list[Phase]:
    """Construct the four-phase, gated rollout timeline.

    Week numbering starts at week 1 = the pilot plan's day zero (not
    the case's original recommendation date). Phase 1's ~18-month
    duration before the go/no-go gate is deliberate: grocery-delivery
    customer retention is only measurable after enough repeat-order
    cycles have played out, and the financial model's payback question
    (hypothesis 4) can't be answered from month-2 data.
    """

    readiness_gate = Gate(
        id="GATE0",
        name="Pilot Readiness Gate",
        at_week=16,
        decision_owner_id="MANAGER",
        criteria=(
            GateCriterion(
                "G0.1", "Ontario business license and GST/HST registration obtained"
            ),
            GateCriterion(
                "G0.2", "Partner-store picking agreements signed for the pilot zone"
            ),
            GateCriterion(
                "G0.3", "Last-mile courier network contracted with agreed SLAs"
            ),
            GateCriterion("G0.4", "Pilot-zone operations team hired and onboarded"),
            GateCriterion(
                "G0.5",
                "Platform localized for CAD pricing, GST/HST tax calculation, "
                "and Canadian payments rails",
            ),
        ),
        possible_outcomes=(
            "Proceed to pilot launch",
            "Delay launch (specific readiness criteria unmet)",
        ),
    )

    go_no_go_gate = Gate(
        id="GATE1",
        name="Go/No-Go Gate",
        at_week=94,
        decision_owner_id="SPONSOR",
        criteria=(
            GateCriterion(
                "G1.1",
                "Partner-store fulfillment cost per order lands within the "
                "range the financial model assumes",
                tied_hypothesis_id="3.1",
            ),
            GateCriterion(
                "G1.2",
                "Last-mile courier network sustains an on-time delivery rate "
                "consistent with the retention assumptions in the financial "
                "model",
                tied_hypothesis_id="3.1",
            ),
            GateCriterion(
                "G1.3",
                "No unresolved regulatory, tax, or employment-law finding "
                "from operating the pilot zone",
                tied_hypothesis_id="3.2",
            ),
            GateCriterion(
                "G1.4",
                "Pilot-zone customer retention at the cohort ages the "
                "financial model relies on meets or exceeds the modeled rate",
                tied_hypothesis_id="4",
            ),
            GateCriterion(
                "G1.5",
                "Blended customer acquisition cost (CAC) is at or below the "
                "level the base-case financial model requires for payback",
                tied_hypothesis_id="4",
            ),
            GateCriterion(
                "G1.6",
                "Pilot-zone contribution margin is trending toward the "
                "payback path the base-case financial model requires",
                tied_hypothesis_id="4",
            ),
        ),
        possible_outcomes=(
            "Scale up (commit to full build-out economics reassessment)",
            "Extend pilot 6 months (inconclusive on one or more criteria)",
            "Wind down (criteria not met; exit the pilot zone)",
        ),
    )

    phase_0 = Phase(
        id="P0",
        name="Phase 0: Diligence & Mobilization",
        start_week=1,
        end_week=16,
        objectives=(
            "Secure regulatory clearance to operate in Ontario",
            "Sign partner-store and courier agreements for the pilot zone",
            "Hire and onboard the pilot-zone operations team",
            "Localize the ordering/payments platform for the Canadian market",
        ),
        active_workstream_ids=("WS1", "WS2", "WS3", "WS4"),
        gate=readiness_gate,
    )

    phase_1 = Phase(
        id="P1",
        name="Phase 1: Pilot Launch & Live Operation",
        start_week=17,
        end_week=94,
        objectives=(
            "Launch live ordering and fulfillment in the pilot zone",
            "Run the sized customer-acquisition campaign and track CAC by "
            "channel from day one",
            "Instrument retention, delivery cost-per-order, and contribution "
            "margin reporting for the go/no-go gate",
        ),
        active_workstream_ids=("WS2", "WS3", "WS4", "WS5"),
        gate=None,
    )

    phase_2 = Phase(
        id="P2",
        name="Phase 2: Go/No-Go Gate",
        start_week=95,
        end_week=98,
        objectives=(
            "Assemble pilot performance data against every gate criterion",
            "Convene the client sponsor, CFO, and case team to render the "
            "scale-up decision",
        ),
        active_workstream_ids=(),
        gate=go_no_go_gate,
    )

    phase_3 = Phase(
        id="P3",
        name="Phase 3: Scale-Up Mobilization",
        start_week=99,
        end_week=130,
        objectives=(
            "Re-run full-scale financial feasibility using pilot-proven "
            "assumptions rather than modeled ones",
            "Expand partner-store and courier agreements beyond the pilot "
            "zone",
            "Begin hiring and technology scale-up for the wider GTA rollout",
        ),
        active_workstream_ids=("WS1", "WS2", "WS3", "WS4", "WS5"),
        gate=None,
    )

    return [phase_0, phase_1, phase_2, phase_3]


def gates(phases: list[Phase]) -> list[Gate]:
    """Return every gate in the timeline, in phase order."""
    return [phase.gate for phase in phases if phase.gate is not None]


def to_markdown(phases: list[Phase]) -> str:
    """Render the phased timeline, including gate criteria, as markdown."""
    lines = ["## Milestone Timeline", ""]
    lines.append("| Phase | Weeks | Duration | Active Workstreams |")
    lines.append("|---|---|---|---|")
    for phase in phases:
        ws_str = ", ".join(phase.active_workstream_ids) if phase.active_workstream_ids else "-"
        lines.append(
            f"| {phase.name} | {phase.start_week}-{phase.end_week} "
            f"| {phase.duration_weeks}w | {ws_str} |"
        )
    lines.append("")

    for phase in phases:
        lines.append(f"### {phase.name} (weeks {phase.start_week}-{phase.end_week})")
        lines.append("**Objectives:**")
        for objective in phase.objectives:
            lines.append(f"- {objective}")
        if phase.gate is not None:
            gate = phase.gate
            lines.append("")
            lines.append(f"**{gate.name}** (week {gate.at_week}, decision owner: {gate.decision_owner_id})")
            lines.append("")
            lines.append("| Criterion | Tied to hypothesis |")
            lines.append("|---|---|")
            for criterion in gate.criteria:
                tied = criterion.tied_hypothesis_id or "-"
                lines.append(f"| {criterion.description} | {tied} |")
            lines.append("")
            lines.append("**Possible outcomes:** " + "; ".join(gate.possible_outcomes))
        lines.append("")
    return "\n".join(lines)
