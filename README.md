# strategy-implementation-roadmap

An implementation-planning toolkit built the way a real consulting team's
*second* deliverable looks — not another market analysis, but the plan for
operationalizing a recommendation that's already been approved.

This project is the direct sequel to
[`market-entry-case-toolkit`](https://github.com/rxj0102/market-entry-case-toolkit).
That project answered "should FreshRoute enter the Greater Toronto Area (GTA)
online grocery delivery market?" with a **conditional go**: a milestone-gated,
partnership-based pilot, reassessed at the 18–24 month mark. This project takes
that recommendation as a given input and builds what a case team actually
delivers next — workstream ownership, a RACI matrix, a gated rollout timeline,
an implementation risk register, a stakeholder communication and
change-management plan, and a case-team staffing and mentorship plan —
combined into one implementation roadmap document.

> **Disclaimer:** FreshRoute is a fictional company built for the sibling
> project's exercise. Every workstream, stakeholder, timeline, risk score,
> and staffing allocation in *this* project is a similarly illustrative,
> hand-set proxy for a portfolio case study — not real client data, not an
> actual implementation plan for any named company, and not a template to be
> copied into a real engagement without re-deriving every number against real
> facts. See "What's intentionally out of scope" below.

## Why this exists

This was built as a portfolio piece for consulting recruiting — specifically,
Bain & Company's **Consultant** role, one step up from Associate Consultant.
The Associate Consultant JD rewards structured analysis and a clean
recommendation, which `market-entry-case-toolkit` already demonstrates. The
Consultant JD explicitly adds: take a strategic recommendation and turn it
into an execution plan, manage that execution, and **mentor junior team
members**. That's a different skill from "can you frame a hypothesis tree and
size a market" — it's organizational and operational thinking, and it needs
its own artifact to demonstrate, not a bullet point on a resume.

So rather than build a second, unrelated case, this project explicitly
continues the first one. The recommendation memo a market-entry case ends
with is not the end of a real engagement — it's the handoff point to exactly
the work this package does.

## What "implementation planning" and "change management" mean in consulting practice

A recommendation memo answers *what* should happen. Implementation planning
answers *how it actually happens*, and change management answers *how the
organization absorbs it without falling apart in the process*. Concretely,
that decomposes into pieces most case teams recognize:

- **Workstream decomposition** — breaking one recommendation into discrete,
  owned, sequenced pieces of work, with explicit dependencies (you can't
  launch marketing before you can legally operate and have somewhere to
  fulfill orders from).
- **RACI (Responsible / Accountable / Consulted / Informed)** — a structured
  answer to "who actually owns this, and who else needs a say," across both
  the client's organization and the delivery team's own seniority ladder.
  This is the artifact that prevents the two most common implementation
  failures: two people who both think they're accountable, and one person
  who's accountable but nobody told.
- **Milestone-gated timelines with go/no-go criteria** — especially relevant
  here because the *entire premise* of the original recommendation was that
  the client shouldn't commit full capital up front. A gate without
  falsifiable, numeric criteria is a calendar reminder, not a decision point.
- **Implementation risk registers** — distinct from the market/financial risks
  a recommendation memo assesses. These are the risks of *doing the work*: a
  partner agreement falling through, a regulatory filing slipping, a courier
  network that can't hold its SLA under real volume.
- **Stakeholder communication and change management** — the "soft skills"
  layer, which is real organizational work and not just a slide about
  "bringing people along." Made concrete here as an actual cadence/channel
  plan and a specific narrative about where the friction will come from.
- **Staffing and mentorship** — a case team is itself an organization that has
  to be staffed, and junior members joining mid-engagement need a structured
  onboarding path, not an assumption that they'll pick it up.

## How this connects to `market-entry-case-toolkit`

| `market-entry-case-toolkit` (Associate Consultant) | `strategy-implementation-roadmap` (Consultant) |
|---|---|
| Hypothesis tree, framed and resolved | Takes the tree's *unresolved* branches (3.1, 3.2, 4) as the specific things the pilot must prove |
| Market sizing, competitive benchmarking, financial feasibility | Not repeated here — this project assumes the market analysis is done and correct |
| A recommendation memo ("conditional go") | The input this project starts from (`case_context.py`) |
| No execution plan | Workstreams, RACI, gated timeline, risk register, comms plan, staffing plan |
| AI-assisted memo synthesis (`memo_synthesis.py`), template + live mode | Same pattern, reused for the change-management narrative (`stakeholder_comms.py`) |

Every module in this package that references the original case (workstream
owners resolving specific hypothesis ids, gate criteria tied back to
hypotheses 3.1/3.2/4, risk-register rows named after the same fulfillment and
regulatory concerns) does so explicitly and traceably — see
`src/strategy_roadmap/case_context.py`, which is the single place this
project restates the original case's facts rather than scattering them across
six modules.

## Package layout

```
src/strategy_roadmap/
├── case_context.py         # the handoff: client, conditional-go decision, unresolved hypotheses
├── workstream_planner.py   # 5 workstreams — owners, dependencies, topological sequencing
├── raci_builder.py         # RACI matrix across workstreams x stakeholders, validated (exactly one A per row)
├── milestone_timeline.py   # Phase 0-3 timeline with go/no-go gates tied to unresolved hypotheses
├── risk_register.py        # implementation risks (not market risks) — likelihood x impact, mitigations
├── stakeholder_comms.py     # communication plan + change-management narrative (template/live LLM modes)
├── staffing_plan.py         # case-team staffing by seniority x workstream, + mentorship/onboarding plan
├── roadmap_synthesis.py     # assembles every module's output into the final roadmap document
└── _viz.py                  # Gantt chart, RACI heatmap, risk heat map (matplotlib)

notebooks/roadmap_walkthrough.ipynb   # the implementation-planning process, worked end-to-end
outputs/implementation_roadmap.md     # the final client-ready roadmap document (generated by the notebook)
outputs/exhibits/*.png                 # the three supporting exhibits (generated by the notebook)
tests/                                 # unit tests for every module (55 tests)
```

## Module 1 — Workstream decomposition (`workstream_planner.py`)

Five workstreams: **Regulatory & Licensing**, **Fulfillment Infrastructure**,
**Local Hiring & Talent**, **Technology Integration**, **Marketing Launch**.
Each has a named owner role, explicit dependencies, and (where relevant) a
link to the specific unresolved case hypothesis it exists to close.
`sequence_workstreams()` topologically sorts them (raising
`CyclicDependencyError` if the dependency graph is broken) and
`compute_waves()` identifies which workstreams can run in parallel. The
sequencing logic is deliberate, not arbitrary: regulatory clearance and
fulfillment infrastructure gate everything else, and marketing launch is
last so customer-acquisition spend doesn't happen before the fulfillment
model is proven.

## Module 2 — RACI matrix (`raci_builder.py`)

A stakeholder set spanning both organizations — client executives (Sponsor,
CFO), client functional leads (one per workstream owner role), and the case
team's own seniority ladder (Partner, Manager, Consultant, Associate
Consultant) — mapped against the five workstreams plus a "Program Governance
& Go/No-Go Gate Decisions" row. `build_case_raci()` validates at construction
time that every row has exactly one Accountable owner and that every
assignment references a real stakeholder — a RACI that fails that check isn't
usable, so it's enforced in code, not left to review.

