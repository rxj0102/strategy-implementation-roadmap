"""Case-team staffing plan and mentorship/onboarding plan for the
FreshRoute GTA pilot implementation.

This is the module most directly aimed at the "manage execution, mentor
junior team members" line in a Consultant-level job description, as
opposed to an Associate Consultant one: it's not enough to know *what*
work needs doing (`workstream_planner.py`) -- a Consultant is expected
to know how to staff a team against that work across seniority levels,
and specifically how to bring a junior team member up to speed when
they join *mid-implementation*, not at a clean project kickoff.
"""

from __future__ import annotations

from dataclasses import dataclass

_ALLOCATION_CATEGORIES = ("WS1", "WS2", "WS3", "WS4", "WS5", "GOV", "MENTORSHIP")


@dataclass(frozen=True)
class StaffingAllocation:
    """One case-team member's time allocation across the engagement.

    Attributes:
        seniority: Seniority level (Partner, Manager, Consultant,
            Associate Consultant).
        overall_engagement_pct: What share of this person's total
            working time is dedicated to this engagement (a Partner is
            never 100% on one pilot; an Associate Consultant usually is).
        time_allocation: This person's *own* time (not the whole
            engagement's) split across workstreams WS1-WS5, "GOV"
            (program governance / gate prep), and "MENTORSHIP" (time
            spent mentoring more junior team members) -- must sum to
            100.
    """

    seniority: str
    overall_engagement_pct: int
    time_allocation: dict[str, int]

    def __post_init__(self) -> None:
        unknown = set(self.time_allocation) - set(_ALLOCATION_CATEGORIES)
        if unknown:
            raise ValueError(
                f"Unknown allocation categories for {self.seniority}: {sorted(unknown)}"
            )
        total = sum(self.time_allocation.values())
        if total != 100:
            raise ValueError(
                f"{self.seniority}'s time_allocation sums to {total}, expected 100"
            )
        if not 0 < self.overall_engagement_pct <= 100:
            raise ValueError(
                f"{self.seniority}'s overall_engagement_pct must be in (0, 100], "
                f"got {self.overall_engagement_pct}"
            )


def build_staffing_plan() -> list[StaffingAllocation]:
    """Construct the case-team staffing plan across four seniority
    levels.

    Deliberate shape, not an even split: the Partner is lightly staffed
    (10% of their time) and concentrated on governance and gate
    decisions, not workstream execution; the Manager splits time across
    coordination and every workstream; the Consultant and Associate
    Consultant are fully staffed and carry the bulk of workstream
    execution and tracking. Every level carries a non-zero MENTORSHIP
    allocation -- mentoring is treated as time-boxed work, not an
    unstaffed assumption.
    """
    return [
        StaffingAllocation(
            seniority="Partner",
            overall_engagement_pct=10,
            time_allocation={
                "WS1": 5,
                "WS2": 5,
                "WS3": 0,
                "WS4": 0,
                "WS5": 10,
                "GOV": 70,
                "MENTORSHIP": 10,
            },
        ),
        StaffingAllocation(
            seniority="Manager",
            overall_engagement_pct=75,
            time_allocation={
                "WS1": 15,
                "WS2": 20,
                "WS3": 15,
                "WS4": 15,
                "WS5": 15,
                "GOV": 10,
                "MENTORSHIP": 10,
            },
        ),
        StaffingAllocation(
            seniority="Consultant",
            overall_engagement_pct=100,
            time_allocation={
                "WS1": 15,
                "WS2": 25,
                "WS3": 15,
                "WS4": 20,
                "WS5": 15,
                "GOV": 5,
                "MENTORSHIP": 5,
            },
        ),
        StaffingAllocation(
            seniority="Associate Consultant",
            overall_engagement_pct=100,
            time_allocation={
                "WS1": 10,
                "WS2": 20,
                "WS3": 20,
                "WS4": 20,
                "WS5": 20,
                "GOV": 5,
                "MENTORSHIP": 5,
            },
        ),
    ]


@dataclass(frozen=True)
class OnboardingMilestone:
    """A single step in the mid-implementation onboarding/mentorship
    plan for a junior team member (an Associate Consultant) joining
    after the pilot is already underway.

    Attributes:
        week_offset: Weeks since *this person's* start date (not the
            pilot's week numbering in `milestone_timeline.py`) -- the
            plan is meant to be reusable for whoever joins, whenever
            they join.
        title: Short milestone name.
        description: What happens at this step and why.
        mentor_role: Seniority level responsible for delivering this
            step (usually "Consultant", occasionally "Manager").
    """

    week_offset: int
    title: str
    description: str
    mentor_role: str


