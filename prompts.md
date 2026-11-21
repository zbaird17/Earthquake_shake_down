# Prompts

## 2026-11-20

### Request 1

- Asked: Set up the project folders and top-level files, describe the layout in
  `AGENTS.md`, and do not build the app.
- Changed: Created `prompts.md`, `index.html`, `AGENTS.md` layout guidance, and
  the `00_planning`, `01_data`, `02_validation`, and `03_output` folders with
  README files. Added a rule requiring new files to be saved in the appropriate
  folder.
- Worked: Yes. The layout was verified after creation.

### Request 2

- Asked: Read `spec.md`, summarize what the app will do, and assess its sections
  and order without changing or building anything.
- Changed: No files were changed.
- Worked: Yes. The spec was read and reviewed, and a concise assessment was
  provided.

### Request 3

- Asked: Suggest how to revise the spec.
- Changed: No repository files were changed. A revision plan was saved in the
  session workspace.
- Worked: Yes. The plan was presented for approval.

### Request 4

- Asked: Commit the current spec draft.
- Changed: The spec was restored to its existing state and not edited. Git was
  initialized, all current project files were staged, and commit `7723bd9`
  (`Add initial project draft`) was created.
- Worked: Yes. The commit exists and the working tree is clean.

### Request 5

- Asked: Explain whether `prompts.md` had been updated after each request.
- Changed: This entry and the earlier request entries are being appended to
  `prompts.md`.
- Worked: This update was missing previously; it is being corrected now.

### Request 6

- Asked: Review the spec again in plan mode, without changing code or building
  the app.
- Changed: No repository files were changed. The existing spec was reviewed and
  summarized at a high level.
- Worked: Yes. The review identified missing workflow and scope structure.

### Request 7

- Asked: Plan the user workflow without building anything.
- Changed: No repository files were changed. A workflow plan was added to the
  session plan: design mode, ground-motion setup, test start, active test,
  outcome, and post-test reset.
- Worked: Yes. The workflow plan was presented for approval.

### Request 8

- Asked: Decide the initial structure and grid resolution.
- Changed: No repository files were changed. The workflow plan was updated to
  use a blank slate, a 1 ft grid, and an optional starter-tower button.
- Worked: Yes. The blank-slate and 1 ft-grid decisions were recorded.

### Request 9

- Asked: Edit the spec for the approved workflow and initial-state decisions,
  remove the specific earthquake requirement, keep user-selected amplitude and
  frequency, and always update `prompts.md`.
- Changed: Updated `spec.md` with scope, user workflow, blank initial state,
  1 ft grid resolution, optional starter tower, and amplitude/frequency
  sine-wave controls. Strengthened the `AGENTS.md` instruction for prompt
  logging and added this request to `prompts.md`.
- Worked: The documentation edits are complete and ready for review and commit.

### Request 10

- Asked: Keep the same seven headings in `spec.md` and arrange the approved
  edits within those headings.
- Changed: Consolidated the scope and workflow changes into the existing
  Purpose, Inputs, Calculations, Outputs, Look and Feel, Validation, and
  Out of Scope headings. Removed the added Scope, User Workflow, and
  Initial State headings.
- Worked: The spec retains exactly the original seven headings and is ready
  for review and commit.

### Request 11

- Asked: Commit the spec heading-preservation changes.
- Changed: Updated `prompts.md` to record this request.
- Worked: The documentation changes had already been committed as `c2bd373`;
  this prompt-log update will be committed separately.

### Request 12

- Asked: Work only on the Purpose section of `spec.md`, identify unclear
  requirements, and expand the purpose based on the approved audience and
  learning goals.
- Changed: Updated the Purpose text to describe the app as an instructional
  design tool for engineering students comparing tower designs and costs under
  approximate sine-wave shaking. Clarified that it supports conceptual
  learning and is not for formal structural analysis or building-code
  certification.
- Worked: The Purpose section was revised without changing or building other
  app components.

### Request 13

- Asked: Expand the sine-wave frequency range and edit the Inputs section to
  match the planned input decisions.
- Changed: Updated `spec.md` under `## Inputs` with a 0–12 inch amplitude range,
  a 0.1–10 Hz frequency range, free floor-mass placement at grid points,
  visible-canvas placement limits, and the starter-tower control.
- Worked: The Inputs section was revised without changing or building any
  other application components.

### Request 14

- Asked: Plan only the Calculations section, ask about unclear physics details,
  add a gravity feature, and add an eighth heading named `Features`.
- Changed: Added the sine-wave displacement formula, Earth/Mars/Moon gravity
  values, the 15-kip joint-force rule, and the 10-second survival rule to
  `spec.md`. Added a final `## Features` section describing the bottom gravity
  control and Mars red/Moon grey backgrounds.
- Worked: The Calculations and Features edits are complete and ready for commit.

### Request 15

- Asked: Review and clarify only the Outputs section, then edit it to match
  the approved readout behavior.
- Changed: Updated `## Outputs` with green/yellow/red joint states, live and
  final cost/time/acceleration readouts, persistent successful-run High Score,
  cleared test readouts, and explicit success/failure results.
- Worked: The Outputs section was revised without changing or building other
  application components.

### Request 16

- Asked: Clarify only the Look and Feel section, plan the approved layout,
  and update the spec when approved.
- Changed: Updated `## Look and Feel` with a playful classroom style,
  left-side structural toolbar, responsive 600 × 500 px maximum canvas,
  collapsible sidebar, mobile stacked controls, and clear interface states.
- Worked: The Look and Feel section was revised without changing or building
  other application components.

### Request 17

- Asked: Add the Mars and Moon 10 ft free-fall targets to the approved
  Validation section update.
- Changed: Updated `## Validation` with Earth, Mars, and Moon target times,
  ±1% tolerances, shake-table checks, and physics/UI acceptance checks.
- Worked: The Validation section was revised without changing or building
  other application components.