## Module 3 — Milestone timeline with gates (`milestone_timeline.py`)

Phase 0 (Diligence & Mobilization) → Phase 1 (Pilot Launch & Live Operation)
→ Phase 2 (Go/No-Go Gate) → Phase 3 (Scale-Up Mobilization). Two gates, each
with named, falsifiable criteria and real decision owners:

- **Pilot Readiness Gate** (end of Phase 0): operational readiness — licenses,
  signed agreements, hiring, platform localization.
- **Go/No-Go Gate** (~18 months into the pilot, inside the case's own
  "18–24 month" reassessment window): six criteria, most tied directly to
  hypotheses 3.1 (fulfillment model), 3.2 (regulatory/compliance), and 4
  (financial viability) from the original case — retention, delivery cost,
  CAC, and fulfillment reliability, evaluated against the numbers the
  original financial model actually needs, not vibes. Three real outcomes
  (scale up / extend / wind down), not a binary.

## Module 4 — Implementation risk register (`risk_register.py`)

Ten risks across fulfillment, regulatory, talent, technology, marketing, and
two cross-cutting organizational risks (client/pilot-team friction, case-team
continuity) — deliberately *not* the market/financial risks the original case
already assessed. Each has likelihood/impact scoring (1–5 each, validated),
a severity band (Low/Medium/High/Critical), a named mitigation owner, and an
early-warning indicator specific enough to actually monitor, not a restatement
of the risk itself.

