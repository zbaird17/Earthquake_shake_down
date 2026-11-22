## Purpose
An interactive 2D structural-dynamics learning tool for engineering students to design multi-story framed towers, compare structural choices and construction costs, and observe their approximate response to user-selected horizontal sine-wave shaking. The app supports conceptual instruction and design exploration rather than formal structural analysis or building-code certification.

## Inputs
Structural Elements (Canvas Placement): Columns ($50/ft), beams ($40/ft), diagonal braces ($30/ft), and floor masses ($20/ft), placed via grid snapping.

Grid Resolution: The canvas has 1 ft grid lines, and placement snaps to those lines. Structural lengths are measured in feet. All structural elements and floor masses must remain within the visible canvas boundary.

Minimum Element Size: Structural members may be as short as 1 ft. Floor-mass width and height may each be as small as 1 ft; no element dimension or member length may be less than 1 ft.

Floor Masses: Floor masses may be placed freely at any grid point. A mass resting on a supporting beam is attached to that beam with constraints at its beam-node attachment points and may move as part of the beam/floor system without sliding independently off the structure. A mass placed without beam support remains unattached and falls under gravity as soon as a test starts.

Shaking Controls: Shake table amplitude A ranges from 0 to 12 inches, and frequency f ranges from 0.1 to 10 Hz for a sine-wave test. Each value has a slider and a corresponding synchronized number box. Suggested starting values are 6 inches of amplitude and 5 Hz of frequency.

Stage 3 Cost and Controls: Structural total cost updates live whenever the design changes. Each column or beam length contributes at $50/ft or $40/ft respectively, each brace contributes at $30/ft, and each floor mass contributes at $20/ft based on its length in the horizontal and vertical dimensions as represented by the element footprint. Amplitude and frequency sliders and number boxes remain synchronized and enforce their stated ranges. Earth, Mars, and Moon selections update the gravity mode and its required visual theme.

Simulation Controls: Start/Stop Test button, Clear Structure button, and Load Starter Tower button.

The app opens in design mode with the exact default starter tower already loaded, plus the user-selectable structural tools. At the 600 px-wide desktop canvas size, columns connect from x=180 and x=420, with shared beam and brace nodes at y=220, y=340, and y=460. The three beams span 240 px horizontally and are 12 ft each; the bottom beam sits directly on the table top. Each side column is split into two separate 6 ft segments from y=220 to y=340 and y=340 to y=460, with a shared column/beam node at y=340. The starter brace layout contains exactly two braces: one spanning the top level between y=220 nodes and one spanning the bottom level between y=340 and y=460 nodes. The shake table is 360 px wide, its top is y=460, and it remains fully visible above the lower canvas/grid band. Each floor mass is a wide 220×20 px panel centered exactly within the 240 px bay, with its bottom edge aligned to a beam centerline. The default tower has two floor masses, on the top and middle beams; the bottom bay has no mass. Mass panels render behind columns, beams, and braces. Columns, beams, and braces must remain snapped to grid lines after placement, endpoint editing, and dragging. During tests, braces follow the two exact beam/column nodes at their endpoints and rotate/translate with the rest of the frame rather than remaining static or teleporting. The Normal/Elevated/Failed legend remains in the top-right outside the structure. Clearing and reloads preserve this default configuration unless the user explicitly replaces it. Escape deactivates the active placement tool and cancels pending placement.

