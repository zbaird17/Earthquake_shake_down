## Purpose
An interactive 2D structural-dynamics learning tool for engineering students to design multi-story framed towers, compare structural choices and construction costs, and observe their approximate response to user-selected horizontal sine-wave shaking. The app supports conceptual instruction and design exploration rather than formal structural analysis or building-code certification.

## Inputs
Structural Elements (Canvas Placement): Columns ($50/ft), beams ($40/ft), diagonal braces ($300/ft), and floor masses ($20/ft), placed via grid snapping.

Grid Resolution: The canvas has 1 ft grid lines, and placement snaps to those lines. Structural lengths are measured in feet. All structural elements and floor masses must remain within the visible canvas boundary.

Floor Masses: Floor masses may be placed freely at any grid point. Placement does not require a specific attachment location.

Shaking Controls: Shake table amplitude A ranges from 0 to 12 inches, and frequency f ranges from 0.1 to 10 Hz for a sine-wave test. Each value has a slider and a corresponding synchronized number box. Suggested starting values are 6 inches of amplitude and 5 Hz of frequency.

Simulation Controls: Start/Stop Test button, Clear Structure button, and Load Starter Tower button.

The app opens in design mode with a blank grid and no structural elements or floor masses. The user selects a structural element, places it on the 1 ft grid, and may revise the design before testing. A placed element is selected by clicking it only after the active placement tool is deactivated. Escape deactivates the placement tool, deselects the active member, and cancels pending placement so clicking an existing member may select or drag it again. Invalid placements outside the canvas boundary or below the shake table are rejected or prevented.

When a structural-member type is selected, the canvas shows a live, grid-snapped ghost preview that follows the pointer until the user places or cancels it. Structural endpoints snap to existing structural nodes or to 1 ft grid intersections; overlapping members must attach at a shared node instead of crossing outside the node. Clicking a corner or body of an existing member while a placement tool is active starts a new member at that snapped node and must not select or drag the existing member. The pointer represents the left/start point of a beam ghost, and beams may be placed at any allowed grid height rather than only at the shake table. Columns may begin at any snapped grid height or structural node, including upper levels; after the bottom/start point is chosen, the ghost extends vertically and the second click selects the upper/end height. A brace ghost begins at the snapped pointer endpoint and spans toward the second clicked node, changing angle and length rather than centering on the pointer. Existing columns may also be extended or moved between nodes. Braces are stretchable, angle-changing members: the user may select a brace and move either endpoint to another node on a column or beam, with the live brace rotating and stretching between the snapped node endpoints. Brace and floor-mass previews indicate snapped anchor validity.

A clearly labeled **Load Starter Tower** button replaces the current design with a simple default frame.

The user sets the sine-wave amplitude and frequency, starts the test, and observes the shake table and tower. During testing, the structure cannot be edited. The user may stop the test manually or clear the structure to return to design mode.

## Calculations
2D Rigid-Body Physics (Matter.js): The simulation uses 2D rigid-body physics to model tower motion and constraints. Unit conversion must consistently represent positions, forces, acceleration, and time.

Gravity: Earth gravity is 32.2 ft/s². Mars gravity is 12.21 ft/s², and Moon gravity is 5.33 ft/s². Selecting a gravity mode applies the corresponding acceleration to the simulation.

Shake Table Displacement: For sine-wave shaking, horizontal table displacement is `x(t) = A sin(2πft)`, where A is amplitude in inches, f is frequency in Hz, t is elapsed time in seconds, and the table starts at zero displacement.

Joint Failure: If the force magnitude at any joint exceeds 15 kip, the associated Matter.js constraint breaks.

Tower wins if it survives for 10.0 seconds without any floor mass colliding with the ground plane.

## Outputs
Real-time animation shows the tower, shake table motion, joint stress states, structural collapse, and floor-mass ground collisions.

Joints use green for normal stress, yellow for elevated stress, and red for failure.

Numerical Readouts:
- Total Cost ($): displayed continuously during design and testing.
- Elapsed Survival Time (s): updated continuously during a test and retained as the final result afterward.
- Peak Ground Acceleration (g): measured as the peak horizontal acceleration of the shake table, updated continuously during a test and retained afterward.
- High Score (g): the highest Peak Ground Acceleration achieved by a successful tower.

High Score is saved in browser local storage so it persists across visits. Failed runs do not update the High Score. Clearing the structure resets test readouts to the initial state.

At the end of a run, the app shows an explicit success or failure result and includes the final elapsed survival time.

## Look and Feel
A playful classroom-simulator style and clean, single-page layout.

A responsive simulation canvas supports a desktop maximum of 600 × 500 px. The structural-element toolbar is positioned on the left side of the canvas. The seismic-controls and readout sidebar is collapsible on both desktop and mobile viewports.

