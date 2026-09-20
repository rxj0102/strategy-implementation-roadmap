"""RACI matrix construction for the FreshRoute GTA pilot implementation.

A workstream plan says who *owns* delivery of each piece. A RACI matrix
says who else has to sign off, be consulted, or just stay informed --
across both the client organization and the case team itself. This is
the organizational/change-management layer of the implementation plan:
it makes explicit exactly the kind of stakeholder-management thinking a
Consultant (vs. Associate Consultant) is expected to demonstrate --
who's accountable when a partner-store agreement is late, who needs to
be in the room for a go/no-go gate, and where the case team's own
seniority levels plug in.

Plain dataclasses + an explicit grid, no external dependencies --
consistent with the rest of this package and with the sibling toolkit's
`hypothesis_tree.py`.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from strategy_roadmap.workstream_planner import Workstream


class RaciRole(str, Enum):
    """The four RACI roles a stakeholder can hold against a row."""

    RESPONSIBLE = "R"
    ACCOUNTABLE = "A"
    CONSULTED = "C"
    INFORMED = "I"
    NOT_INVOLVED = "-"


@dataclass(frozen=True)
class Stakeholder:
    """A person/role in the RACI matrix, on either side of the engagement.

    Attributes:
        id: Short stable identifier (e.g. "SPONSOR") used as the grid's
            column key.
        name: Display name for the role.
        org: "client" or "case_team" -- which side of the engagement this
            stakeholder sits on.
        seniority: Seniority label (e.g. "Partner", "SVP"), used to keep
            the RACI grid and the staffing plan's seniority levels aligned.
    """

    id: str
    name: str
    org: str
    seniority: str


@dataclass(frozen=True)
class RaciRow:
    """One row of the matrix: a workstream (or governance item) and the
    RACI role assigned to every stakeholder against it."""

    row_id: str
    row_label: str
    assignments: dict[str, RaciRole]


@dataclass(frozen=True)
class RaciMatrix:
    """The full RACI grid: stakeholders (columns) x rows (workstreams plus
    program governance)."""

    stakeholders: tuple[Stakeholder, ...]
    rows: tuple[RaciRow, ...]


class InvalidRaciRowError(ValueError):
    """Raised when a RACI row doesn't have exactly one Accountable owner,
    or assigns a role to a stakeholder id that doesn't exist."""


def build_stakeholders() -> list[Stakeholder]:
    """The full stakeholder set: client executives, client functional
    leads (one per workstream owner role), and the case team's own
    seniority ladder."""
    return [
        Stakeholder("SPONSOR", "Client Sponsor (SVP, International Expansion)", "client", "SVP"),
        Stakeholder("CFO", "Client CFO", "client", "CFO"),
        Stakeholder("REG_LEAD", "Regulatory & Compliance Lead", "client", "Functional Lead"),
        Stakeholder("FULFILL_LEAD", "Fulfillment Lead", "client", "Functional Lead"),
        Stakeholder("HR_LEAD", "HR / Local Operations Lead", "client", "Functional Lead"),
        Stakeholder("TECH_LEAD", "Technology Integration Lead", "client", "Functional Lead"),
        Stakeholder("MKT_LEAD", "Marketing Lead", "client", "Functional Lead"),
        Stakeholder("PARTNER", "Case Team Partner", "case_team", "Partner"),
        Stakeholder("MANAGER", "Case Team Manager", "case_team", "Manager"),
        Stakeholder("CONSULTANT", "Case Team Consultant", "case_team", "Consultant"),
        Stakeholder("AC", "Case Team Associate Consultant", "case_team", "Associate Consultant"),
    ]


_NI = RaciRole.NOT_INVOLVED
_R = RaciRole.RESPONSIBLE
_A = RaciRole.ACCOUNTABLE
_C = RaciRole.CONSULTED
_I = RaciRole.INFORMED