When a structural-member type is selected, the canvas shows a live, grid-snapped ghost preview that follows the pointer until the user places or cancels it. Structural endpoints snap to existing structural nodes or to 1 ft grid intersections; overlapping members must attach at a shared node instead of crossing outside the node. Clicking a corner or body of an existing member while a placement tool is active starts a new member at that snapped node and must not select or drag the existing member. The pointer represents the left/start point of a beam ghost, and beams may be placed at any allowed grid height rather than only at the shake table. Columns may begin at any snapped grid height or structural node, including upper levels; after the bottom/start point is chosen, the ghost extends vertically and the second click selects the upper/end height. Braces use the same two-click placement flow as beams and columns: either endpoint may be selected at any allowed 1 ft grid intersection, and the user need not click on an existing member. The brace ghost begins at the snapped first endpoint and spans toward the second clicked point, changing angle and length rather than centering on the pointer. Existing columns may also be extended or moved between nodes. Braces are stretchable, angle-changing members: the user may select a brace and move either endpoint to another snapped point, with the live brace rotating and stretching between the snapped endpoints. Brace rendering and length labels always remain visually upright: the physical nodes do not move, and the label/text is counter-rotated while the brace line stretches and changes angle. Floor-mass ghosts use the same snapped top-left position as the placed mass footprint, filling grid cells between grid lines rather than centering the panel on a grid line. Brace and floor-mass previews indicate snapped anchor validity.

A clearly labeled **Load Starter Tower** button replaces the current design with a simple default frame.

The user sets the sine-wave amplitude and frequency, starts the test, and observes the shake table and tower. During testing, the structure cannot be edited. A successful tower reaches 10 seconds without a floor-mass ground collision. After reaching 10 seconds or a floor-mass ground collision, show the result and continue simulating the tower physics and shake-table motion until the user clicks Stop Test. Keep the recorded outcome and elapsed survival time fixed while the simulation continues. Keep design controls locked until Stop Test; then restore the saved design and return to design mode. The user may also stop an active test manually or clear the structure to return to design mode.

## Calculations
2D Rigid-Body Physics (Matter.js): The simulation uses 2D rigid-body physics to model tower motion and constraints. Unit conversion must consistently represent positions, forces, acceleration, and time.

Stage 4 Physics: During an active test, the app uses Matter.js constraints and rigid bodies for placed structural members and floor masses. Canvas position in pixels maps consistently to feet, elapsed simulation time maps to seconds, and horizontal acceleration is derived from the shake-table sine-wave motion. The table starts at zero displacement and follows `x(t) = A sin(2πft)` with the amplitude and frequency selected in Stage 3. Earth, Mars, and Moon gravity remain selectable and affect the same rigid bodies. Start/Stop and Clear actions control test state, and structural editing is locked for the full test duration.

Brace and Joint Motion: Brace endpoints are the same structural nodes that terminate the connected beams or columns. During a test, each brace's visible endpoints remain coincident with the live beam/column joint positions as the frame moves. Render the line using the current distance and angle between those joints so its far end does not separate from its joint. A brace is never attached to a floor mass. Stop or reset restores its original endpoints, angle, width, and height.

Gravity: Earth gravity is 32.2 ft/s². Mars gravity is 12.21 ft/s², and Moon gravity is 5.33 ft/s². Selecting a gravity mode applies the corresponding acceleration to the simulation.

Shake Table Displacement: For sine-wave shaking, horizontal table displacement is `x(t) = A sin(2πft)`, where A is amplitude in inches, f is frequency in Hz, t is elapsed time in seconds, and the table starts at zero displacement.

Joint Failure: Estimate joint demand as an instructional proxy: distribute each structural member's Matter.js mass evenly over its 1 ft grid intervals, assigning half of an interval's mass to each endpoint, and add half the mass of each supported floor mass at its beam support nodes. At each constrained node, multiply the resulting tributary mass by the resultant of gravity and horizontal shake-table acceleration. Convert Matter.js mass units using 0.01 kip·s²/ft per mass unit. Joints below 10 kip are normal (green); joints from 10 through 15 kip are elevated (yellow); if demand exceeds 15 kip, mark the joint failed (red), remove its associated Matter.js constraints, and show the resulting collapse. This proxy is for classroom behavior and is not a code-level structural-force calculation.

Tower wins if it survives for 10.0 seconds without any floor mass colliding with the ground plane.

