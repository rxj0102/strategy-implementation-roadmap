"""Stakeholder communication plan and change-management narrative for the
FreshRoute GTA pilot.

This is the "soft skills" layer of the implementation plan made
concrete and structured: who gets told what, how often, through what
channel (`build_communication_plan()`), plus a written narrative on the
specific organizational friction this pilot will create and how the
case team plans to manage it (`synthesize_change_narrative()`).

The narrative half deliberately mirrors
`market_entry_toolkit.memo_synthesis`'s pattern: a template mode that
runs fully offline and deterministically (what actually produced this
repository's committed output), and an optional live mode that calls
the Anthropic API if a key is available. The guardrail is the same,
too -- the LLM is handed the structured facts (`ChangeManagementInputs`)
and a required stance (`narrative_hint`), and its job is to write the
narrative up, not to invent organizational facts or override the given
stance. A human case-team reviewer is still expected to sign off before
this goes near the client (`REVIEW_CHECKLIST`).
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from strategy_roadmap.case_context import CaseContext
from strategy_roadmap.risk_register import RiskItem
from strategy_roadmap.workstream_planner import Workstream


@dataclass(frozen=True)
class CommunicationPlanRow:
    """One row of the stakeholder communication plan.

    Attributes:
        audience: The stakeholder group being communicated with.
        frequency: How often this communication happens.
        channel: The medium used.
        content_focus: What this communication actually covers.
        owner_id: Stakeholder id (from `raci_builder`) accountable for
            sending it.
    """

    audience: str
    frequency: str
    channel: str
    content_focus: str
    owner_id: str


def build_communication_plan() -> list[CommunicationPlanRow]:
    """Construct the stakeholder communication plan.

    Six distinct audiences, each with a cadence and channel matched to
    how much lead time they need to act on what they're told: daily for
    the people executing day-to-day, weekly for cross-functional
    coordination, monthly for governance, and ad hoc exactly when a gate
    decision is due.
    """
    return [
        CommunicationPlanRow(
            audience="Client Sponsor & CFO (Steering Committee)",
            frequency="Monthly",
            channel="Steering committee readout (deck + live discussion)",
            content_focus=(
                "Progress against gate criteria, financial tracking, top "
                "risks, decisions needed from leadership"
            ),
            owner_id="PARTNER",
        ),
        CommunicationPlanRow(
            audience="Client Functional Leads (Regulatory, Fulfillment, HR, "
            "Technology, Marketing)",
            frequency="Weekly",
            channel="Cross-functional operations sync (video call)",
            content_focus=(
                "Workstream status, blockers, and dependency handoffs "
                "between workstreams"
            ),
            owner_id="MANAGER",
        ),
        CommunicationPlanRow(
            audience="Pilot-Zone Operations Team (including new hires)",
            frequency="Daily",
            channel="Stand-up (in-person or video)",
            content_focus=(
                "Day-to-day execution status, immediate blockers, onboarding "
                "support for new team members"
            ),
            owner_id="HR_LEAD",
        ),
        CommunicationPlanRow(
            audience="Broader Client Organization (existing US operations "
            "and other functions)",
            frequency="Monthly",
            channel="Company newsletter / all-hands update",
            content_focus=(
                "Pilot milestones reached, what to expect next, how the "
                "pilot affects existing teams' processes or shared systems"
            ),
            owner_id="MANAGER",
        ),
        CommunicationPlanRow(
            audience="Case Team (internal)",
            frequency="Weekly",
            channel="Internal working session",
            content_focus=(
                "RACI and risk-register updates, gate-readiness tracking, "
                "and a standing mentorship check-in for junior team members"
            ),
            owner_id="PARTNER",
        ),
        CommunicationPlanRow(
            audience="Client Sponsor & CFO",
            frequency="At each gate (ad hoc)",
            channel="Gate decision memo + review meeting",
            content_focus=(
                "Gate criteria results against threshold, recommended "
                "decision, and the options actually on the table"
            ),
            owner_id="PARTNER",
        ),
    ]


@dataclass(frozen=True)
class ChangeManagementInputs:
    """Everything the change-management narrative prompt is grounded in.
    Every field is text produced by other modules in this package -- the
    LLM (in live mode) is never asked to originate an organizational fact,
    only to write up facts it's handed, the same guardrail
    `memo_synthesis.CaseInputs` uses for the recommendation memo.
    """

    client_name: str
    pilot_summary: str
    new_hires_context: str
    friction_points: str
    narrative_hint: str
    """A short, analyst-authored steer on how to frame the narrative
    (e.g. "frame the friction as manageable via structured governance,
    not as a reason to slow the pilot"). Treated as a constraint on the
    write-up, not a suggestion -- see `memo_synthesis.CaseInputs
    .recommendation_hint` for the same pattern in the sibling repo."""


def build_change_management_inputs(
    case_context: CaseContext,
    workstreams: list[Workstream],
    risks: list[RiskItem],
) -> ChangeManagementInputs:
    """Assemble `ChangeManagementInputs` from the case context, workstream
    plan, and risk register, so the narrative's grounding facts are
    computed once from those modules rather than re-typed by hand."""
    hiring_ws = next(ws for ws in workstreams if ws.id == "WS3")
    friction_risk = next((r for r in risks if r.id == "R9"), None)

    friction_bullets = [
        "New GTA pilot-zone hires (local market lead, courier-network "
        "coordinator, support staff) joining an organization whose "
        "processes, tooling, and culture were built around 15 established "
        "U.S. metro markets, not a first international pilot.",
        "Decision rights between the existing U.S. operations team and the "
        "new GTA pilot team are not yet precedented -- shared vendor "
        "contracts, platform-change approvals, and data-handling policy all "
        "touch both.",
        "The pilot's capital-light, milestone-gated structure (a deliberate "
        "choice given the financial case did not clear payback at full "
        "scale) means the GTA team is operating with more scrutiny and a "
        "shorter runway to prove itself than a typical new-market launch "
        "team would have.",
    ]
    if friction_risk is not None:
        friction_bullets.append(
            f"Risk register item {friction_risk.id}: {friction_risk.description}"
        )

    return ChangeManagementInputs(
        client_name=case_context.client_name,
        pilot_summary=case_context.original_recommendation,
        new_hires_context=(
            f"Workstream {hiring_ws.id} ({hiring_ws.name}) hires a pilot-zone "
            "market lead, courier-network coordinator, and customer support "
            "staff -- all new to FreshRoute, several new to on-demand "
            "grocery delivery, joining mid-implementation rather than at "
            "company founding."
        ),
        friction_points="\n".join(f"- {b}" for b in friction_bullets),
        narrative_hint=(
            "Frame the organizational friction as real and specifically "
            "named, but manageable through structured governance (a joint "
            "US/GTA decision forum, explicit escalation paths, a living "
            "mentorship/onboarding plan) -- not as a reason to slow down "
            "or de-scope the pilot. The pilot's whole premise is proving "
            "execution capability, not just market opportunity."
        ),
    )


# ---------------------------------------------------------------------------
# Prompt library (live mode)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are a senior case-team member at a top-tier management consultancy, \
writing the internal change-management brief that accompanies an \
implementation roadmap. This is not a client-facing recommendation memo \
-- it is the honest internal narrative the case team and client \
leadership use to plan for organizational friction before it happens. \
Crisp, specific, no corporate-speak, no false reassurance.

Hard rules:
1. Use ONLY the facts given to you in the inputs below. Do not invent \
organizational history, named individuals, or incidents that aren't in \
the input.
2. The framing stance is given to you (see "Required narrative framing" \
in the user message). Your job is to write the friction points up \
persuasively and precisely within that framing, not to reach your own \
independent conclusion about whether the pilot should proceed.
3. Structure: a short paragraph naming the friction points concretely, \
a short paragraph on the specific new-hire onboarding challenge, and a \
short paragraph on the structural mitigations already in place \
(governance forum, mentorship plan, escalation paths).
4. Write for an internal case-team-and-client-leadership audience: \
assume they already know the pilot's structure, don't re-explain it.
"""


def build_user_prompt(inputs: ChangeManagementInputs) -> str:
    """Assemble the user-turn prompt from structured inputs. A plain
    function (not a method) so the exact prompt is printable and
    unit-testable independent of whether a live call happens -- same
    reasoning as `memo_synthesis.build_user_prompt()`."""
    return f"""\
CLIENT: {inputs.client_name}
PILOT SUMMARY: {inputs.pilot_summary}

=== NEW HIRES CONTEXT ===
{inputs.new_hires_context}

=== IDENTIFIED FRICTION POINTS ===
{inputs.friction_points}

=== REQUIRED NARRATIVE FRAMING ===
{inputs.narrative_hint}

Write the internal change-management narrative now, per the system \
instructions.
"""


# ---------------------------------------------------------------------------
# Template mode (offline, deterministic, no LLM)
# ---------------------------------------------------------------------------


def draft_change_narrative_template(inputs: ChangeManagementInputs) -> str:
    """Fill the change-management narrative directly from
    `ChangeManagementInputs`, with no LLM call. This is the default
    synthesis path and is what produced this repository's committed
    output."""
    return f"""\
## Change Management Narrative

**Pilot:** {inputs.pilot_summary}

### Where the friction will come from

{inputs.friction_points}

### The new-hire challenge, specifically

{inputs.new_hires_context} Onboarding them mid-implementation -- after \
the regulatory and fulfillment groundwork is already underway rather \
than at a clean company-founding starting point -- means their ramp-up \
has to happen alongside live execution, not before it. That is exactly \
what `staffing_plan.py`'s mentorship plan is designed to shorten.

### How this is being managed, not just acknowledged

{inputs.narrative_hint}
"""


# ---------------------------------------------------------------------------
# Live mode (optional, requires `anthropic` package + ANTHROPIC_API_KEY)
# ---------------------------------------------------------------------------


class LiveSynthesisUnavailable(RuntimeError):
    """Raised when live mode is requested but the `anthropic` package or
    an API key isn't available -- callers should catch this and fall
    back to `draft_change_narrative_template()` rather than crash the
    run."""


def draft_change_narrative_live(
    inputs: ChangeManagementInputs,
    model: str = "claude-sonnet-4-5-20250929",
    max_tokens: int = 900,
) -> str:
    """Call the Anthropic API to draft the change-management narrative
    from `inputs`. Requires the optional `anthropic` package and
    `ANTHROPIC_API_KEY`; raises `LiveSynthesisUnavailable` with a clear
    message otherwise so callers can fall back to the template path --
    same contract as `memo_synthesis.draft_memo_live()`."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise LiveSynthesisUnavailable(
            "ANTHROPIC_API_KEY is not set. Set it to use live LLM synthesis, "
            "or call draft_change_narrative_template() / "
            "synthesize_change_narrative(use_live_llm=False) for the "
            "offline template path."
        )
    try:
        import anthropic
    except ImportError as exc:
        raise LiveSynthesisUnavailable(
            "The 'anthropic' package is not installed. Install it with "
            "`pip install anthropic` (or `pip install -e \".[llm]\"`) to use "
            "live synthesis, or call draft_change_narrative_template() "
            "instead."
        ) from exc

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_user_prompt(inputs)}],
    )
    return "".join(
        block.text for block in response.content if getattr(block, "type", None) == "text"
    )


def synthesize_change_narrative(
    inputs: ChangeManagementInputs, use_live_llm: bool | None = None
) -> tuple[str, str]:
    """Top-level synthesis entry point.

    If `use_live_llm` is None (the default), auto-detects: uses live
    mode if `ANTHROPIC_API_KEY` is set and `anthropic` is importable,
    otherwise falls back to template mode. Pass True/False to force a
    mode explicitly (e.g. in tests). Returns (narrative_text, mode)
    where mode is "live" or "template".
    """
    should_try_live = use_live_llm if use_live_llm is not None else bool(
        os.environ.get("ANTHROPIC_API_KEY")
    )
    if should_try_live:
        try:
            return draft_change_narrative_live(inputs), "live"
        except LiveSynthesisUnavailable:
            if use_live_llm is True:
                raise
    return draft_change_narrative_template(inputs), "template"


# ---------------------------------------------------------------------------
# Human-in-the-loop review
# ---------------------------------------------------------------------------

REVIEW_CHECKLIST: tuple[str, ...] = (
    "Every friction point in the draft traces back to a real input fact "
    "(workstream, risk-register item, or case context) -- none were "
    "invented by the LLM.",
    "The narrative's framing matches `narrative_hint` -- it did not "
    "soften the friction into nothing, or escalate it into a reason to "
    "stop the pilot, without the case team deciding that explicitly.",
    "No named individual or fabricated incident appears in the draft.",
    "The new-hire onboarding challenge is addressed specifically, not "
    "just folded into generic change-management language.",
    "A named case-team reviewer has read the full draft and signed off "
    "before it is shared with client leadership.",
)


def print_review_checklist() -> None:
    print("Human-in-the-loop review checklist (complete before sharing):")
    for i, item in enumerate(REVIEW_CHECKLIST, start=1):
        print(f"  [ ] {i}. {item}")


def to_markdown(comms_plan: list[CommunicationPlanRow]) -> str:
    """Render the communication plan as a markdown table (the narrative
    itself is rendered separately by `draft_change_narrative_template()`
    / `synthesize_change_narrative()`, since it's prose, not tabular)."""
    lines = ["## Stakeholder Communication Plan", ""]
    lines.append("| Audience | Frequency | Channel | Content Focus | Owner |")
    lines.append("|---|---|---|---|---|")
    for row in comms_plan:
        lines.append(
            f"| {row.audience} | {row.frequency} | {row.channel} | "
            f"{row.content_focus} | {row.owner_id} |"
        )
    lines.append("")
    return "\n".join(lines)