The shake table occupies the bottom of the canvas and is aligned exactly with the bottom snap-grid line. There is no separate ground band between the bottom grid line and the table. Structural columns connect directly to the top surface of the shake table, and no structural member or floor mass may extend below the table.

On mobile viewports, the controls stack beneath the canvas. Placement controls remain touch-friendly, and controls must not obscure the canvas during testing.

The interface provides clear active, disabled, hover, and failure states.

## Validation
Free-Fall Calibration: a block starting 10 ft above the ground is calibrated for each gravity mode:
- Earth at 32.2 ft/s²: 0.78811 seconds
- Mars at 12.21 ft/s²: 1.2798 seconds
- Moon at 5.33 ft/s²: 1.9371 seconds

Measured free-fall times must be within ±1% of the applicable target. Test cases should record the gravity mode, expected time, actual time, tolerance, and pass/fail result.

Shake-Table Calibration: measure 10 complete cycles and compare the measured period with the configured frequency, and compare the measured extreme displacement with the configured amplitude. Verify the checks visually in the animation and with automated test data. General input and motion measurements must be within ±1%.

Acceptance Checks:
- Placement snaps to the 1 ft grid and prevents elements outside the visible canvas boundary.
- Cost updates match the placed element lengths and rates.
- Slider values remain synchronized with their number boxes.
- The 15-kip force-magnitude threshold breaks the associated joint constraint.
- A tower survives 10.0 seconds without a floor-mass ground collision to pass.
- Floor-mass ground collision or structural collapse clearly ends or identifies the failed test.
- Clear Structure resets test readouts and returns the app to the initial blank state.
- The Earth, Mars, and Moon gravity controls work and apply the specified backgrounds.
- Desktop and mobile layouts remain usable and keep controls from obscuring the canvas.

## Out of Scope
- Three-dimensional analysis, out-of-plane motion, and torsion.
- Buckling analysis.
- Recorded earthquake ground-motion libraries; the app uses only user-selected sine-wave amplitude and frequency.
- Other load types, such as wind and fire.

## Features
Place a gravity control at the bottom of the app for Earth, Mars, and Moon modes. Earth uses the default 32.2 ft/s² setting and appearance. Mars uses 12.21 ft/s² and changes the background to red. The Moon uses 5.33 ft/s² and changes the background to grey.

## Build Stages

### Stage 1: Page Mockup
Create the responsive page layout without Matter.js or real calculations. Include the desktop canvas maximum of 600 × 500 px, left structural toolbar, collapsible sidebar, simulation controls, gravity control, and placeholder readouts.

Test: Verify desktop and mobile layouts, toolbar placement, sidebar collapse, control usability, and that no layout change obscures the canvas.

### Stage 2: Structure Placement
Add 1 ft grid snapping and basic design editing. Support columns, beams, braces, floor masses, blank starting state, click selection, mouse repositioning, Delete-key removal, Escape deselection and placement cancellation, starter-tower replacement, and visible-canvas boundary validation. Keep the shake table on the bottom snap-grid line, place column bases directly on the table at that line, and prevent structural members or masses from extending below it.

Test: Verify snapping, boundary limits, selection, repositioning, deletion, starter-tower replacement, and cost-independent placement behavior.

### Stage 3: Costs and Controls
Connect live cost calculations and input controls. Add the 0–12 inch amplitude range, 0.1–10 Hz frequency range, 6-inch and 5 Hz starting values, synchronized sliders and number boxes, and Earth/Mars/Moon gravity selection.

Test: Verify element-cost arithmetic, control limits, synchronized inputs, default values, gravity changes, and required Mars red/Moon grey backgrounds.

### Stage 4: Basic Physics and Shake Motion
Add Matter.js and a basic shake table. Implement consistent unit conversion, Earth/Mars/Moon gravity, sine-wave displacement, tower and table animation, Start/Stop behavior, and editing locks during tests.

Test: Calibrate 10 ft free-fall targets for Earth, Mars, and Moon. Measure 10 cycles and compare table period and extreme displacement with configured values.

### Stage 5: Structural Failure and Outcomes
Add the 15-kip joint-force threshold, green/yellow/red stress states, constraint breaking, structural collapse, floor-mass ground collision, 10-second survival, and explicit win/failure results.

Test: Verify one successful 10-second run, one joint-failure run, one ground-collision run, and one manually stopped test.

### Stage 6: Readouts, Persistence, and Polish
Complete live Total Cost, elapsed time, peak table acceleration, local-storage High Score, Clear Structure reset behavior, mobile touch controls, and final visual polish.

Test: Run the full acceptance checklist; verify successful-run-only High Score persistence across refreshes, failed-run behavior, Clear Structure reset, and desktop/mobile usability.