Failure Timing: A floor-mass ground collision records a failure outcome. Joint failure and floor-mass detachment are damage indicators only; continue the full physics simulation through collapse until a floor mass reaches the ground or the 10.0-second survival limit records a pass. After either result, continue simulating until the user clicks Stop Test. Do not record failure when a joint breaks or when a floor mass first detaches.

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
The completed result and simulated structure remain visible until the user clicks Stop Test; completion does not automatically restore the pre-test structure. After either success or failure, keep the full physics simulation and configured sine-wave shaking active until Stop Test. Keep the outcome and elapsed-time readout from changing after the result is recorded.

## Look and Feel
A playful classroom-simulator style and clean, single-page layout.

A responsive simulation canvas supports a desktop maximum of 600 × 500 px. The structural-element toolbar is positioned on the left side of the canvas. Keep the seismic-controls and readout sidebar collapsible in a right-hand column on desktop and tablet widths; only stack it beneath the canvas on narrow mobile screens. Keep sidebar sections in a single vertical column and keep the starter-tower and test controls in the sidebar rather than duplicating them in the page header. Calibration test cases and expected results are documented in `02_validation/calibration_test_cases.md`; do not display free-fall calibration controls, target references, drop simulations, or temporary masses in the app.

The shake table occupies the bottom of the canvas and is aligned exactly with the bottom snap-grid line. There is no separate ground band between the bottom grid line and the table. Structural columns connect directly to the top surface of the shake table, and no structural member or floor mass may extend below the table.

On mobile viewports, the controls stack beneath the canvas. Placement controls remain touch-friendly, and controls must not obscure the canvas during testing.

The interface provides clear active, disabled, hover, and failure states. When a test ends, both the Start test result button and the status panel below the readouts are green for a pass and red for a failure, with readable white text. Do not show a ground-motion trace; the table motion is always the configured sine wave.

## Validation
Free-Fall Calibration Test (external validation only): release a test mass from rest 10 ft above the ground and record the time until it reaches the ground plane. The app does not include a calibration drop control or temporary calibration mass. Compare the measured time with the expected result within ±1%; maintain test cases and expected results in `02_validation/calibration_test_cases.md`. The selected gravity mode determines the expected time:
- Earth at 32.2 ft/s²: 0.78811 seconds
- Mars at 12.21 ft/s²: 1.2798 seconds
- Moon at 5.33 ft/s²: 1.9371 seconds

Record gravity mode, expected time, actual time, tolerance, and pass/fail result for each external free-fall test.

Shake-Table Calibration Test (external validation): measure 10 complete cycles and compare measured period and extreme displacement with the configured frequency and amplitude. Record the test case and expected results in `02_validation/calibration_test_cases.md`. Input and motion measurements must be within ±1%.

Acceptance Checks:
- Placement snaps to the 1 ft grid and prevents elements outside the visible canvas boundary.
- Columns, beams, braces, and floor-mass dimensions accept exactly 1 ft as the minimum size and reject anything smaller.
- Cost updates match the placed element lengths and rates.
- Slider values remain synchronized with their number boxes.
- The 15-kip force-magnitude threshold breaks the associated joint constraint.
- A tower survives 10.0 seconds without a floor-mass ground collision to pass.
- A floor-mass ground collision ends the test as a failure; joint failure and detachment alone do not end it.
- After either a pass or failure result, tower physics and shake-table motion continue until Stop Test, while the recorded outcome and elapsed time remain fixed.
- A floor mass without beam support falls as soon as the test begins.
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
Add the 15-kip joint-force threshold, green/yellow/red stress states, constraint breaking, structural collapse, floor-mass ground collision as the failure trigger, 10-second survival, and explicit win/failure results. Continue full physics and table motion after either result until Stop Test is clicked.

Test: Verify one successful 10-second run, a joint-failure run that continues collapsing until ground contact or 10 seconds, one ground-collision run, post-result table motion until Stop Test, and one manually stopped test.

### Stage 6: Readouts, Persistence, and Polish
Complete live Total Cost, elapsed time, peak table acceleration, local-storage High Score, Clear Structure reset behavior, mobile touch controls, and final visual polish.

Test: Run the full acceptance checklist; verify successful-run-only High Score persistence across refreshes, failed-run behavior, Clear Structure reset, and desktop/mobile usability.
