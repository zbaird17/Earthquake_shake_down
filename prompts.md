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