## Module 5 — Stakeholder communications & change management (`stakeholder_comms.py`)

A six-audience communication plan (cadence and channel matched to how much
lead time each audience needs to act) plus a change-management narrative
addressing the pilot's specific organizational friction — new hires joining
mid-implementation, decision-rights ambiguity between the client's existing
U.S. operations team and the new GTA pilot team. The narrative synthesis
mirrors the sibling project's `memo_synthesis.py` pattern exactly: a fully
offline, deterministic **template mode** (what produced this repository's
committed output) and an optional **live mode** that calls the Anthropic API
if `ANTHROPIC_API_KEY` is set, with the same guardrail — the model is handed
the structured facts and a required framing stance, and its job is to write
them up, not originate them. `REVIEW_CHECKLIST` is the human-in-the-loop step
before either mode's output goes near client leadership.

## Module 6 — Team staffing & mentorship plan (`staffing_plan.py`)

The module most directly aimed at the Consultant-level "manage execution,
mentor junior team members" requirement. A four-level staffing plan (Partner,
Manager, Consultant, Associate Consultant) with each person's own time split
across the five workstreams, program governance, and — for every level,
non-zero — a dedicated mentorship allocation. Paired with a structured,
week-by-week onboarding plan for an Associate Consultant joining
**mid-implementation**, not at a clean project kickoff: a context handoff
using this package's own outputs, shadowing, a supervised first ownership
step, client-facing co-leading, and a deliberate step-down (not a stop) in
check-in cadence once the new team member is independent.

## The notebook and the roadmap document

[`notebooks/roadmap_walkthrough.ipynb`](notebooks/roadmap_walkthrough.ipynb)
runs the whole process end-to-end, explicitly opening with the original
case's conditional-go decision and the hypotheses it left unresolved, then
working through each module in the order above before assembling the final
document. Running it end to end regenerates
`outputs/implementation_roadmap.md` and the three exhibits in
`outputs/exhibits/`.

The final roadmap document combines the workstream plan, RACI matrix
(with heatmap exhibit), gated timeline (with Gantt exhibit), risk register
(with heat-map exhibit), stakeholder communication plan, change-management
narrative, and staffing/mentorship plan into the single document a case team
would actually leave with a client.

## Running it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"        # add ".[llm]" too if you want to try live change-narrative synthesis

# Run the full pipeline end-to-end and regenerate the roadmap doc + exhibits:
jupyter nbconvert --to notebook --execute --inplace notebooks/roadmap_walkthrough.ipynb
# ...or just open notebooks/roadmap_walkthrough.ipynb and run all cells.

# Or generate the roadmap document directly from a Python shell:
python -c "from strategy_roadmap.roadmap_synthesis import generate_roadmap; print(generate_roadmap())"

# Run the tests (55 tests across all seven modules):
pytest
```

To try **live change-narrative synthesis** instead of the offline template:
`pip install anthropic`, `export ANTHROPIC_API_KEY=...`, and rerun the
notebook — `synthesize_change_narrative()` auto-detects the key and switches
modes.

## What's intentionally out of scope

- **No real data.** Every workstream, stakeholder, gate threshold, risk score,
  and staffing allocation is an illustrative, hand-set proxy — the point is to
  demonstrate the *method* of implementation planning, not to model an actual
  FreshRoute rollout.
- **No re-run of the market analysis.** Market sizing, competitive
  benchmarking, and financial feasibility stay in `market-entry-case-toolkit`;
  this project takes the conditional-go recommendation as a given input.
- **No project-management software integration.** This produces the planning
  artifacts (RACI, timeline, risk register) a team would then load into
  whatever PM tooling it actually uses — it isn't itself a PM tool.
- **No live LLM call baked into the committed outputs.** No API key was
  available in the build environment; the live path is implemented,
  documented, and tested (see `stakeholder_comms.py`), but
  `outputs/implementation_roadmap.md`'s change-management narrative was
  generated in template mode. This is stated in the document's own footer,
  not hidden.

## License

MIT — see [`LICENSE`](LICENSE).