def build_case_raci(workstreams: list[Workstream]) -> RaciMatrix:
    """Build the RACI matrix for the five workstreams plus program
    governance / gate decisions.

    Design choices worth calling out (this is the "organizational
    thinking" the RACI is meant to demonstrate, not just a filled-in
    template):

    - Each workstream has exactly one Accountable owner: the client
      functional lead who owns delivery (validated by
      `_validate_row()`) -- a RACI with two "A"s is a RACI that will
      cause finger-pointing the first time something slips.
    - The case team Manager is Consulted (not Responsible) on every
      workstream: the Manager's job is cross-workstream coordination
      and unblocking, not doing the work.
    - The Consultant and Associate Consultant are jointly Responsible
      for the analytical/tracking work behind each workstream (RACI
      upkeep, risk-register updates, timeline tracking) -- the actual
      case-team labor, distinct from the client's delivery
      accountability.
    - The Partner is Informed on individual workstreams but Consulted
      (not Accountable) on the governance row: a Partner steers a
      stalled pilot back on track, but doesn't own day-to-day delivery.
    - Program governance and the go/no-go gate decisions are
      Accountable to the Client Sponsor -- consistent with
      `case_context`'s framing that this is a capital-light pilot whose
      whole point is giving the client an early, cheap kill switch.
    """
    stakeholders = build_stakeholders()
    stakeholder_ids = {s.id for s in stakeholders}

    workstream_owner_to_stakeholder = {
        "Regulatory & Compliance Lead (client)": "REG_LEAD",
        "Fulfillment Lead (client)": "FULFILL_LEAD",
        "HR / Local Operations Lead (client)": "HR_LEAD",
        "Technology Integration Lead (client)": "TECH_LEAD",
        "Marketing Lead (client)": "MKT_LEAD",
    }

    rows: list[RaciRow] = []

    for ws in workstreams:
        owner_id = workstream_owner_to_stakeholder[ws.owner_role]
        assignments = {sid: _I for sid in stakeholder_ids}
        assignments[owner_id] = _A
        assignments["MANAGER"] = _C
        assignments["CONSULTANT"] = _R
        assignments["AC"] = _R
        assignments["PARTNER"] = _I
        assignments["SPONSOR"] = _I
        # CFO is only actively engaged where budget is directly at stake.
        assignments["CFO"] = _C if ws.id == "WS5" else _NI
        rows.append(
            RaciRow(row_id=ws.id, row_label=ws.name, assignments=assignments)
        )

    governance_assignments = {sid: _I for sid in stakeholder_ids}
    governance_assignments["SPONSOR"] = _A
    governance_assignments["CFO"] = _C
    governance_assignments["PARTNER"] = _C
    governance_assignments["MANAGER"] = _R
    governance_assignments["CONSULTANT"] = _R
    governance_assignments["AC"] = _I
    rows.append(
        RaciRow(
            row_id="GOV",
            row_label="Program Governance & Go/No-Go Gate Decisions",
            assignments=governance_assignments,
        )
    )

    for row in rows:
        _validate_row(row, stakeholder_ids)

    return RaciMatrix(stakeholders=tuple(stakeholders), rows=tuple(rows))


def _validate_row(row: RaciRow, stakeholder_ids: set[str]) -> None:
    """Validate a single RACI row: every assignment references a real
    stakeholder, and exactly one stakeholder is Accountable."""
    unknown_ids = set(row.assignments) - stakeholder_ids
    if unknown_ids:
        raise InvalidRaciRowError(
            f"Row '{row.row_id}' assigns roles to unknown stakeholder ids: "
            f"{sorted(unknown_ids)}"
        )
    accountable_count = sum(
        1 for role in row.assignments.values() if role == RaciRole.ACCOUNTABLE
    )
    if accountable_count != 1:
        raise InvalidRaciRowError(
            f"Row '{row.row_id}' has {accountable_count} Accountable owners "
            "(expected exactly 1)."
        )


def to_markdown(matrix: RaciMatrix) -> str:
    """Render the RACI matrix as a markdown table."""
    header = ["Workstream"] + [s.name for s in matrix.stakeholders]
    lines = ["## RACI Matrix", ""]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "|".join(["---"] * len(header)) + "|")
    for row in matrix.rows:
        cells = [row.row_label] + [
            row.assignments[s.id].value for s in matrix.stakeholders
        ]
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")
    lines.append(
        "**Legend:** R = Responsible (does the work), A = Accountable "
        "(owns the outcome, exactly one per row), C = Consulted (two-way "
        "input before a decision), I = Informed (one-way notification "
        "after a decision), - = not involved."
    )
    return "\n".join(lines)
