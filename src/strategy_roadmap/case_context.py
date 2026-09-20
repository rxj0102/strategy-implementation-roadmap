"""Shared case facts carried over from the market-entry-case-toolkit project.

This module is the single source of truth for the "input" this project
builds on: the FreshRoute / Greater Toronto Area (GTA) market-entry case,
its conditional-go recommendation, and the specific hypothesis-tree
branches the original analysis left unresolved. Every other module in
this package imports from here rather than re-stating case facts, so the
link back to the original recommendation memo is explicit and traceable
in one place instead of scattered across six modules.

See https://github.com/rxj0102/market-entry-case-toolkit for the source
case: `outputs/recommendation_memo.md` (the memo) and
`src/market_entry_toolkit/hypothesis_tree.py` (the issue tree these
`UnresolvedHypothesis` entries reference by id).

Disclaimer: FreshRoute is a fictional company. All figures, names, and
dates below are illustrative, hand-set proxies for a portfolio case
study, not real client data. See the README for the full disclaimer.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UnresolvedHypothesis:
    """A hypothesis-tree branch the original analysis left unresolved.

    These are exactly the threads a milestone-gated pilot exists to
    close before a full-scale build-out is committed -- they are the
    reason the gates in `milestone_timeline.py` and several rows in
    `risk_register.py` exist at all.

    Attributes:
        id: The original hypothesis-tree node id (e.g. "3.1"), for
            direct cross-reference back to the source case.
        statement: The original hypothesis statement.
        original_verdict: The verdict the analysis toolkit reached
            ("partially supported" or "not supported").
        why_unresolved: Why the original analysis couldn't fully close
            this branch without in-market data.
        what_the_pilot_must_prove: The specific, falsifiable thing the
            Toronto pilot needs to demonstrate to resolve this branch.
    """

    id: str
    statement: str
    original_verdict: str
    why_unresolved: str
    what_the_pilot_must_prove: str


@dataclass(frozen=True)
class CaseContext:
    """The FreshRoute GTA case as handed off to the implementation team."""

    client_name: str
    core_question: str
    original_recommendation: str
    pilot_scope: str
    reassessment_horizon: str
    unresolved_hypotheses: tuple[UnresolvedHypothesis, ...]


def build_case_context() -> CaseContext:
    """Construct the case context this implementation roadmap builds on.

    Mirrors `market_entry_toolkit.hypothesis_tree.build_case_tree()` and
    `outputs/recommendation_memo.md` from the sibling repository --
    the conditional-go recommendation and the three branches (3.1, 3.2,
    and the financial-viability branch, 4) that were "partially
    supported" or "not supported" rather than cleanly resolved.
    """

    fulfillment_model = UnresolvedHypothesis(
        id="3.1",
        statement=(
            "Fulfillment model (partner-store picking + last-mile courier "
            "network) is replicable in the GTA without a new warehouse "
            "buildout"
        ),
        original_verdict="partially supported",
        why_unresolved=(
            "The operating-model fit review was qualitative, checked "
            "against the known GTA grocery-partner landscape -- it was "
            "never tested against a real partner-store agreement, a real "
            "courier network, or real GTA order volume."
        ),
        what_the_pilot_must_prove=(
            "Partner-store picking accuracy and last-mile courier delivery "
            "cost per order hold within the assumptions used in the "
            "financial model, at real pilot-zone order volumes."
        ),
    )

    regulatory_compliance = UnresolvedHypothesis(
        id="3.2",
        statement=(
            "Regulatory, payments, and labor differences (GST/HST, "
            "cross-border data, employment law) are navigable within "
            "FreshRoute's existing compliance capability"
        ),
        original_verdict="partially supported",
        why_unresolved=(
            "The regulatory/compliance delta review identified the gaps "
            "but did not test them against an actual GTA business license "
            "application, an actual cross-border data-handling review, or "
            "actual Ontario employment-standards hiring."
        ),
        what_the_pilot_must_prove=(
            "FreshRoute can obtain the required GTA business licenses, "
            "clear a cross-border data review, and hire under Ontario "
            "employment law on the timeline the pilot plan assumes, "
            "without a dedicated new compliance build."
        ),
    )

    financial_viability = UnresolvedHypothesis(
        id="4",
        statement="The entry is financially worth it on a risk-adjusted basis",
        original_verdict="not supported (for a full-scale launch as originally framed)",
        why_unresolved=(
            "None of the base/upside/downside financial scenarios cleared "
            "payback within five years under the full ~$18M CAD upfront "
            "launch. This is precisely why the recommendation was reframed "
            "from a full launch to a smaller, milestone-gated pilot -- the "
            "unresolved question is whether a pilot can prove out the "
            "retention, delivery-cost, and CAC assumptions the full-scale "
            "case depends on, at a fraction of the capital at risk."
        ),
        what_the_pilot_must_prove=(
            "Pilot-zone customer retention, delivery cost per order, and "
            "customer acquisition cost (CAC) land within the ranges the "
            "full-scale financial model requires to clear payback -- "
            "measured directly, not modeled."
        ),
    )

    return CaseContext(
        client_name="FreshRoute",
        core_question=(
            "Should FreshRoute enter the Greater Toronto Area (GTA) online "
            "grocery delivery market?"
        ),
        original_recommendation=(
            "Conditional go: proceed via a milestone-gated, "
            "partnership-based pilot in a subset of the GTA to prove out "
            "retention, delivery-cost, and CAC assumptions, with a formal "
            "reassessment of full-scale build-out economics at the "
            "18-24 month mark."
        ),
        pilot_scope=(
            "A single pilot zone within the GTA (a subset of serviceable "
            "postal codes, not the full metro), operated via partner-store "
            "picking and a third-party last-mile courier network rather "
            "than a new owned warehouse -- deliberately capital-light so "
            "the pilot can fail cheaply if the unresolved hypotheses don't "
            "hold."
        ),
        reassessment_horizon="18-24 months from pilot launch",
        unresolved_hypotheses=(
            fulfillment_model,
            regulatory_compliance,
            financial_viability,
        ),
    )
