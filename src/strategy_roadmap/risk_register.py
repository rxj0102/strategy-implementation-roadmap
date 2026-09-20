"""Implementation risk register for the FreshRoute GTA pilot.

This is deliberately a different risk register from the one the original
case would have produced. `market_entry_toolkit` never built one -- its
job was to assess whether the *market* was worth entering (sizing,
competition, financial feasibility). This module assesses the risks of
*executing* the pilot the case recommended: a partner-store agreement
falling through, a regulatory filing slipping, a courier network that
can't hold its SLA under real volume. Several rows are written to be
the operational failure mode of exactly the hypotheses `case_context.py`
left unresolved -- an early-warning indicator here is what would tell the
team a go/no-go gate criterion is heading for a "no" well before the
gate itself.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskItem:
    """A single implementation risk.

    Attributes:
        id: Short stable identifier (e.g. "R1").
        category: Risk category (e.g. "Fulfillment", "Regulatory").
        description: The risk itself, phrased as a concrete failure
            mode, not a vague worry.
        workstream_id: Id of the `workstream_planner.Workstream` this
            risk sits under, if it's specific to one. Cross-cutting
            risks (change management, case-team continuity) may have
            none.
        likelihood: 1 (rare) to 5 (near-certain).
        impact: 1 (negligible) to 5 (severe -- would sink the pilot or a
            gate criterion outright).
        mitigation: The specific action taken to reduce likelihood or
            impact.
        mitigation_owner_id: Stakeholder id (from `raci_builder`)
            accountable for the mitigation.
        early_warning_indicator: A concrete, monitorable signal that
            would show this risk materializing before it becomes a
            crisis -- what the team actually watches during rollout.
        tied_hypothesis_id: Id of the `case_context.UnresolvedHypothesis`
            this risk threatens, if any -- these are the rows a reader
            should recognize as "this is what could make gate criterion
            fail."
    """

    id: str
    category: str
    description: str
    workstream_id: str | None
    likelihood: int
    impact: int
    mitigation: str
    mitigation_owner_id: str
    early_warning_indicator: str
    tied_hypothesis_id: str | None = None

    def __post_init__(self) -> None:
        if not 1 <= self.likelihood <= 5:
            raise ValueError(f"likelihood must be 1-5, got {self.likelihood}")
        if not 1 <= self.impact <= 5:
            raise ValueError(f"impact must be 1-5, got {self.impact}")

    @property
    def score(self) -> int:
        """Likelihood x impact, on a 1-25 scale."""
        return self.likelihood * self.impact

    @property
    def severity_band(self) -> str:
        """Standard 5x5 heat-map banding of `score`."""
        if self.score >= 16:
            return "Critical"
        if self.score >= 10:
            return "High"
        if self.score >= 5:
            return "Medium"
        return "Low"


def build_risk_register() -> list[RiskItem]:
    """Construct the implementation risk register for the pilot.

    Ten risks: two per workstream-heavy area (fulfillment, regulatory)
    where the operational stakes are highest, one each for hiring,
    technology, and marketing/commercial, and two cross-cutting
    organizational risks that don't sit under any single workstream.
    """
    return [
        RiskItem(
            id="R1",
            category="Fulfillment",
            description=(
                "Partner-store picking accuracy or throughput degrades once "
                "real pilot-zone order volume hits, beyond what was tested "
                "in the initial agreement"
            ),
            workstream_id="WS2",
            likelihood=3,
            impact=4,
            mitigation=(
                "Phase in order volume with a ramp schedule agreed with "
                "partner stores; weekly picking-accuracy audits for the "
                "first 8 weeks of live operation"
            ),
            mitigation_owner_id="FULFILL_LEAD",
            early_warning_indicator=(
                "Picking-error rate or order-fulfillment cycle time trending "
                "above the partner-store agreement's committed threshold "
                "for 2+ consecutive weeks"
            ),
            tied_hypothesis_id="3.1",
        ),
        RiskItem(
            id="R2",
            category="Fulfillment",
            description=(
                "Third-party courier network cannot sustain agreed delivery "
                "SLAs during demand spikes (weekends, promotions)"
            ),
            workstream_id="WS2",
            likelihood=3,
            impact=4,
            mitigation=(
                "Contract a secondary backup courier for the pilot zone; "
                "cap promotional-driven demand spikes until SLA performance "
                "is proven at baseline volume"
            ),
            mitigation_owner_id="FULFILL_LEAD",
            early_warning_indicator=(
                "On-time delivery rate below 92% in any rolling 2-week window"
            ),
            tied_hypothesis_id="3.1",
        ),
        RiskItem(
            id="R3",
            category="Regulatory",
            description=(
                "Ontario business license or GST/HST registration is "
                "delayed, pushing back the pilot launch date"
            ),
            workstream_id="WS1",
            likelihood=2,
            impact=4,
            mitigation=(
                "Engage local Ontario counsel at Phase 0 kickoff (not after "
                "an internal filing attempt stalls); build a 4-week buffer "
                "into the Phase 0 timeline for regulatory turnaround"
            ),
            mitigation_owner_id="REG_LEAD",
            early_warning_indicator=(
                "No confirmation of filing acceptance by week 8 of Phase 0"
            ),
            tied_hypothesis_id="3.2",
        ),
        RiskItem(
            id="R4",
            category="Regulatory",
            description=(
                "Cross-border customer-data handling review surfaces a "
                "finding that requires a platform rework mid-pilot"
            ),
            workstream_id="WS1",
            likelihood=2,
            impact=3,
            mitigation=(
                "Complete the cross-border data review before, not "
                "alongside, the technology-integration workstream, so any "
                "required rework is designed in rather than retrofitted"
            ),
            mitigation_owner_id="REG_LEAD",
            early_warning_indicator=(
                "Data review not signed off by the end of Phase 0"
            ),
            tied_hypothesis_id="3.2",
        ),
        RiskItem(
            id="R5",
            category="Talent",
            description=(
                "Local hiring shortfall or high early turnover in pilot-zone "
                "operations roles (market lead, courier coordinator, support "
                "staff)"
            ),
            workstream_id="WS3",
            likelihood=3,
            impact=3,
            mitigation=(
                "Start recruiting in parallel with Phase 0 regulatory work "
                "rather than after it clears; build a hiring-pipeline buffer "
                "of two extra qualified candidates per role"
            ),
            mitigation_owner_id="HR_LEAD",
            early_warning_indicator=(
                "Any pilot-zone operations role unfilled within 2 weeks of "
                "its Phase 0 target date, or first-90-day turnover above 15%"
            ),
        ),
        RiskItem(
            id="R6",
            category="Technology",
            description=(
                "Platform localization (CAD pricing, tax calculation, "
                "payments rails, partner-store inventory feed) slips past "
                "the Phase 0 readiness gate"
            ),
            workstream_id="WS4",
            likelihood=2,
            impact=4,
            mitigation=(
                "Sequence the partner-store inventory integration after "
                "core CAD/tax/payments localization, so a slip in the "
                "harder integration doesn't block the simpler, higher-"
                "confidence pieces"
            ),
            mitigation_owner_id="TECH_LEAD",
            early_warning_indicator=(
                "Core localization not passing integration testing by week "
                "10 of Phase 0"
            ),
        ),
        RiskItem(
            id="R7",
            category="Marketing / Commercial",
            description=(
                "Customer acquisition cost (CAC) exceeds the financial "
                "model's threshold because the pilot-zone campaign attracts "
                "low-intent or out-of-zone customers"
            ),
            workstream_id="WS5",
            likelihood=3,
            impact=5,
            mitigation=(
                "Launch with narrow, geo-fenced targeting only, and track "
                "CAC by channel from day one so an underperforming channel "
                "is paused, not scaled"
            ),
            mitigation_owner_id="MKT_LEAD",
            early_warning_indicator=(
                "Blended CAC exceeds the financial model's threshold for 2+ "
                "consecutive reporting weeks"
            ),
            tied_hypothesis_id="4",
        ),
        RiskItem(
            id="R8",
            category="Marketing / Commercial",
            description=(
                "Pilot-zone customer retention falls short of the level the "
                "financial model requires, driven by delivery reliability "
                "or assortment gaps rather than price"
            ),
            workstream_id="WS5",
            likelihood=3,
            impact=5,
            mitigation=(
                "Instrument cohort-level retention reporting from week 1 "
                "(not just at the gate), so a retention shortfall surfaces "
                "early enough to diagnose and fix before the go/no-go gate"
            ),
            mitigation_owner_id="MKT_LEAD",
            early_warning_indicator=(
                "Week-8 cohort retention trending below the financial "
                "model's required curve"
            ),
            tied_hypothesis_id="4",
        ),
        RiskItem(
            id="R9",
            category="Change Management",
            description=(
                "Cross-functional friction between the client's existing US "
                "operations team and the new GTA pilot team slows decisions "
                "(e.g. platform-change approvals, shared vendor contracts)"
            ),
            workstream_id=None,
            likelihood=3,
            impact=3,
            mitigation=(
                "Stand up a joint US/GTA decision forum with clear escalation "
                "paths at Phase 0 kickoff, before friction has a chance to "
                "calcify into informal workarounds"
            ),
            mitigation_owner_id="MANAGER",
            early_warning_indicator=(
                "Cross-team decision requests taking longer than 5 business "
                "days to resolve, self-reported by either team"
            ),
        ),
        RiskItem(
            id="R10",
            category="Case Team Continuity",
            description=(
                "Case-team staffing churn mid-pilot (a Consultant or "
                "Associate Consultant rotating off) causes institutional "
                "knowledge loss on why specific gate criteria or mitigation "
                "plans were set the way they were"
            ),
            workstream_id=None,
            likelihood=2,
            impact=3,
            mitigation=(
                "Maintain the mentorship/onboarding plan in `staffing_plan.py` "
                "as a living handoff document, not a one-time induction, so "
                "any incoming team member can pick up context without "
                "re-deriving it from scratch"
            ),
            mitigation_owner_id="MANAGER",
            early_warning_indicator=(
                "Any case-team rotation announced with less than 2 weeks of "
                "overlap with their successor"
            ),
        ),
    ]


def to_markdown(risks: list[RiskItem]) -> str:
    """Render the risk register as a markdown table, sorted by severity
    (highest score first) so the reader sees the biggest exposures first."""
    ranked = sorted(risks, key=lambda r: r.score, reverse=True)
    lines = ["## Implementation Risk Register", ""]
    lines.append(
        "| ID | Category | Risk | Likelihood | Impact | Score | Severity | "
        "Mitigation Owner | Early-Warning Indicator |"
    )
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for risk in ranked:
        lines.append(
            f"| {risk.id} | {risk.category} | {risk.description} | "
            f"{risk.likelihood} | {risk.impact} | {risk.score} | "
            f"{risk.severity_band} | {risk.mitigation_owner_id} | "
            f"{risk.early_warning_indicator} |"
        )
    lines.append("")
    lines.append("**Mitigations:**")
    for risk in ranked:
        lines.append(f"- **{risk.id}:** {risk.mitigation}")
    return "\n".join(lines)
