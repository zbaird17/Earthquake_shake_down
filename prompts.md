## Propmts

### 2026-11-23

- Asked for a read-through of `spec.md` and a pre-implementation plan for the Python Tkinter desktop app.
- No application code or specification changes were made.
- Planned files and architecture: `app.py` for Tkinter UI and event routing; `structure_model.py` for design-state, placement, and cost data; `calculations.py` for pure NumPy geometry, unit conversion, cost, gravity, joint-demand, and acceleration helpers; `simulation.py` for fixed-step rigid-body dynamics and outcome timing; `requirements.txt` for dependencies; and focused tests under `tests/`.
- Beam/structure calculations will be organized in a pure-model layer: canvas-to-feet conversion, grid and bounds validation, member and node geometry, moment/pinned node state, tributary joint demand, connection constraints, sine-wave table motion, cost, and result scoring.
- Identified a platform conflict: the spec calls for Matter.js, but Matter.js is a JavaScript physics engine and cannot be used directly in a Python/Tkinter app. The implementation should use a Python 2D rigid-body package or a small custom fixed-step solver.
- Identified desktop persistence refinements: replace browser local storage with a JSON file in the OS user-data directory and preserve one three-gravity score set per active design fingerprint.

### Implementation Completion

- Updated `spec.md` before app code to replace browser/Matter.js assumptions with Pymunk and a desktop JSON score store.
- Created `app.py`, `calculations.py`, `structure_model.py`, `simulation.py`, `requirements.txt`, and `tests/test_core.py`.
- Implemented the Tkinter layout, Matplotlib 600×500 canvas, starter tower, placement tools, live cost, gravity controls, amplitude/frequency controls, Pymunk fixed-step testing, joint indicators, results, and reset behavior.
- Installed NumPy, Matplotlib, Pymunk, and their resolved dependencies into the workspace-selected Python 3.15 interpreter.
- Verified every Python module compiles successfully and launched `app.py`; it remained running until explicitly stopped.
- Initial focused tests cover starter-tower structure, cost, peak acceleration, table motion, and minimum member size.
- Reran `python -m unittest discover -s tests -v`; all 6 focused core tests passed after correcting the starter-member count and snapped minimum-size test assumptions.

### Physics Drift Fix

- Investigated the starter tower at zero amplitude over 300 fixed physics steps.
- Fixed Pymunk table-base joints to use a table-local anchor instead of passing a world-coordinate anchor.
- Fixed supported floor-mass joints to rotate mass and beam anchor offsets into each body's local coordinate frame.
- Disabled Pymunk collision responses between structural members and between structural members and the table; supported masses remain constraint-carried, while loose masses retain collisions.
- Rechecked the starter tower: after 5 seconds at 0-inch amplitude, all member and floor-mass horizontal velocities were below rounding/noise and no lateral drift occurred.

### Brace Rendering and Interface Editing

- Investigated the disappearing top brace and replaced live brace-node canvas conversion with Pymunk initial-pose-aware body-local transform.
- Added structural endpoint handles and endpoint dragging for beams, columns, braces, and whole-member dragging in design mode.
- Added grid-snapped placement for all four tools and Delete/Escape removal/cancellation behavior.

### Selected Gravity Visual State

- Added an agreed behavior requirement: the Earth/Mars/Moon gravity button for the active mode must show a contrasting selected fill and border.
- Required the selected state to update immediately and remain visible and disabled throughout testing.
- Applied the visual state in `app.py` with colored Earth, Mars, and Moon selected buttons; unselected and disabled states are updated by a centralized gravity-button state helper.