def build_mentorship_plan() -> list[OnboardingMilestone]:
    """Construct the structured onboarding/mentorship plan for an
    Associate Consultant joining mid-implementation.

    The core design problem this solves: a clean project kickoff gives
    a new joiner shared context for free (everyone starts at the same
    time). Someone joining mid-pilot has none of that, and the risk
    register's own R10 ("case-team knowledge loss") is exactly what
    happens when onboarding is treated as a one-time induction instead
    of a structured handoff. This plan is written to close that gap on
    a fixed cadence, not an ad hoc one.
    """
    return [
        OnboardingMilestone(
            week_offset=0,
            title="Context handoff session",
            description=(
                "Full walkthrough of the case history: the original "
                "hypothesis tree and conditional-go recommendation "
                "(case_context.py), current workstream status "
                "(workstream_planner.py), the RACI matrix, and the live "
                "risk register -- delivered by the Manager and Consultant "
                "together, using this package's own outputs as the "
                "handoff document rather than an ad hoc verbal briefing."
            ),
            mentor_role="Manager",
        ),
        OnboardingMilestone(
            week_offset=1,
            title="Shadow a workstream cycle",
            description=(
                "Shadow the Consultant through one full weekly tracking "
                "cycle on a single assigned workstream: how status is "
                "gathered, how blockers get escalated, how the RACI is "
                "actually used in a live handoff dispute."
            ),
            mentor_role="Consultant",
        ),
        OnboardingMilestone(
            week_offset=2,
            title="Own a risk-register update, reviewed before circulation",
            description=(
                "Independently update the risk register's likelihood/"
                "impact scoring and early-warning indicators for two "
                "assigned workstreams; the Consultant reviews before it "
                "goes to the weekly cross-functional sync."
            ),
            mentor_role="Consultant",
        ),
        OnboardingMilestone(
            week_offset=4,
            title="Co-lead the cross-functional ops sync",
            description=(
                "Lead the weekly cross-functional operations sync for one "
                "cycle, with the Consultant present as a silent backup "
                "rather than a lead -- the first time the new team member "
                "is client-facing rather than only case-team-facing."
            ),
            mentor_role="Consultant",
        ),
        OnboardingMilestone(
            week_offset=8,
            title="Independent workstream ownership",
            description=(
                "Independently own tracking and reporting for assigned "
                "workstreams. Mentorship check-in cadence moves from "
                "weekly to biweekly -- a deliberate step-down, not a "
                "silent stop, so support doesn't just evaporate once the "
                "new team member looks competent."
            ),
            mentor_role="Consultant",
        ),
        OnboardingMilestone(
            week_offset=12,
            title="Standing mentorship check-in",
            description=(
                "Biweekly 1:1 with the Consultant and a monthly check-in "
                "with the Manager continue for the remainder of the "
                "engagement -- mentorship is treated as ongoing time-boxed "
                "work (see `build_staffing_plan()`'s MENTORSHIP "
                "allocation), not a milestone that's 'done' once reached."
            ),
            mentor_role="Manager",
        ),
    ]


def to_markdown(
    staffing: list[StaffingAllocation], mentorship: list[OnboardingMilestone]
) -> str:
    """Render the staffing plan and mentorship plan as a markdown
    section."""
    lines = ["## Team Staffing & Mentorship Plan", ""]
    lines.append("### Staffing Allocation")
    lines.append("")
    header = ["Seniority", "% of Time on Engagement"] + list(_ALLOCATION_CATEGORIES)
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "|".join(["---"] * len(header)) + "|")
    for allocation in staffing:
        row = [
            allocation.seniority,
            f"{allocation.overall_engagement_pct}%",
        ] + [f"{allocation.time_allocation[cat]}%" for cat in _ALLOCATION_CATEGORIES]
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")
    lines.append(
        "*Percentages in WS1-WS5/GOV/MENTORSHIP columns are each person's "
        "own time split, not a share of the whole team's effort.*"
    )
    lines.append("")

    lines.append(
        "### Onboarding & Mentorship Plan (Associate Consultant joining "
        "mid-implementation)"
    )
    lines.append("")
    for milestone in mentorship:
        lines.append(
            f"**Week {milestone.week_offset}: {milestone.title}** "
            f"(mentor: {milestone.mentor_role})"
        )
        lines.append(f"- {milestone.description}")
        lines.append("")
    return "\n".join(lines)
