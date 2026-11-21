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

### Request 18

- Asked: Review and shorten the Out of Scope section, then update it with the
  approved exclusions.
- Changed: Reduced `## Out of Scope` to three-dimensional/out-of-plane
  behavior, buckling, recorded earthquake libraries, and other loads such as
  wind and fire.
- Worked: The Out of Scope section was revised without changing or building
  other application components.

### Request 19

- Asked: Review the complete spec and identify improvements.
- Changed: No spec edit was requested or made. A whole-document consistency
  review identified follow-up needs around defaults, editing behavior, cost
  interpretation, gravity switching, and test-state handling.
- Worked: The review identified ambiguous defaults and editing behavior as the
  first priority.

### Request 20

- Asked: Resolve default gravity, default amplitude and frequency, element
  selection/deletion/repositioning, and starter-tower replacement behavior.
- Changed: Updated `spec.md` to default gravity to Earth, suggest 6 inches and
  5 Hz as middle-range starting values, define click selection with mouse
  repositioning and Delete-key removal, and specify that starter-tower loading
  replaces the existing design.
- Worked: The ambiguity decisions were documented in the spec.

### Request 21

- Asked: Determine whether any other spec improvements are needed before
  implementation.
- Changed: No spec changes were made. The full spec was reviewed for major
  contradictions and missing requirements.
- Worked: The spec is ready to build. Minor implementation choices such as exact
  starter-tower geometry and internal unit scaling can be resolved while coding.

### Request 22

- Asked: Read the full spec and suggest 4–6 staged implementation phases,
  starting with a non-calculation page mockup and including testing checks.
- Changed: No spec or application files were changed. A staged build-and-test
  plan was prepared for the response.
- Worked: The planning request was fulfilled and no code was written.

### Request 23

- Asked: Add the staged implementation plan to `spec.md` under a new
  `Build Stages` heading.
- Changed: Added six build stages covering mockup, placement, costs and
  controls, physics, outcomes, and persistence/polish. Included test checks for
  each stage.
- Worked: The Build Stages section was added without writing application code.

### Request 24

- Asked: Build Stage 1 from `spec.md` as a single-file HTML mockup, showing
  all specified inputs, outputs, and plots with realistic placeholder values.
- Changed: Replaced `index.html` with a responsive plain HTML/CSS/JavaScript
  mockup containing the structural toolbar, 1 ft simulation grid, starter
  tower, shake table, amplitude/frequency controls, gravity modes, numerical
  readouts, ground-motion plot, simulation buttons, and collapsible sidebar.
- Worked: The mockup serves successfully on a local HTTP server and renders as
  a desktop page with the intended layout and controls.

### Request 25

- Asked: Build Stage 2 from `spec.md` with functional structural placement and
  editing while retaining the mockup inputs, outputs, and plots.
- Changed: Updated `index.html` for a blank initial design, 1 ft grid-snapped
  placement, selectable and draggable elements, Delete-key removal, starter
  tower loading, structure clearing, boundary limits, and editing lock during
  test mode.
- Worked: Browser verification passed for blank state, starter loading,
  placement, Delete removal, test-mode editing lock, and mobile overflow.

### Request 26

- Asked: Shrink the canvas at narrow viewport widths and keep the tower view
  centered instead of left-aligning it.
- Changed: Updated the responsive workspace and mobile canvas sizing so the
  canvas uses the available width, remains centered, and does not overflow;
  reduced the mobile minimum canvas height and prevented horizontal layout
  left alignment.
- Worked: Responsive sizing was implemented. The starter tower now needs
  dynamic center-based placement verification.

### Request 26 verification

- Changed: Verified the canvas at a 620 px viewport: it shrinks to the available
  width, has no horizontal overflow, remains centered, and the starter tower
  is built around the canvas center.
- Worked: Yes. The responsive sizing and dynamic starter placement passed
  browser checks.

### Request 27

- Asked: Change beam and column placement from preset segments to two-click
  start-and-end placement.
- Changed: Updated `index.html` with pending segment preview, horizontal beam
  endpoints, vertical column endpoints, Escape cancellation, and dynamic
  starter-tower beam/column segments.
- Worked: Browser checks passed for variable-length beam and column placement,
  starter-tower loading, and segment status feedback.

### Request 28

- Asked: Allow beam and column length to be edited after placement and show
  the segment preview following the mouse during placement.
- Changed: Updated `index.html` with mouse-following segment previews,
  displayed live length labels, and draggable start/end handles on placed
  beams and columns.
- Worked: Browser checks passed for live beam and column previews, placed
  segment length labels, and dragging endpoint handles to resize both types.

### Request 29

- Asked: Require braces to snap to columns and beams.
- Changed: Updated `index.html` so brace placement uses two snapped anchor
  points on structural beam or column segments, with live diagonal preview
  and invalid-anchor feedback.
- Worked: Browser and direct interaction checks passed for snap-point
  detection, live brace preview, and brace creation between beam/column
  anchors.
