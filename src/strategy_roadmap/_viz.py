"""Shared chart styling and exhibit-plotting functions.

Not a case-analysis module -- just the shared visual theme and the
three exhibit functions `roadmap_synthesis.py` calls to regenerate
`outputs/exhibits/*.png`. Colors are the same validated categorical and
status slots from the design-system palette used by the sibling
`market_entry_toolkit._viz` module (fixed hue order, not reassigned per
chart), so the two portfolio projects read as one visual family.

Status colors (good/warning/serious/critical) are reserved for the risk
heat map's severity bands and never reused for a category series, per
the palette's own rule that status color never impersonates a series.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import Patch

from strategy_roadmap.milestone_timeline import Phase
from strategy_roadmap.raci_builder import RaciMatrix, RaciRole
from strategy_roadmap.risk_register import RiskItem

# Categorical (fixed order, slots 1/2/3/7/8 of the design-system palette)
BLUE = "#2a78d6"  # categorical slot 1
ORANGE = "#eb6834"  # categorical slot 2
AQUA = "#1baf7a"  # categorical slot 3
VIOLET = "#4a3aa7"  # categorical slot 7
RED = "#e34948"  # categorical slot 8 / also used as a gate/decision cue

# Status palette (fixed -- never themed, never reused for a category series)
STATUS_GOOD = "#0ca30c"
STATUS_WARNING = "#fab219"
STATUS_SERIOUS = "#ec835a"
STATUS_CRITICAL = "#d03b3b"

GRAY_GRID = "#e1e0d9"  # hairline gridline
GRAY_AXIS = "#c3c2b7"  # baseline/axis
MUTED = "#898781"  # axis/tick labels
PRIMARY_TEXT = "#0b0b0b"
SECONDARY_TEXT = "#52514e"
SURFACE = "#fcfcfb"

_SEVERITY_COLORS = {
    "Low": STATUS_GOOD,
    "Medium": STATUS_WARNING,
    "High": STATUS_SERIOUS,
    "Critical": STATUS_CRITICAL,
}

_RACI_COLORS = {
    RaciRole.INFORMED: BLUE,
    RaciRole.CONSULTED: ORANGE,
    RaciRole.RESPONSIBLE: AQUA,
    RaciRole.ACCOUNTABLE: RED,
    RaciRole.NOT_INVOLVED: GRAY_GRID,
}

_PHASE_COLORS = {"P0": BLUE, "P1": ORANGE, "P2": VIOLET, "P3": AQUA}


def new_figure(figsize: tuple[float, float] = (10, 5)) -> tuple[Figure, Axes]:
    fig, ax = plt.subplots(figsize=figsize, dpi=150)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    return fig, ax


def clean_axes(ax: Axes, y_grid: bool = True) -> None:
    """Strip chart-junk: no top/right spines, hairline recessive
    gridlines, muted tick labels."""
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(GRAY_AXIS)
    ax.tick_params(colors=MUTED, labelsize=9)
    if y_grid:
        ax.yaxis.grid(True, color=GRAY_GRID, linewidth=1, zorder=0)
        ax.set_axisbelow(True)
        ax.tick_params(axis="y", length=0)


def plot_gantt_timeline(phases: list[Phase]) -> Figure:
    """Gantt-style horizontal bar chart of the phased rollout timeline,
    with each gate marked as a vertical decision line at its week."""
    fig, ax = new_figure(figsize=(10, 4.5))
    y_positions = list(range(len(phases)))[::-1]

    for y, phase in zip(y_positions, phases):
        color = _PHASE_COLORS.get(phase.id, MUTED)
        ax.barh(
            y,
            width=phase.duration_weeks,
            left=phase.start_week,
            height=0.5,
            color=color,
            zorder=3,
        )

    for phase in phases:
        if phase.gate is None:
            continue
        ax.axvline(phase.gate.at_week, color=RED, linestyle="--", linewidth=1.5, zorder=4)
        ax.annotate(
            phase.gate.name,
            xy=(phase.gate.at_week, len(phases) - 0.3),
            xytext=(4, 0),
            textcoords="offset points",
            fontsize=8,
            color=RED,
            rotation=0,
            va="bottom",
        )

    ax.set_yticks(y_positions)
    ax.set_yticklabels([phase.name for phase in phases], fontsize=9, color=PRIMARY_TEXT)
    ax.set_xlabel("Week (from pilot plan day zero)", fontsize=9, color=SECONDARY_TEXT)
    ax.set_title(
        "Implementation Timeline: Phased Rollout with Go/No-Go Gates",
        fontsize=11,
        color=PRIMARY_TEXT,
        loc="left",
    )
    clean_axes(ax, y_grid=False)
    ax.xaxis.grid(True, color=GRAY_GRID, linewidth=1, zorder=0)
    ax.set_axisbelow(True)
    fig.tight_layout()
    return fig


def plot_raci_heatmap(matrix: RaciMatrix) -> Figure:
    """RACI matrix rendered as a colored grid: one cell per
    (workstream/governance row, stakeholder) pair, colored by RACI role
    and labeled with its letter."""
    n_rows = len(matrix.rows)
    n_cols = len(matrix.stakeholders)
    fig, ax = new_figure(figsize=(1.1 * n_cols + 2, 0.55 * n_rows + 2.6))

    for row_idx, row in enumerate(matrix.rows):
        for col_idx, stakeholder in enumerate(matrix.stakeholders):
            role = row.assignments[stakeholder.id]
            ax.add_patch(
                plt.Rectangle(
                    (col_idx, n_rows - row_idx - 1),
                    1,
                    1,
                    facecolor=_RACI_COLORS[role],
                    edgecolor=SURFACE,
                    linewidth=2,
                )
            )
            if role != RaciRole.NOT_INVOLVED:
                ax.text(
                    col_idx + 0.5,
                    n_rows - row_idx - 0.5,
                    role.value,
                    ha="center",
                    va="center",
                    fontsize=9,
                    color="white" if role != RaciRole.CONSULTED else PRIMARY_TEXT,
                    fontweight="bold",
                )

    ax.set_xlim(0, n_cols)
    ax.set_ylim(0, n_rows)
    ax.set_xticks([i + 0.5 for i in range(n_cols)])
    ax.set_xticklabels(
        [s.name for s in matrix.stakeholders], rotation=45, ha="right", fontsize=8, color=PRIMARY_TEXT
    )
    ax.set_yticks([n_rows - i - 0.5 for i in range(n_rows)])
    ax.set_yticklabels([row.row_label for row in matrix.rows], fontsize=8, color=PRIMARY_TEXT)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(length=0)
    ax.set_title("RACI Matrix", fontsize=11, color=PRIMARY_TEXT, loc="left")

    legend_handles = [
        Patch(facecolor=_RACI_COLORS[role], label=f"{role.value} = {label}")
        for role, label in [
            (RaciRole.RESPONSIBLE, "Responsible"),
            (RaciRole.ACCOUNTABLE, "Accountable"),
            (RaciRole.CONSULTED, "Consulted"),
            (RaciRole.INFORMED, "Informed"),
        ]
    ]
    ax.legend(
        handles=legend_handles,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.55),
        ncol=4,
        frameon=False,
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.12, 1, 1))
    return fig


def plot_risk_heatmap(risks: list[RiskItem]) -> Figure:
    """5x5 likelihood x impact risk heat map, cells colored by severity
    band (status palette) and labeled with the risk ids that land there."""
    fig, ax = new_figure(figsize=(7, 6))

    grid_ids: dict[tuple[int, int], list[str]] = {}
    for risk in risks:
        grid_ids.setdefault((risk.likelihood, risk.impact), []).append(risk.id)

    for likelihood in range(1, 6):
        for impact in range(1, 6):
            score = likelihood * impact
            if score >= 16:
                severity = "Critical"
            elif score >= 10:
                severity = "High"
            elif score >= 5:
                severity = "Medium"
            else:
                severity = "Low"
            ax.add_patch(
                plt.Rectangle(
                    (impact - 1, likelihood - 1),
                    1,
                    1,
                    facecolor=_SEVERITY_COLORS[severity],
                    edgecolor=SURFACE,
                    linewidth=2,
                )
            )
            ids = grid_ids.get((likelihood, impact))
            if ids:
                ax.text(
                    impact - 0.5,
                    likelihood - 0.5,
                    ", ".join(ids),
                    ha="center",
                    va="center",
                    fontsize=8,
                    color=PRIMARY_TEXT,
                    fontweight="bold",
                )

    ax.set_xlim(0, 5)
    ax.set_ylim(0, 5)
    ax.set_xticks([i + 0.5 for i in range(5)])
    ax.set_xticklabels(range(1, 6), fontsize=9, color=PRIMARY_TEXT)
    ax.set_yticks([i + 0.5 for i in range(5)])
    ax.set_yticklabels(range(1, 6), fontsize=9, color=PRIMARY_TEXT)
    ax.set_xlabel("Impact", fontsize=10, color=SECONDARY_TEXT)
    ax.set_ylabel("Likelihood", fontsize=10, color=SECONDARY_TEXT)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(length=0)
    ax.set_title("Implementation Risk Heat Map", fontsize=11, color=PRIMARY_TEXT, loc="left")

    legend_handles = [
        Patch(facecolor=_SEVERITY_COLORS[band], label=band)
        for band in ("Low", "Medium", "High", "Critical")
    ]
    ax.legend(
        handles=legend_handles,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.15),
        ncol=4,
        frameon=False,
        fontsize=9,
    )
    fig.tight_layout()
    return fig
